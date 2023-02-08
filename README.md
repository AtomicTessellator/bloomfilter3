# bloomfilter3

Python bloom-filter library with a focus on ease of use and high performance.

## Motivation

This library was heavily inspired from the excellent [bloom-filter2](https://github.com/remram44/python-bloom-filter/tree/904cea7522a18a7bbef66d3c6b2ee23738171e5a) library, however I decided to make some changes that enhanced functionality and ease of use.

Unfortunatly these changes makes the library non-backwards compatible, hence bloomfilter3 was born.

Credits and links can be found in AUTHORS.md.

## Changes from bloom-filter2:
  - mmap only and by default
  - bloom filter parameters are stored WITH the bloom filter itself on disk, no need to keep track of parameters (max_elements, error_rate) seperatly
  - Simpler persistence

## Using
```python
from bloom_filter3 import BloomFilter

# instantiate BloomFilter with custom settings,
# max_elements is how many elements you expect the filter to hold.
# error_rate defines accuracy; You can use defaults with
# `BloomFilter()` without any arguments. Following example
# is same as defaults:

bloom = BloomFilter(
  max_elements=10_000,
  error_rate=0.1
)

# Test whether the bloom-filter has seen a key:
assert "test-key" not in bloom

# Mark the key as seen
bloom.add("test-key")

# Now check again
assert "test-key" in bloom
```

## Contributing

  - Please review CODE_OF_CONDUCT.md
  - Please make sure you do `make tests` and `make lint` before submitting a PR
  - Please make sure you add tests for any new functionality
