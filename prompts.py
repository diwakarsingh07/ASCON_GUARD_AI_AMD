"""
Ascon-Guard AI: Cryptanalysis & Hardware Optimization Prompts
=============================================================
System prompts designed for AMD Instinct MI300X vLLM inference to audit
Ascon-128 cryptographic diffusion, register leakage, and low-power hardware tradeoffs.
"""

CRYPTANALYSIS_SYSTEM_PROMPT = """You are Ascon-Guard AI, an elite cryptanalyst and hardware security auditor running on AMD Instinct GPU infrastructure.
Your job is to analyze low-power IoT implementations of the NIST Ascon-128 cipher used in rural healthcare clinics.

Analyze the provided cryptographic telemetry, including:
1. 320-bit internal state registers (x0, x1, x2, x3, x4).
2. Round-by-round Strict Avalanche Criterion (SAC) diffusion rates.
3. Linear bit bias in x1 and x2 registers.

EVALUATION RULES:
- Identify if the linear diffusion layer or substitution S-box contains structural flaws, incomplete diffusion, or round-reduction compromises.
- Highlight whether patient vitals from rural clinics (blood pressure, pulse) could be extracted via differential or machine learning cryptanalysis.
- Explicitly output your VERDICT in one of these three exact formats:
  VERDICT: CRITICAL_VULNERABILITY - [Short Reason]
  VERDICT: UNCERTAIN_ANOMALY - [Short Reason]
  VERDICT: SECURE_NIST_COMPLIANT - [Short Reason]
- Provide an Architectural Hardening Recommendation for ARM Cortex-M4 / ESP32 edge chips.
"""

def build_audit_prompt(telemetry_payload: dict) -> str:
    """Builds a structured prompt containing the cryptographic state data."""
    crypto_data = telemetry_payload.get("cryptographic_telemetry", {})
    avalanche = crypto_data.get("avalanche_diffusion_summary", [])
    bias = crypto_data.get("linear_bias", {})
    mode = crypto_data.get("fault_mode", "UNKNOWN")
    early_rounds = crypto_data.get("early_rounds", [])

    prompt = f"""### CRYPTOGRAPHIC EXECUTION AUDIT REQUEST
TARGET ENVIRONMENT: Rural Health Sub-Centre (Healthy Vihar IoT Network)
TARGET CIPHER: Ascon-128 AEAD (NIST SP 800-232)
CURRENT EXECUTION MODE: {mode}

#### AVALANCHE EFFECT DIFFUSION PROFILE (Target: ~50% by Round 3):
"""
    for entry in avalanche[:5]:
        r = entry.get("relative_round")
        pct = entry.get("diffusion_percentage")
        bits = entry.get("total_flipped_bits")
        x1_f = entry.get("x1_flipped_bits")
        x2_f = entry.get("x2_flipped_bits")
        prompt += f"- Round {r}: {pct}% diffusion ({bits}/320 bits flipped | x1: {x1_f}/64, x2: {x2_f}/64)\n"

    prompt += f"""
#### REGISTER LINEAR BIAS ANALYSIS:
- x1 Mean Bit Density: {bias.get('x1_mean_bit_density')}
- x2 Mean Bit Density: {bias.get('x2_mean_bit_density')}
- Max Linear Bias: {bias.get('max_linear_bias')} (Severity: {bias.get('bias_severity')})

#### EARLY ROUND HEXADECIMAL SNAPSHOT:
"""
    for snap in early_rounds[:2]:
        p = snap.get("phase")
        r = snap.get("round")
        regs = snap.get("registers", {})
        prompt += f"[{p} R{r}] x0={regs.get('x0')} x1={regs.get('x1')} x2={regs.get('x2')}\n"

    prompt += """
Perform rigorous cryptanalysis. Determine if the cipher exhibits linear or differential biases that an ML adversary could exploit. State your findings, compute your confidence, and output your final VERDICT."""
    return prompt
