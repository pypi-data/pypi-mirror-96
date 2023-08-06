# This file is a part of pyctr.
#
# Copyright (c) 2017-2020 Ian Burgwin
# This file is licensed under The MIT License (MIT).
# You can find the full license text in LICENSE in the root of this project.

"""Module for interacting with Executable Filesystem (ExeFS) files."""

from hashlib import sha256
from os import PathLike
from threading import Lock
from typing import TYPE_CHECKING, NamedTuple

from ..common import PyCTRError, _ReaderOpenFileBase
from ..fileio import SubsectionIO
from ..util import readle
from .base import TypeReaderBase
from .smdh import SMDH, InvalidSMDHError

if TYPE_CHECKING:
    from typing import BinaryIO, Dict, Union

__all__ = ['EXEFS_EMPTY_ENTRY', 'EXEFS_ENTRY_SIZE', 'EXEFS_ENTRY_COUNT', 'EXEFS_HEADER_SIZE', 'ExeFSError',
           'ExeFSFileNotFoundError', 'InvalidExeFSError', 'ExeFSNameError', 'BadOffsetError', 'CodeDecompressionError',
           'decompress_code', 'ExeFSReader']

EXEFS_ENTRY_SIZE = 0x10
EXEFS_ENTRY_COUNT = 10
EXEFS_EMPTY_ENTRY = b'\0' * EXEFS_ENTRY_SIZE
EXEFS_HEADER_SIZE = 0x200

CODE_DECOMPRESSED_NAME = '.code-decompressed'


class ExeFSError(PyCTRError):
    """Generic exception for ExeFS operations."""


class ExeFSFileNotFoundError(ExeFSError):
    """File not found in the ExeFS."""


class InvalidExeFSError(ExeFSError):
    """Invalid ExeFS header."""


class ExeFSNameError(InvalidExeFSError):
    """Name could not be decoded, likely making the file not a valid ExeFS."""

    def __str__(self):
        return f'could not decode from ascii: {self.args[0]!r}'


class BadOffsetError(InvalidExeFSError):
    """Offset is not a multiple of 0x200. This kind of ExeFS will not work on a 3DS."""

    def __str__(self):
        return f'offset is not a multiple of 0x200: {self.args[0]:#x}'


class CodeDecompressionError(ExeFSError):
    """Exception when attempting to decompress ExeFS .code."""


# lazy check
CODE_MAX_SIZE = 0x2300000


def decompress_code(code: bytes) -> bytes:
    # remade from C code, this could probably be done better
    # https://github.com/d0k3/GodMode9/blob/689f6f7cf4280bf15885cbbf848d8dce81def36b/arm9/source/game/codelzss.c#L25-L93
    off_size_comp = int.from_bytes(code[-8:-4], 'little')
    add_size = int.from_bytes(code[-4:], 'little')
    comp_start = 0
    code_len = len(code)

    code_comp_size = off_size_comp & 0xFFFFFF
    code_comp_end = code_comp_size - ((off_size_comp >> 24) % 0xFF)
    code_dec_size = code_len + add_size

    if code_len < 8:
        raise CodeDecompressionError('code_len < 8')
    if code_len > CODE_MAX_SIZE:
        raise CodeDecompressionError('code_len > CODE_MAX_SIZE')

    if code_comp_size <= code_len:
        comp_start = code_len - code_comp_size

    if code_comp_end < 0:
        raise CodeDecompressionError('code_comp_end < 0')
    if code_dec_size > CODE_MAX_SIZE:
        raise CodeDecompressionError('code_dec_size > CODE_MAX_SIZE')

    dec = bytearray(code)
    dec.extend(b'\0' * add_size)

    data_end = comp_start + code_dec_size
    ptr_in = comp_start + code_comp_end
    ptr_out = code_dec_size

    while ptr_in > comp_start and ptr_out > comp_start:
        if ptr_out < ptr_in:
            raise CodeDecompressionError('ptr_out < ptr_in')

        ptr_in -= 1
        ctrl_byte = dec[ptr_in]
        for i in range(7, -1, -1):
            if ptr_in <= comp_start or ptr_out <= comp_start:
                break

            if (ctrl_byte >> i) & 1:
                ptr_in -= 2
                seg_code = int.from_bytes(dec[ptr_in:ptr_in + 2], 'little')
                if ptr_in < comp_start:
                    raise CodeDecompressionError('ptr_in < comp_start')
                seg_off = (seg_code & 0x0FFF) + 2
                seg_len = ((seg_code >> 12) & 0xF) + 3

                if ptr_out - seg_len < comp_start:
                    raise CodeDecompressionError('ptr_out - seg_len < comp_start')
                if ptr_out + seg_off >= data_end:
                    raise CodeDecompressionError('ptr_out + seg_off >= data_end')

                c = 0
                while c < seg_len:
                    byte = dec[ptr_out + seg_off]
                    ptr_out -= 1
                    dec[ptr_out] = byte
                    c += 1
            else:
                if ptr_out == comp_start:
                    raise CodeDecompressionError('ptr_out == comp_start')
                if ptr_in == comp_start:
                    raise CodeDecompressionError('ptr_in == comp_start')

                ptr_out -= 1
                ptr_in -= 1
                dec[ptr_out] = dec[ptr_in]

    if ptr_in != comp_start:
        raise CodeDecompressionError('ptr_in != comp_start')
    if ptr_out != comp_start:
        raise CodeDecompressionError('ptr_out != comp_start')

    return bytes(dec)


class ExeFSEntry(NamedTuple):
    name: str
    """Name of the entry."""
    offset: int
    """Offset of the entry, relative to the end of the header."""
    size: int
    """Size of the entry data."""
    hash: bytes
    """SHA-256 of the entry data."""


def _normalize_path(p: str):
    """Fix a given path to work with ExeFS filenames."""
    if p.startswith('/'):
        p = p[1:]
    # while it is technically possible for an ExeFS entry to contain ".bin",
    #   this would not happen in practice.
    # even so, normalization can be disabled by passing normalize=False to
    #   ExeFSReader.open
    if p.lower().endswith('.bin'):
        p = p[:4]
    return p


class _ExeFSOpenFile(_ReaderOpenFileBase):
    """Class for open ExeFS file entries."""

    def __init__(self, reader: 'ExeFSReader', path: str):
        super().__init__(reader, path)
        self._info = reader.entries[self._path]


class ExeFSReader(TypeReaderBase):
    """
    Reads the contents of the ExeFS, found inside NCCH containers.

    The contents typically include .code, icon, and banner. For titles released before System Menu 5.0.0-11, logo can
    also one of the contents, otherwise logo has a dedicated NCCH section.

    The other notable use of an ExeFS is GodMode9's essentials backup, which can include the files frndseed, hwcal0,
    hwcal1, movable, nand_cid, nand_hdr, otp, and secinfo.

    .code can sometimes be compressed which is indicated in the NCCH Extended Header. When decompressed, a new entry
    called .code-decompressed is added.

    If icon is found, it is loaded into an :class:`~.SMDH` object.

    :param fp: A file path or a file-like object with the CCI data.
    :param closefd: Close the underlying file object when closed. Defaults to `True` for file paths, and `False` for
        file-like objects.
    """

    _code_dec = None

    entries: 'Dict[str, ExeFSEntry]'
    """Entries in the ExeFS."""

    icon: 'SMDH' = None
    """The icon info, if one is in the ExeFS."""

    def __init__(self, fp: 'Union[PathLike, str, bytes, BinaryIO]', *, closefd: bool = True, _load_icon: bool = True):
        super().__init__(fp, closefd=closefd)

        # Threading lock to prevent two operations on one class instance from interfering with eachother.
        self._lock = Lock()

        self.entries = {}

        header = self._file.read(EXEFS_HEADER_SIZE)

        # ExeFS entries can fit up to 10 names. hashes are stored in reverse order
        #   (e.g. the first entry would have the hash at the very end - 0x1E0)
        for entry_n, hash_n in zip(range(0, EXEFS_ENTRY_COUNT * EXEFS_ENTRY_SIZE, EXEFS_ENTRY_SIZE),
                                   range(0x1E0, 0xA0, -0x20)):
            entry_raw = header[entry_n:entry_n + 0x10]
            entry_hash = header[hash_n:hash_n + 0x20]
            if entry_raw == EXEFS_EMPTY_ENTRY:
                continue

            try:
                # ascii is used since only a-z would be used in practice
                name = entry_raw[0:8].rstrip(b'\0').decode('ascii')
            except UnicodeDecodeError:
                raise ExeFSNameError(entry_raw[0:8])

            entry = ExeFSEntry(name=name,
                               offset=readle(entry_raw[8:12]),
                               size=readle(entry_raw[12:16]),
                               hash=entry_hash)

            # the 3DS fails to parse an ExeFS with an offset that isn't a multiple of 0x200
            #   so we should do the same here
            if entry.offset % 0x200:
                raise BadOffsetError(entry.offset)

            self.entries[name] = entry

        # this sometimes needs to be loaded outside, since reading it here may cause encryption problems
        #   when the NCCH has not fully initialized yet and needs to figure out what ExeFS regions need
        #   to be decrypted with the Original NCCH key
        if _load_icon:
            self._load_icon()

    def _load_icon(self):
        try:
            with self.open('icon') as f:
                self.icon = SMDH.load(f)
        except (ExeFSFileNotFoundError, InvalidSMDHError):
            pass

    def __len__(self) -> int:
        """Return the amount of entries in the ExeFS."""
        return len(self.entries)

    def open(self, path: str, *, normalize: bool = True):
        """
        Open an entry in the ExeFS for reading.

        :param path: Name of the entry. Can start with / or end in .bin.
        :param normalize: Remove / and .bin from the path.
        :return: A file-like object that reads from the entry.
        """
        if normalize:
            # remove beginning "/" and ending ".bin"
            path = _normalize_path(path)
        try:
            entry = self.entries[path]
        except KeyError:
            raise ExeFSFileNotFoundError(path)
        if entry.offset == -1:
            # this would be the decompressed .code, if the original .code was compressed
            return _ExeFSOpenFile(self, path)
        else:
            return SubsectionIO(self._file, self._start + EXEFS_HEADER_SIZE + entry.offset, entry.size)

    def get_data(self, info: ExeFSEntry, offset: int, size: int) -> bytes:
        if offset + size > info.size:
            size = info.size - offset
        with self._lock:
            if info.offset == -1:
                # return the decompressed code instead
                return self._code_dec[offset:offset + size]
            else:
                # data for ExeFS entries start relative to the end of the header
                self._file.seek(self._start + EXEFS_HEADER_SIZE + info.offset + offset)
                return self._file.read(size)

    def decompress_code(self) -> bool:
        """
        Decompress '.code' in the container. The result will be available as '.code-decompressed'.

        :return: If '.code' was actually decompressed.
        :rtype: bool
        """
        with self.open('.code') as f:
            code = f.read()

        # if it's already decompressed, this would return the code unmodified
        code_dec = decompress_code(code)

        decompressed = code_dec != code

        if decompressed:
            code_dec_hash = sha256(code_dec)
            entry = ExeFSEntry(name=CODE_DECOMPRESSED_NAME,
                               offset=-1,
                               size=len(code_dec),
                               hash=code_dec_hash.digest())
            self._code_dec = code_dec
        else:
            # if the code was already decompressed, don't store a second copy in memory
            code_entry = self.entries['.code']
            entry = ExeFSEntry(name=CODE_DECOMPRESSED_NAME,
                               offset=code_entry.offset,
                               size=code_entry.size,
                               hash=code_entry.hash)

        self.entries[CODE_DECOMPRESSED_NAME] = entry

        # returns if the code was actually decompressed or not
        return decompressed
