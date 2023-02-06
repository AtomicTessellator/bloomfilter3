from bloomfilter3.backends import Mmap_backend
from bloomfilter3 import BloomFilter

import math
import mmap
import os
import tempfile


def test_membership():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom_persist.bin')

        bf = BloomFilter(
            path,
            max_elements=12_768,
            error_rate=0.04
        )

        header_bytes = Mmap_backend.pack_header(bf)

        # The header must be a multiple of mmap.ALLOCATIONGRANULARITY
        remaining_bytes = len(header_bytes) // mmap.ALLOCATIONGRANULARITY
        assert remaining_bytes == 0

        format_, error_rate_p, ideal_num_elements_n, num_bits_m, num_probes_k = Mmap_backend.unpack_header(header_bytes)

        assert format_ == 1
        assert math.isclose(error_rate_p, 0.04, rel_tol=1e-6)
        assert ideal_num_elements_n == 12_768
        assert num_bits_m == 85542
        assert num_probes_k == 5
