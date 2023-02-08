from bloomfilter3.backends import Mmap_backend
from bloomfilter3 import BloomFilter

import math
import mmap
import os
import string
import random
import tempfile


def _random_string(length: int) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def test_membership():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom_persist.bin')

        bf = BloomFilter(
            path,
            max_elements=12_768,
            error_rate=0.04
        )

        header_bytes = Mmap_backend.pack_header(bf.bf_cfg)

        # The header must be a multiple of mmap.ALLOCATIONGRANULARITY
        remaining_bytes = len(header_bytes) // mmap.ALLOCATIONGRANULARITY
        assert remaining_bytes == 0

        format_, bf_cfg = Mmap_backend.unpack_header(header_bytes)

        assert format_ == 1
        assert math.isclose(bf_cfg.error_rate_p, 0.04, rel_tol=1e-6)
        assert bf_cfg.max_elements == 12_768
        assert bf_cfg.num_bits_m == 85542
        assert bf_cfg.num_probes_k == 5


def test_performance():

    members = set()

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom_persist.bin')

        bf = BloomFilter(
            path,
            max_elements=12_768,
            error_rate=0.04
        )

        # Add 10,000 members to the test
        for i in range(10000):
            rnd = _random_string(100)
            members.add(rnd)
            bf.add(rnd)

        # Make sure they are all in there
        for test_str in members:
            assert test_str in bf

        # Load it again into another object
        bf2 = BloomFilter(path)

        assert math.isclose(bf2.bf_cfg.error_rate_p, bf.bf_cfg.error_rate_p, rel_tol=1e-6)
        assert bf2.bf_cfg.max_elements == bf.bf_cfg.max_elements
        assert bf2.bf_cfg.num_bits_m == bf.bf_cfg.num_bits_m
        assert bf2.bf_cfg.num_probes_k == bf.bf_cfg.num_probes_k
