from bloomfilter3 import BloomFilter

import os
import pytest
import tempfile


def test_membership():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom1.bin')

        bf = BloomFilter(path, error_rate=0.01)

        assert not ('foo' in bf)

        bf.add('foo')
        assert 'foo' in bf

def test_bitwise_and():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')
        path2 = os.path.join(tmp, 'bloom2.bin')

        bf1 = BloomFilter(path1, error_rate=0.01)
        bf2 = BloomFilter(path2, error_rate=0.01)

        bf1.add('foo')
        bf2.add('foo')

        bf1 &= bf2

        assert 'foo' in bf1

def test_or():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')
        path2 = os.path.join(tmp, 'bloom2.bin')

        bf1 = BloomFilter(path1, error_rate=0.01)
        bf2 = BloomFilter(path2, error_rate=0.01)

        bf1.add('foo')
        bf2.add('bar')

        bf1 |= bf2

        assert 'foo' in bf1
        assert 'bar' in bf1

def test_close():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom1.bin')

        bf = BloomFilter(path, error_rate=0.01)

        bf.close()

def test_context():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom1.bin')

        with BloomFilter(path, error_rate=0.01) as bf:
            bf.add('foo')
            assert 'foo' in bf

def test_delete():

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bloom1.bin')

        bf = BloomFilter(path, error_rate=0.01)

        bf.add('foo')
        assert 'foo' in bf

        bf.__del__()

def test_template_matching():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')
        path2 = os.path.join(tmp, 'bloom2.bin')

        bf = BloomFilter(path1, error_rate=0.01)
        bf2 = BloomFilter(path2, error_rate=0.01)

        bf.add('foo')
        bf2.add('bar')

        compare_result = bf._match_template(bf2)

        assert compare_result

def test_repr():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')

        bf = BloomFilter(path1, error_rate=0.01)

        assert repr(bf)

def test_clear():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')

        bf = BloomFilter(path1, error_rate=0.01)
        bf.backend.clear(1)

def test_validations():

    with tempfile.TemporaryDirectory() as tmp:
        path1 = os.path.join(tmp, 'bloom1.bin')

        with pytest.raises(ValueError):
            bf = BloomFilter(
                path1,
                max_elements=-10,
                error_rate=0.01
            )

        with pytest.raises(ValueError):
            bf = BloomFilter(
                path1,
                error_rate=0
            )

        with pytest.raises(ValueError):
            bf = BloomFilter(
                path1,
                error_rate=2
            )

        with pytest.raises(ValueError):
            bf = BloomFilter(
                path1,
                error_rate=-10
            )

        path_large = os.path.join(tmp, 'bloom_large.bin')
        path_small = os.path.join(tmp, 'bloom_small.bin')

        bf_large = BloomFilter(path_large, max_elements=100_000, error_rate=0.01)
        bf_small = BloomFilter(path_small, max_elements=100, error_rate=0.01)

        with pytest.raises(ValueError):
            bf_large |= bf_small

        with pytest.raises(ValueError):
            bf_large &= bf_small
