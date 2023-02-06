import math
import sys
from pathlib import Path

from bloomfilter3.backends import Mmap_backend
from bloomfilter3.hash.hashing import get_filter_bitno_probes

try:
    import mmap  # noqa
except ImportError:
    print(f"mmap is not supported on this platform : {sys.platform}")
    sys.exit(1)


class BloomFilter:
    """Probabilistic set membership testing for large sets

    This is a probabilistic data structure. It is not guaranteed to be
    accurate, but it is very fast and very space efficient.

    The error rate is configurable, but it is not guaranteed to be accurate.

    The number of elements is configurable, but it is not guaranteed to be
    accurate.

    The number of bits is configurable, but it is not guaranteed to be
    accurate.

    Args:
        filename: The filename that will be used to store the filter.

        max_elements: The maximum number of elements you expect to add to the
            filter. This is not a hard limit, approxi

        error_rate: The maximum error rate you are willing to accept between
            0 and 1, exclusive

    >>> bf = BloomFilter(1000, 0.1)
    >>> 'foo' in bf
    False
    >>> bf.add('foo')
    >>> 'foo' in bf
    True

    """

    def __init__(self, filename, max_elements: int = 10000, error_rate: float = 0.1):
        if max_elements <= 0:
            raise ValueError("ideal_num_elements_n must be > 0")

        if not (0 < error_rate < 1):
            raise ValueError("error_rate_p must be between 0 and 1 exclusive")

        file = Path(filename)
        if file.exists():
            self.load(filename)
        else:
            self.error_rate_p = error_rate
            self.ideal_num_elements_n = max_elements
            numerator = -1 * self.ideal_num_elements_n * math.log(self.error_rate_p)
            denominator = math.log(2) ** 2
            real_num_bits_m = numerator / denominator
            self.num_bits_m = int(math.ceil(real_num_bits_m))
            real_num_probes_k = (
                self.num_bits_m / self.ideal_num_elements_n
            ) * math.log(2)
            self.num_probes_k = int(math.ceil(real_num_probes_k))
            self.probe_bitnoer = get_filter_bitno_probes
            self.backend = Mmap_backend(self, filename)

    @staticmethod
    def load(filename):
        """Load a bloom filter from a file"""
        # backend = Mmap_backend.load(filename)
        pass

    def __repr__(self):
        return (
            "BloomFilter(ideal_num_elements_n=%d, error_rate_p=%f, " + "num_bits_m=%d)"
        ) % (
            self.ideal_num_elements_n,
            self.error_rate_p,
            self.num_bits_m,
        )

    def add(self, key):
        """Add an element to the filter"""
        for bitno in self.probe_bitnoer(self, key):
            self.backend.set(bitno)

    def __iadd__(self, key):
        self.add(key)
        return self

    def _match_template(self, bloom_filter):
        """
        Compare a sort of signature for two bloom filters.

        Used in preparation for binary operations
        """
        return (
            self.num_bits_m == bloom_filter.num_bits_m
            and self.num_probes_k == bloom_filter.num_probes_k
            and self.probe_bitnoer == bloom_filter.probe_bitnoer
        )

    def union(self, bloom_filter):
        """Compute the set union of two bloom filters"""
        self.backend |= bloom_filter.backend

    def __ior__(self, bloom_filter):
        self.union(bloom_filter)
        return self

    def intersection(self, bloom_filter):
        """Compute the set intersection of two bloom filters"""
        self.backend &= bloom_filter.backend

    def __iand__(self, bloom_filter):
        self.intersection(bloom_filter)
        return self

    def __contains__(self, key):
        for bitno in self.probe_bitnoer(self, key):
            if not self.backend.is_set(bitno):
                return False
        return True

    def close(self):
        self.backend.close()
        self.backend = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.backend = None

    def __del__(self):
        if hasattr(self, 'backend') and self.backend is not None:
            self.backend.close()
            self.backend = None
