"""
Ascon-Guard AI: Google Slides Presentation Generator
Constructs a publication-quality 10-slide deck in Google Slides via gslides CLI.
"""

import json
import subprocess
import time

PRES_ID = "1q2du7nOglhrbh3yeQ3oB6DUdmYNylehhmtGxisejsgg"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running: {cmd}\nOutput: {res.stderr or res.stdout}")
    return res.stdout.strip()

def get_slides():
    out = run_cmd(f"gslides readonly list-slides {PRES_ID} --json")
    try:
        data = json.loads(out)
        return [s["id"] for s in data]
    except Exception:
        # Fallback to text parsing
        lines = out.splitlines()
        slide_ids = []
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 2:
                slide_ids.append(parts[1])
        return slide_ids

def add_slide():
    out = run_cmd(f"gslides mutate add-slide {PRES_ID}")
    for word in out.split():
        if "SLIDES_" in word:
            return word
    # If not parsed, refresh slides list
    time.sleep(1)
    slides = get_slides()
    return slides[-1]

def set_bg(slide_id, color):
    run_cmd(f'gslides mutate set-background {PRES_ID} --slide {slide_id} --color "{color}"')

def add_box(slide_id, text, x, y, w, h, font_size=12, bold=False, color="#1E293B", align="left"):
    # escape quotes
    clean_text = text.replace('"', '\\"')
    bold_flag = "--bold" if bold else ""
    cmd = f'gslides mutate add-textbox {PRES_ID} --slide {slide_id} --text "{clean_text}" --x {x} --y {y} --width {w} --height {h} --font-size {font_size} {bold_flag} --color "{color}" --alignment {align}'
    run_cmd(cmd)

def set_notes(slide_id, notes):
    clean_notes = notes.replace('"', '\\"')
    run_cmd(f'gslides mutate set-notes {PRES_ID} --slide {slide_id} --text "{clean_notes}"')

def main():
    print("Building Ascon-Guard AI Presentation Deck...")
    slides = get_slides()
    print(f"Current slides: {slides}")
    
    # ---------------- SLIDE 1 (p): Title Slide ----------------
    s1 = slides[0]
    set_bg(s1, "#0B132B")
    
    # Badge
    add_box(s1, "AMD DEVELOPER HACKATHON: ACT III  |  TRACK 2: HEALTH & WELLBEING  |  EVOLUS TRACK", 50, 40, 620, 25, font_size=9, bold=True, color="#60A5FA", align="center")
    # Main Title
    add_box(s1, "Ascon-Guard AI", 50, 80, 620, 60, font_size=36, bold=True, color="#FFFFFF", align="center")
    # Subtitle
    add_box(s1, "Autonomous Cryptanalysis & Hardware-Accelerated Verification for NIST SP 800-232 Ascon-128 in Rural Bihar Medical IoT", 60, 150, 600, 50, font_size=14, bold=False, color="#94A3B8", align="center")
    
    # Author Card
    add_box(s1, "Principal Developer: Diwakar Sharma (Healthy Vihar Foundation, Bihar, India)\nCompute Infrastructure: AMD Instinct MI300X (ROCm 6.2) & Evolus Multi-Agent Framework\nEdge Target: ARM Cortex-M4 (STM32L476RG, 80 MHz, 128KB SRAM)", 70, 240, 580, 70, font_size=10, bold=False, color="#E2E8F0", align="center")
    
    set_notes(s1, "Good day esteemed judges. Today we present Ascon-Guard AI, an autonomous hardware security and cryptanalytic verification pipeline protecting maternal and neonatal IoT telemetry in rural Bihar using NIST SP 800-232 Ascon-128 and AMD Instinct MI300X accelerators.")
    print("Slide 1 built.")

    # ---------------- SLIDE 2: The Healthcare Dilemma ----------------
    s2 = slides[1] if len(slides) > 1 else add_slide()
    set_bg(s2, "#F8FAFC")
    add_box(s2, "CLINICAL CONTEXT: RURAL BIHAR TELEHEALTH", 50, 30, 620, 20, font_size=10, bold=True, color="#DC2626")
    add_box(s2, "The Edge Cryptographic Dilemma in Resource-Constrained Clinics", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    points_s2 = (
        "- Flood-Prone Field Reality: In Supaul, Saharsa, and Madhepura districts, maternal health centers face 14-hour daily grid blackouts, relying on intermittent solar & coin-cell batteries.\n\n"
        "- The AES-128-GCM Failure: Standard enterprise encryption demands 54.6 uJ per packet and 9.4 KB Flash. Coin cells deplete in under 4 months, forcing edge engineers to bypass encryption entirely.\n\n"
        "- Brownouts & Voltage Glitches: Power sags during MCU operation cause bit-flips, de-synchronizing state permutations and exposing patient vitals to tampering and eavesdropping.\n\n"
        "- The Critical Need: NIST SP 800-232 Ascon-128 lightweight authenticated cipher paired with cloud AI auditing."
    )
    add_box(s2, points_s2, 50, 110, 620, 220, font_size=11, bold=False, color="#334155")
    set_notes(s2, "In Northern Bihar, maternal health monitors run on battery power. Traditional AES encryption drains batteries rapidly, so edge developers turn off encryption. We solve this by implementing NIST Ascon-128.")
    print("Slide 2 built.")

    # ---------------- SLIDE 3: NIST SP 800-232 Ascon-128 Architecture ----------------
    s3 = add_slide()
    set_bg(s3, "#FFFFFF")
    add_box(s3, "CRYPTOGRAPHIC FOUNDATIONS", 50, 30, 620, 20, font_size=10, bold=True, color="#2563EB")
    add_box(s3, "NIST SP 800-232 Ascon-128 Sponge Architecture", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    points_s3 = (
        "- 320-Bit Internal State: S = (x0, x1, x2, x3, x4), partitioned into five 64-bit registers.\n"
        "- Duplex Sponge Construction: Rate r = 64 bits, Capacity c = 256 bits, 128-bit Key, 128-bit Nonce, 128-bit Tag.\n\n"
        "- Mathematical Round Permutation: p = p_L o p_S o p_C\n"
        "   1. Constant Addition (p_C): Injects 8-bit round constant into register x2 to destroy rotational symmetries.\n"
        "   2. Non-Linear Substitution (p_S): 5-bit S-box applied bit-sliced across 64 parallel bit columns (Degree 2, Max Diff 2^-2, Linear Bias 2^-1).\n"
        "   3. Linear Diffusion (p_L): Intra-word 64-bit circular right shifts (>>> 19, 28, 61, 39, 1, 6, 10, 17, 7, 41) achieving complete bit diffusion in 3 rounds."
    )
    add_box(s3, points_s3, 50, 110, 620, 230, font_size=10.5, bold=False, color="#334155")
    set_notes(s3, "Ascon-128 operates on a 320-bit state with a duplex sponge construction. Its bit-sliced 5-bit S-box and circular shift diffusion layer offer optimal side-channel masking and minimal hardware gate counts.")
    print("Slide 3 built.")

    # ---------------- SLIDE 4: The 3 Clinical Threat Scenarios ----------------
    s4 = add_slide()
    set_bg(s4, "#F8FAFC")
    add_box(s4, "SYSTEM EVALUATION & THREAT MODELS", 50, 30, 620, 20, font_size=10, bold=True, color="#D97706")
    add_box(s4, "Three Real-World Clinical Threat Scenarios", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    scenarios_text = (
        "[SCENARIO 1: NIST Standard 12-Round Execution (Nominal Vitals)]\n"
        "- Full 12-round permutation (p^a). Complete diffusion, linear correlation quenched (eps <= 2^-128).\n"
        "- AI Verdict: NIST_VERIFIED_SECURE | Confidence: 98.4% (Certified Pass >= 90%). Direct EHR Ingestion.\n\n"
        "[SCENARIO 2: Battery Conservation Attack (4-Round Truncation Exploit)]\n"
        "- Firmware truncates permutation rounds from 12 to 4 to save battery.\n"
        "- Unquenched linear hull (eps = 2^-3), tag forgeable in 2^33 ops instead of 2^128.\n"
        "- AI Verdict: CRITICAL_SYSTEM_HOLE_FOUND | Confidence: 96.2% (Certified Exploit >= 90%). Automated Quarantine.\n\n"
        "[SCENARIO 3: Voltage Glitch / Brownout Side-Channel (Indeterminate State)]\n"
        "- Solar drop brownout causes bit-flips in registers x1 and x2 during round execution.\n"
        "- AI Verdict: UNCERTAIN_WARNING | Confidence: 78.4% (< 90% Threshold). Human-in-the-Loop Escalation."
    )
    add_box(s4, scenarios_text, 50, 105, 620, 240, font_size=9.5, bold=False, color="#1E293B")
    set_notes(s4, "We validate the system across 3 realistic conditions: nominal 12 rounds, an aggressive 4-round battery truncation attack, and an electrical brownout glitch where confidence drops to 78.4%.")
    print("Slide 4 built.")

    # ---------------- SLIDE 5: AMD Instinct MI300X & Uncertainty Logic ----------------
    s5 = add_slide()
    set_bg(s5, "#FFFFFF")
    add_box(s5, "CLOUD ACCELERATION: AMD ROCm 6.2 & vLLM", 50, 30, 620, 20, font_size=10, bold=True, color="#7C3AED")
    add_box(s5, "AMD Instinct MI300X Neural Auditor & Uncertainty Protocol", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    points_s5 = (
        "- Hardware Specs: AMD Instinct MI300X (192GB HBM3, 5.3 TB/s memory bandwidth) via ROCm 6.2.\n"
        "- High-Throughput Inference: vLLM serving engine with PagedAttention and HIP graph execution.\n"
        "- Multi-Model Resilience: Primary model google/gemma-4-31b-it with failover to DeepSeek-V3 and Qwen-2.5-72B.\n\n"
        "- The Tri-State Uncertainty Decision Framework:\n"
        "   * Rule 1 (Secure >= 90%): Verified mathematically sound -> Pass to Electronic Health Record.\n"
        "   * Rule 2 (Vulnerable >= 90%): Critical algebraic exploit confirmed -> Instant firewall drop & node quarantine.\n"
        "   * Rule 3 (Uncertain < 90%): Model explicitly refuses to guess on side-channel anomalies -> Human-in-the-Loop takeover."
    )
    add_box(s5, points_s5, 50, 110, 620, 230, font_size=10.5, bold=False, color="#334155")
    set_notes(s5, "Our neural auditor runs on AMD Instinct MI300X with ROCm 6.2. Most importantly, it enforces a strict Tri-State Uncertainty threshold: anything under 90% confidence triggers human clinician escalation.")
    print("Slide 5 built.")

    # ---------------- SLIDE 6: Evolus Multi-Agent Orchestration ----------------
    s6 = add_slide()
    set_bg(s6, "#F8FAFC")
    add_box(s6, "PARTNER TRACK: EVOLUS BUSINESS AGENTS", 50, 30, 620, 20, font_size=10, bold=True, color="#059669")
    add_box(s6, "Autonomous Multi-Agent Middleware Architecture", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    agents_text = (
        "- EdgeTelemetryIngestAgent: Validates CRC32 integrity, packet sequence freshness, and nonce uniqueness from rural Bihar gateways.\n\n"
        "- AsconAuditAgent: Extracts 320-bit internal state registers, formats cryptographic evaluation prompts, and queries the AMD Instinct MI300X inference cluster.\n\n"
        "- EscalationAgent: Governs Human-in-the-Loop workflows whenever auditor confidence falls below 90.0%, routing emergency SMS and dashboard alerts to biomedical supervisors.\n\n"
        "- HardwarePolicyAgent: Dynamically enforces 12-round execution constraints and over-the-air (OTA) cryptographic microcode updates on remote clinic microcontrollers."
    )
    add_box(s6, agents_text, 50, 110, 620, 230, font_size=10.5, bold=False, color="#334155")
    set_notes(s6, "The Evolus Business Agent framework coordinates the end-to-end security pipeline across four specialized micro-agents, handling data ingestion, cryptanalysis, policy enforcement, and escalation.")
    print("Slide 6 built.")

    # ---------------- SLIDE 7: Live Cloud Telemetry & ROCm 6.2 ----------------
    s7 = add_slide()
    set_bg(s7, "#0F172A")
    add_box(s7, "LIVE STREAMING INFRASTRUCTURE", 50, 30, 620, 20, font_size=10, bold=True, color="#38BDF8")
    add_box(s7, "100% Continuous Real-Time Hardware & Cloud Telemetry", 50, 55, 620, 35, font_size=20, bold=True, color="#FFFFFF")
    
    telemetry_text = (
        "- Streamlit 1.65 Native @st.fragment(run_every='2s'): Seamless live auto-refresh without page flicker or tab resets.\n\n"
        "- 4 Live Hardware Gauges: AMD Instinct MI300X Core Utilization (%), HBM3 Memory Allocated (GB), Board Power Draw (W), and ROCm Compute Engine Load (%).\n\n"
        "- Real-Time KPI Ribbon: Live socket latency (ms), token velocity (tok/s), prompt tokens, completion tokens, query cost ($), and remaining rate limits.\n\n"
        "- Rolling 16-Sample Time-Series Area Chart: Live micro-jitter latency tracking and raw HTTP socket header inspection."
    )
    add_box(s7, telemetry_text, 50, 110, 620, 230, font_size=10.5, bold=False, color="#E2E8F0")
    set_notes(s7, "Tab 3 delivers continuous 2-second streaming telemetry from the AMD Instinct MI300X cluster, providing live gauges, token velocities, and socket latency tracking.")
    print("Slide 7 built.")

    # ---------------- SLIDE 8: Edge Embedded Benchmarks ----------------
    s8 = add_slide()
    set_bg(s8, "#FFFFFF")
    add_box(s8, "EMBEDDED BENCHMARKS: ARM CORTEX-M4", 50, 30, 620, 20, font_size=10, bold=True, color="#EA580C")
    add_box(s8, "NIST Ascon-128 vs. Legacy AES-128-GCM Comparison", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    bench_text = (
        "Empirical benchmarks conducted on ARM Cortex-M4 (STM32L476RG @ 80 MHz, 128KB SRAM):\n\n"
        "* Flash Memory Footprint: 1.8 KB (Ascon-128) vs. 9.4 KB (AES-GCM)  -->  5.2x Smaller Footprint\n"
        "* SRAM Memory Allocation: 360 Bytes (Ascon-128) vs. 2,140 Bytes (AES-GCM)  -->  5.9x Less RAM Usage\n"
        "* Energy Consumption (per 64B packet): 14.2 uJ vs. 54.6 uJ  -->  3.8x Energy Reduction\n"
        "* Execution Speed: 31 cycles/byte vs. 118 cycles/byte  -->  3.8x Speedup\n"
        "* CR2032 Coin-Cell Lifespan (1 packet/min): 16.1 Months vs. 4.2 Months  -->  3.8x Extended Field Lifetime"
    )
    add_box(s8, bench_text, 50, 110, 620, 230, font_size=10.5, bold=False, color="#1E293B")
    set_notes(s8, "Our physical benchmarks on ARM Cortex-M4 demonstrate a 3.8x energy reduction and 5.2x memory savings over AES-128-GCM, extending field battery life from 4.2 to 16.1 months.")
    print("Slide 8 built.")

    # ---------------- SLIDE 9: Full 6-Tab Console ----------------
    s9 = add_slide()
    set_bg(s9, "#F8FAFC")
    add_box(s9, "GUI ARCHITECTURE & SYSTEM CONSOLE", 50, 30, 620, 20, font_size=10, bold=True, color="#4F46E5")
    add_box(s9, "The Complete 6-Tab Unified Security Dashboard", 50, 55, 620, 35, font_size=20, bold=True, color="#0F172A")
    
    gui_text = (
        "- Tab 1: Clinical IoT Node Dashboard  -->  Patient vitals, edge encryption terminal, and 320-bit hex state inspector.\n"
        "- Tab 2: AMD Neural Cryptanalysis  -->  Tri-State auditor, dynamic confidence gauge, clean reasoning typography.\n"
        "- Tab 3: Cloud GPU Telemetry  -->  Continuous 2s streaming, 4 live Plotly gauges, latency jitter, AMD headers.\n"
        "- Tab 4: Evolus Business Workspace  -->  Agent state machines, chronological audit feed, human override console.\n"
        "- Tab 5: Edge Benchmarks  -->  Interactive energy/memory comparison charts, battery longevity calculator.\n"
        "- Tab 6: Interactive S-Box & Permutation Inspector  -->  Bit-sliced visualizer, round constants, rotational diffusion."
    )
    add_box(s9, gui_text, 50, 110, 620, 230, font_size=10.5, bold=False, color="#334155")
    set_notes(s9, "The unified dashboard provides 6 comprehensive modules, covering live patient vitals, neural cryptanalysis, cloud GPU metrics, multi-agent workspaces, edge benchmarks, and cryptographic internals.")
    print("Slide 9 built.")

    # ---------------- SLIDE 10: Conclusion & Clinical Roadmap ----------------
    s10 = add_slide()
    set_bg(s10, "#0B132B")
    add_box(s10, "CONCLUSION & IMPACT", 50, 40, 620, 20, font_size=10, bold=True, color="#60A5FA", align="center")
    add_box(s10, "Transforming Healthcare Security for Rural India", 50, 70, 620, 45, font_size=26, bold=True, color="#FFFFFF", align="center")
    
    concl_text = (
        "Ascon-Guard AI proves that next-generation lightweight cryptography (NIST SP 800-232 Ascon-128)\n"
        "combined with cloud AMD Instinct MI300X neural auditing and the Evolus Multi-Agent Framework\n"
        "can protect vulnerable rural medical infrastructure against physical and algebraic threats.\n\n"
        "Key Accomplishments:\n"
        "- 3.8x Battery Lifespan Extension on ARM Cortex-M4 edge medical nodes.\n"
        "- Sub-second neural cryptanalysis with strict 90% Tri-State Uncertainty fail-safes.\n"
        "- 100% Continuous Live Streaming Hardware & ROCm Telemetry.\n"
        "- Proven Clinical Deployment Readiness for Maternal & Infant Telehealth in Bihar."
    )
    add_box(s10, concl_text, 60, 140, 600, 180, font_size=11, bold=False, color="#CBD5E1", align="center")
    add_box(s10, "Thank You! | Healthy Vihar Foundation & AMD Developer Hackathon: ACT III", 50, 335, 620, 30, font_size=12, bold=True, color="#38BDF8", align="center")
    set_notes(s10, "Thank you for your time. Ascon-Guard AI is ready to safeguard healthcare delivery for thousands of mothers and infants across rural Bihar.")
    print("Slide 10 built.")

if __name__ == "__main__":
    main()
