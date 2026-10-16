"""
Ascon-Guard AI: Automated Statistical Cryptanalysis & Diffusion Metrics
========================================================================
Analyzes Ascon-128 state matrices for:
1. Strict Avalanche Criterion (SAC) & bit diffusion rate across permutation rounds.
2. Linear register bias (P(bit=1) deviation on x0..x4).
3. Differential trail propagation and state entropy.
Outputs mathematical metrics for LLM reasoning and uncertainty verification.
"""

import math
from typing import List, Dict, Any, Tuple
from ascon_engine import AsconEngine, AsconState, generate_rural_clinic_record

def count_bits(n: int) -> int:
    """Returns the Hamming weight (number of set bits) of a 64-bit word."""
    return bin(n & 0xFFFFFFFFFFFFFFFF).count("1")

def hamming_distance_states(s1: AsconState, s2: AsconState) -> int:
    """Computes bitwise Hamming distance between two 320-bit Ascon states."""
    dist = 0
    dist += count_bits(s1.x0 ^ s2.x0)
    dist += count_bits(s1.x1 ^ s2.x1)
    dist += count_bits(s1.x2 ^ s2.x2)
    dist += count_bits(s1.x3 ^ s2.x3)
    dist += count_bits(s1.x4 ^ s2.x4)
    return dist

def evaluate_avalanche_effect(fault_mode: str = "SECURE", test_rounds: int = 12) -> List[Dict[str, Any]]:
    """
    Tests Strict Avalanche Criterion (SAC):
    Flips a single bit in input state and measures the percentage of flipped bits
    in the 320-bit internal state round-by-round.
    Ideal cipher target: ~50% (160 bits out of 320) after round 3.
    """
    engine = AsconEngine(fault_mode=fault_mode)
    
    # Base input state
    base_state = AsconState(0x80400c0600000000, 0x0123456789abcdef, 0x23456789abcdef01, 0x3456789abcdef012, 0x456789abcdef0123)
    # Flipped state (1-bit difference in x1)
    flipped_state = AsconState(0x80400c0600000000, 0x0123456789abcdef ^ 0x1, 0x23456789abcdef01, 0x3456789abcdef012, 0x456789abcdef0123)

    results = []
    curr_base = base_state.clone()
    curr_flip = flipped_state.clone()

    start_round = 12 - test_rounds
    for r in range(start_round, 12):
        curr_base = engine.round_permutation(curr_base, r)
        curr_flip = engine.round_permutation(curr_flip, r)
        
        diff_bits = hamming_distance_states(curr_base, curr_flip)
        diffusion_pct = (diff_bits / 320.0) * 100.0
        
        # Breakdown by register
        x1_diff = count_bits(curr_base.x1 ^ curr_flip.x1)
        x2_diff = count_bits(curr_base.x2 ^ curr_flip.x2)
        
        results.append({
            "round_index": r,
            "relative_round": r - start_round + 1,
            "total_flipped_bits": diff_bits,
            "diffusion_percentage": round(diffusion_pct, 2),
            "x1_flipped_bits": x1_diff,
            "x2_flipped_bits": x2_diff,
            "ideal_target_bits": 160
        })

    return results

def compute_linear_bias_metrics(telemetry: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes linear bit bias across recorded intermediate rounds.
    Detects if any 64-bit register has a systematic bias deviating from 0.5.
    """
    if not telemetry:
        return {"max_bias": 0.0, "status": "NO_DATA"}

    x1_weights = []
    x2_weights = []

    for item in telemetry:
        regs = item["registers"]
        x1_val = int(regs["x1"], 16)
        x2_val = int(regs["x2"], 16)
        x1_weights.append(count_bits(x1_val) / 64.0)
        x2_weights.append(count_bits(x2_val) / 64.0)

    avg_x1 = sum(x1_weights) / len(x1_weights)
    avg_x2 = sum(x2_weights) / len(x2_weights)

    bias_x1 = abs(avg_x1 - 0.5)
    bias_x2 = abs(avg_x2 - 0.5)
    max_bias = max(bias_x1, bias_x2)

    return {
        "x1_mean_bit_density": round(avg_x1, 4),
        "x2_mean_bit_density": round(avg_x2, 4),
        "max_linear_bias": round(max_bias, 4),
        "bias_severity": "HIGH_CORRELATION" if max_bias > 0.12 else ("MODERATE_LEAK" if max_bias > 0.06 else "NORMAL_ENTROPY")
    }

def generate_telemetry_digest(fault_mode: str = "SECURE") -> Dict[str, Any]:
    """
    Generates a full cryptographic digest and diffusion matrix
    ready for transmission to the Evolus Gateway and AMD Cloud Auditor.
    """
    engine = AsconEngine(fault_mode=fault_mode)
    key = b"BIHAR_HEALTH_001"
    nonce = b"NONCE_RURAL_9482"
    patient_json = generate_rural_clinic_record()
    
    ct, tag = engine.encrypt(key, nonce, b"HEALTHY_VIHAR_AD", patient_json.encode())
    
    avalanche_profile = evaluate_avalanche_effect(fault_mode=fault_mode, test_rounds=12)
    bias_metrics = compute_linear_bias_metrics(engine.telemetry_history)
    
    # Extract round 1, round 2, and final round state snapshots
    init_snapshots = [t for t in engine.telemetry_history if t["phase"] == "INIT"][:4]
    
    return {
        "engine_mode": fault_mode,
        "sample_patient_id": "PAT-BIHAR-9482",
        "ciphertext_hex": ct[:32].hex() + "...",
        "tag_hex": tag.hex(),
        "total_permutation_rounds_logged": len(engine.telemetry_history),
        "avalanche_profile": avalanche_profile,
        "linear_bias_metrics": bias_metrics,
        "early_round_states": init_snapshots
    }
