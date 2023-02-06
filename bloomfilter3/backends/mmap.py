import mmap
import os
import struct


class Mmap_backend:
    """
    Backend storage for our "array of bits" using an mmap'd file.
    Please note that this has only been tested on Linux so far.
    """

    effs = 2**8 - 1

    def __init__(self, filter, filename) -> None:
        self.filter = filter
        self.num_chars = (self.filter.num_bits_m + 7) // 8

        flags = os.O_RDWR | os.O_CREAT

        offset_bytes = Mmap_backend.header_end_offset_bytes(filter)

        self.file_ = os.open(filename, flags)
        os.lseek(self.file_, offset_bytes + self.num_chars + 1, os.SEEK_SET)
        os.write(self.file_, b"\x00")

        self.mmap = mmap.mmap(self.file_, self.num_chars, offset=offset_bytes)

        # Write the header
        self.mmap.seek(0)
        self.mmap.write(Mmap_backend.pack_header(filter))

    @staticmethod
    def pack_header(filter) -> bytearray:
        """Return the header"""
        header = bytearray()

        # Format : unsigned int, currently hardcoded to "1"
        header += struct.pack("I", 1)

        # Error Rate : float
        header += struct.pack("f", filter.error_rate_p)

        # Ideal Num Elements : long long
        header += struct.pack("q", filter.ideal_num_elements_n)

        # Num bits : long long
        header += struct.pack("q", filter.num_bits_m)

        # Num Probes : unsigned int
        header += struct.pack("I", filter.num_probes_k)

        return header

    @staticmethod
    def header_size_bytes(filter) -> int:
        """Return the size of the header in bytes"""
        return Mmap_backend.pack_header(filter).__len__()

    @staticmethod
    def header_end_offset_bytes(filter) -> int:
        """
        Return the end offset of the header in bytes, this must be a
        multiple of mmap.ALLOCATIONGRANULARITY, because mmap can only
        seek in offsets of mmap.ALLOCATIONGRANULARITY
        """
        header_size = Mmap_backend.header_size_bytes(filter)
        return (
            int(header_size / mmap.ALLOCATIONGRANULARITY) * mmap.ALLOCATIONGRANULARITY
        )

    @staticmethod
    def unpack_header(header) -> tuple:
        """Unpack the header"""
        # Format : unsigned int, currently hardcoded to "1"
        (format_,) = struct.unpack("I", header[0:4])

        # Error Rate : float
        (error_rate_p,) = struct.unpack("f", header[4:8])

        # Ideal Num Elements : long long
        (ideal_num_elements_n,) = struct.unpack("q", header[8:16])

        # Num bits : long long
        (num_bits_m,) = struct.unpack("q", header[16:24])

        # Num Probes : unsigned int
        (num_probes_k,) = struct.unpack("I", header[24:28])

        return (
            format_,
            error_rate_p,
            ideal_num_elements_n,
            num_bits_m,
            num_probes_k,
        )

    def is_set(self, bitno) -> int:
        """
        Return 1 if bit number bitno is set, 0 otherwise

        Args:
            bitno (int): bit number

        Returns:
            int: 1 if bit number bitno is set, 0 otherwise
        """
        byteno, bit_within_wordno = divmod(bitno, 8)
        mask = 1 << bit_within_wordno
        byte = self.mmap[byteno]

        return byte & mask

    def set(self, bitno):
        """set bit number bitno to true"""
        byteno, bit_within_byteno = divmod(bitno, 8)
        mask = 1 << bit_within_byteno
        byte = self.mmap[byteno]
        byte |= mask
        self.mmap[byteno] = byte

    def clear(self, bitno) -> None:
        """clear bit number bitno - set it to false"""
        byteno, bit_within_byteno = divmod(bitno, 8)
        mask = 1 << bit_within_byteno
        byte = self.mmap[byteno]
        byte &= Mmap_backend.effs - mask
        self.mmap[byteno] = byte

    def __iand__(self, other):
        if self.filter.num_bits_m != other.filter.num_bits_m:
            raise ValueError("Bitmasks must be of equal size")

        for byteno in range(self.num_chars):
            self.mmap[byteno] = self.mmap[byteno] & other.mmap[byteno]

        return self

    def __ior__(self, other):
        if self.filter.num_bits_m != other.filter.num_bits_m:
            raise ValueError("Bitmasks must be of equal size")

        for byteno in range(self.num_chars):
            self.mmap[byteno] = self.mmap[byteno] | other.mmap[byteno]

        return self

    def close(self):
        """Close the file"""
        os.close(self.file_)
