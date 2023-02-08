from dataclasses import dataclass


@dataclass
class BloomFilterCfg:
    error_rate_p: float
    max_elements: int
    num_bits_m: int
    num_probes_k: int
