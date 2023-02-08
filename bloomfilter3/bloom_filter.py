import math
import sys
from pathlib import Path

from bloomfilter3.backends import Mmap_backend
from bloomfilter3.cfg import BloomFilterCfg
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

        self.probe_bitnoer = get_filter_bitno_probes

        file = Path(filename)

        if file.exists():
            self.backend = Mmap_backend.load(filename)
            self.bf_cfg = self.backend.bf_cfg
        else:
            self.bf_cfg = self.compute_config(max_elements, error_rate)
            self.backend = Mmap_backend(self.bf_cfg, filename)

    def compute_config(self, max_elements: int, error_rate) -> BloomFilterCfg:
        numerator = -1 * max_elements * math.log(error_rate)
        denominator = math.log(2) ** 2
        num_bits_m = int(math.ceil(numerator / denominator))

        # Compute num_probes_k
        real_num_probes_k = (num_bits_m / max_elements) * math.log(2)
        num_probes_k = int(math.ceil(real_num_probes_k))

        bf_cfg = BloomFilterCfg(
            error_rate_p=error_rate,
            max_elements=max_elements,
            num_bits_m=num_bits_m,
            num_probes_k=num_probes_k,
        )

        return bf_cfg

    def __repr__(self):
        return ("BloomFilter(max_elements=%d, error_rate_p=%f, " + "num_bits_m=%d)") % (
            self.bf_cfg.max_elements,
            self.bf_cfg.error_rate_p,
            self.bf_cfg.num_bits_m,
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
            self.bf_cfg.num_bits_m == bloom_filter.bf_cfg.num_bits_m
            and self.bf_cfg.num_probes_k == bloom_filter.bf_cfg.num_probes_k
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
        if hasattr(self, "backend") and self.backend is not None:
            self.backend.close()
            self.backend = None
