MERSENNES1 = [2**x - 1 for x in [17, 31, 127]]
MERSENNES2 = [2**x - 1 for x in [19, 67, 257]]


def simple_hash(int_list, prime1, prime2, prime3) -> int:
    """Compute a hash value from a list of integers and 3 primes"""
    result = 0
    for integer in int_list:
        result += ((result + integer + prime1) * prime2) % prime3
    return result


def hash1(int_list) -> int:
    """Basic hash function #1"""
    return simple_hash(int_list, MERSENNES1[0], MERSENNES1[1], MERSENNES1[2])


def hash2(int_list) -> int:
    """Basic hash function #2"""
    return simple_hash(int_list, MERSENNES2[0], MERSENNES2[1], MERSENNES2[2])


def get_filter_bitno_probes(bloom_filter, key) -> int:
    """
    Apply num_probes_k hash functions to key.

    Generate the array index and bitmask corresponding to each result
    """

    # This one assumes key is either bytes or str (or other list of integers)

    if hasattr(key, "__divmod__"):
        int_list = []
        temp = key
        while temp:
            quotient, remainder = divmod(temp, 256)
            int_list.append(remainder)
            temp = quotient
    elif isinstance(key, (list, tuple, str, bytes)) and not key:
        int_list = []
    elif hasattr(key[0], "__divmod__"):
        int_list = key
    elif isinstance(key[0], str):
        int_list = [ord(char) for char in key]
    else:
        raise TypeError("Sorry, I do not know how to hash this type")

    hash_value1 = hash1(int_list)
    hash_value2 = hash2(int_list)
    probe_value = hash_value1

    for probeno in range(1, bloom_filter.bf_cfg.num_probes_k + 1):
        probe_value *= hash_value1
        probe_value += hash_value2
        probe_value %= MERSENNES1[2]
        yield probe_value % bloom_filter.bf_cfg.num_bits_m
