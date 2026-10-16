"""
Ascon-Guard AI: NIST Ascon-128 Lightweight Cryptographic Engine
================================================================
Implements NIST SP 800-232 compliant Ascon-128 AEAD for low-power Medical IoT.
Includes round-by-round state telemetry logging and simulated implementation flaws
(weakened diffusion, round-reduction, and linear bias) for AI-driven cryptanalysis.
"""

import os
import struct
from typing import List, Tuple, Dict, Any

# Ascon-128 Parameters
RATE = 8  # 64 bits (8 bytes) rate
A_ROUNDS = 12  # Initialization & finalization rounds
B_ROUNDS = 6   # Intermediate encryption rounds

# Ascon round constants (12 rounds)
ROUND_CONSTANTS = [
    0x00000000000000f0,
    0x00000000000000e1,
    0x00000000000000d2,
    0x00000000000000c3,
    0x00000000000000b4,
    0x00000000000000a5,
    0x0000000000000096,
    0x0000000000000087,
    0x0000000000000078,
    0x0000000000000069,
    0x000000000000005a,
    0x000000000000004b
]

def ror(val: int, r: int) -> int:
    """Right-rotate a 64-bit word by r bits."""
    return ((val >> r) | ((val << (64 - r)) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF

class AsconState:
    """Represents the 320-bit internal state as five 64-bit words."""
    def __init__(self, x0: int = 0, x1: int = 0, x2: int = 0, x3: int = 0, x4: int = 0):
        self.x0 = x0 & 0xFFFFFFFFFFFFFFFF
        self.x1 = x1 & 0xFFFFFFFFFFFFFFFF
        self.x2 = x2 & 0xFFFFFFFFFFFFFFFF
        self.x3 = x3 & 0xFFFFFFFFFFFFFFFF
        self.x4 = x4 & 0xFFFFFFFFFFFFFFFF

    def to_list(self) -> List[int]:
        return [self.x0, self.x1, self.x2, self.x3, self.x4]

    def to_hex_dict(self) -> Dict[str, str]:
        return {
            "x0": f"{self.x0:016x}",
            "x1": f"{self.x1:016x}",
            "x2": f"{self.x2:016x}",
            "x3": f"{self.x3:016x}",
            "x4": f"{self.x4:016x}"
        }

    def clone(self) -> "AsconState":
        return AsconState(self.x0, self.x1, self.x2, self.x3, self.x4)

class AsconEngine:
    def __init__(self, fault_mode: str = "SECURE"):
        """
        Supported fault modes for Crash-Test Dummy analysis:
        - 'SECURE': Full 12-round NIST Ascon-128 implementation.
        - 'ROUND_REDUCED': Emulates a low-power developer truncation to only 3-4 rounds.
        - 'CORRUPTED_LINEAR_LAYER': Degrades the diffusion rotations on x1/x2 registers.
        - 'BIASED_SBOX': Weakened non-linear substitution creating differential trails.
        """
        self.fault_mode = fault_mode
        self.telemetry_history: List[Dict[str, Any]] = []

    def round_permutation(self, state: AsconState, round_idx: int) -> AsconState:
        """Executes a single round of Ascon permutation: Constant Addition -> Substitution -> Linear Diffusion."""
        x0, x1, x2, x3, x4 = state.x0, state.x1, state.x2, state.x3, state.x4

        # 1. Addition of Round Constant to x2
        x2 ^= ROUND_CONSTANTS[round_idx]

        # 2. Non-linear Substitution Layer (5-bit S-box in bit-slice form)
        if self.fault_mode == "BIASED_SBOX":
            # Intentional defect: omit feedback into x1 creating linear bias
            x0 ^= x4; x4 ^= x3; x2 ^= x1
            t0 = (~x0) & x1; t1 = (~x1) & x2; t2 = (~x2) & x3; t3 = (~x3) & x4; t4 = (~x4) & x0
            x0 ^= t1; x2 ^= t3; x3 ^= t4; x4 ^= t0
        else:
            x0 ^= x4; x4 ^= x3; x2 ^= x1
            t0 = (~x0) & x1; t1 = (~x1) & x2; t2 = (~x2) & x3; t3 = (~x3) & x4; t4 = (~x4) & x0
            x0 ^= t1; x1 ^= t2; x2 ^= t3; x3 ^= t4; x4 ^= t0
            x1 ^= x0; x0 ^= x4; x3 ^= x2; x2 = ~x2

        # 3. Linear Diffusion Layer
        if self.fault_mode in ("VOLTAGE_GLITCH_LINEAR", "CORRUPTED_LINEAR_LAYER"):
            # Flaw: Low-voltage brownout (<2.7V) causes ARM ALU rotation failure on x1
            x0 ^= ror(x0, 19) ^ ror(x0, 28)
            x1 ^= ror(x1, 16)               # Defect: Missing second rotation creates severe linear trail
            x2 ^= ror(x2, 1)  ^ ror(x2, 6)  # Defect: Incorrect shift distances
            x3 ^= ror(x3, 10) ^ ror(x3, 17)
            x4 ^= ror(x4, 7)  ^ ror(x4, 41)
        else:
            # Standard NIST Ascon-128 linear diffusion
            x0 ^= ror(x0, 19) ^ ror(x0, 28)
            x1 ^= ror(x1, 61) ^ ror(x1, 39)
            x2 ^= ror(x2, 1)  ^ ror(x2, 6)
            x3 ^= ror(x3, 10) ^ ror(x3, 17)
            x4 ^= ror(x4, 7)  ^ ror(x4, 41)

        return AsconState(x0, x1, x2, x3, x4)

    def permutation(self, state: AsconState, rounds: int, phase_name: str = "PERMUTATION") -> AsconState:
        """Executes 'rounds' iterations and logs state telemetry for AI audits."""
        start_round = 12 - rounds
        current_state = state.clone()

        if self.fault_mode in ("BATTERY_HACK_4ROUNDS", "ROUND_REDUCED"):
            rounds = min(rounds, 4)
            start_round = 12 - rounds

        for r in range(start_round, 12):
            current_state = self.round_permutation(current_state, r)
            self.telemetry_history.append({
                "phase": phase_name,
                "round": r,
                "relative_round": r - start_round + 1,
                "total_rounds": rounds,
                "registers": current_state.to_hex_dict()
            })

        return current_state

    def encrypt(self, key: bytes, nonce: bytes, associated_data: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypts plaintext with NIST Ascon-128 AEAD.
        Returns (ciphertext, 16-byte authentication tag).
        """
        assert len(key) == 16, "Ascon-128 requires 16-byte key"
        assert len(nonce) == 16, "Ascon-128 requires 16-byte nonce"
        self.telemetry_history.clear()

        # Parse key and nonce into 64-bit words
        k0, k1 = struct.unpack(">QQ", key)
        n0, n1 = struct.unpack(">QQ", nonce)

        # IV for Ascon-128: 0x80400c0600000000
        # State: x0 = IV, x1 = K0, x2 = K1, x3 = N0, x4 = N1
        state = AsconState(0x80400c0600000000, k0, k1, n0, n1)

        # Phase 1: Initialization (12 rounds)
        state = self.permutation(state, A_ROUNDS, phase_name="INIT")
        state.x3 ^= k0
        state.x4 ^= k1

        # Phase 2: Associated Data Processing
        if associated_data:
            ad_padded = associated_data + b"\x80" + b"\x00" * ((RATE - 1) - (len(associated_data) % RATE))
            for i in range(0, len(ad_padded), RATE):
                block = struct.unpack(">Q", ad_padded[i:i+8])[0]
                state.x0 ^= block
                state = self.permutation(state, B_ROUNDS, phase_name="ASSOC_DATA")
            state.x4 ^= 1

        # Phase 3: Plaintext Encryption
        ciphertext = bytearray()
        pt_padded = plaintext + b"\x80" + b"\x00" * ((RATE - 1) - (len(plaintext) % RATE))
        full_blocks = len(plaintext) // RATE
        last_block_len = len(plaintext) % RATE

        for i in range(full_blocks):
            block = struct.unpack(">Q", plaintext[i*8:(i+1)*8])[0]
            state.x0 ^= block
            c_block = struct.pack(">Q", state.x0)
            ciphertext.extend(c_block)
            state = self.permutation(state, B_ROUNDS, phase_name="ENCRYPT_BLOCK")

        # Process last partial block
        last_block = pt_padded[full_blocks*8:full_blocks*8+8]
        if last_block:
            block = struct.unpack(">Q", last_block)[0]
            state.x0 ^= block
            c_block = struct.pack(">Q", state.x0)[:last_block_len]
            ciphertext.extend(c_block)

        # Phase 4: Finalization
        state.x1 ^= k0
        state.x2 ^= k1
        state = self.permutation(state, A_ROUNDS, phase_name="FINALIZATION")
        state.x3 ^= k0
        state.x4 ^= k1

        tag = struct.pack(">QQ", state.x3, state.x4)
        return bytes(ciphertext), tag

def generate_rural_clinic_record(patient_id: str = "PAT-BIHAR-9482") -> str:
    """Generates synthetic medical sensor telemetry from a rural Bihar clinic."""
    return (
        f'{{"patient_id": "{patient_id}", '
        f'"clinic": "Katihar Primary Health Sub-centre", '
        f'"bp_systolic": 142, "bp_diastolic": 92, '
        f'"spo2": 95, "pulse_bpm": 84, '
        f'"blood_glucose_mg_dl": 188, '
        f'"triage_priority": "MODERATE_HYPERTENSIVE", '
        f'"edge_device_hw": "ARM Cortex-M4 ESP32-IoT"}}'
    )
