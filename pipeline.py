"""
Ascon-Guard AI: Automated Cryptanalysis & Hardware Optimization Pipeline
========================================================================
Main Orchestrator connecting:
[Laptop: ascon_engine.py] -> [Evolus Gateway] -> [AMD Instinct MI300X vLLM]
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.rule import Rule

from ascon_engine import AsconEngine, generate_rural_clinic_record
from cryptanalysis import generate_telemetry_digest
from evolus_gateway import EvolusGateway
from amd_auditor import AmdAuditor

console = Console(force_terminal=True)

def display_banner():
    banner = """[bold cyan]
  ==================================================================================
      ___   _____ _____ ____  _   _          ____ _   _    _    ____  ____  
     / _ \ / ____/ ____/ __ \| \ | |        / ___| | | |  / \  |  _ \|  _ \ 
    / /_\ \\\___ \\\___ \ |  | |  \| | _____ | |  _| | | | / _ \ | |_) | | | |
    |  _  |___) |___) | |__| | |\  ||_____|| |_| | |_| |/ ___ \|  _ <| |_| |
    |_| |_|____/_____/ \____/|_| \_|        \____|\___//_/   \_\_| \_\____/ 
  ==================================================================================[/bold cyan]
[bold white]  AUTOMATED CRYPTANALYSIS & HARDWARE OPTIMIZATION FOR MEDICAL IoT | AMD ACT III HACKATHON[/bold white]
[dim cyan]  Target: NIST SP 800-232 Ascon-128 | Infrastructure: AMD Instinct MI300X + Evolus Gateway[/dim cyan]
"""
    console.print(banner)

def run_audit_cycle(fault_mode: str = "SECURE"):
    console.print(Rule(f"[bold yellow]STARTING AUDIT: MODE = {fault_mode}[/bold yellow]"))

    # STEP A: Local Ascon Execution & Telemetry Generation
    with Progress(SpinnerColumn(), TextColumn("[bold green]{task.description}"), BarColumn(), transient=True) as progress:
        t1 = progress.add_task("[cyan]Step A: Generating Ascon-128 bitstream & rural clinic vitals...", total=100)
        time.sleep(0.3)
        digest = generate_telemetry_digest(fault_mode=fault_mode)
        progress.update(t1, advance=100)

    # Display Vitals & Registers
    patient_json = generate_rural_clinic_record()
    console.print(Panel(
        f"[bold white]Clinic Node:[/bold white] Katihar Primary Health Sub-Centre (Bihar)\n"
        f"[bold white]Patient Telemetry:[/bold white] {patient_json}\n"
        f"[bold white]Ascon-128 Ciphertext Sample:[/bold white] [green]{digest['ciphertext_hex']}[/green] | [bold white]Tag:[/bold white] [yellow]{digest['tag_hex'][:16]}...[/yellow]",
        title="[bold cyan][STEP A] Edge Medical IoT Telemetry[/bold cyan]",
        border_style="cyan"
    ))

    # Strict Avalanche Criterion Table
    diff_table = Table(title="Strict Avalanche Criterion (SAC) Diffusion Curve", header_style="bold magenta")
    diff_table.add_column("Permutation Round", justify="center")
    diff_table.add_column("Flipped Bits (/320)", justify="center")
    diff_table.add_column("Diffusion %", justify="center")
    diff_table.add_column("x1 / x2 Distribution", justify="center")
    diff_table.add_column("NIST Target", justify="center")

    for entry in digest["avalanche_profile"][:6]:
        r = entry["relative_round"]
        flipped = entry["total_flipped_bits"]
        pct = entry["diffusion_percentage"]
        dist = f"x1:{entry['x1_flipped_bits']} | x2:{entry['x2_flipped_bits']}"
        target = "PASS (~50%)" if pct >= 45.0 else ("[bold red]FAIL (DEFICIT)[/bold red]" if r >= 3 else "IN_PROGRESS")
        color = "green" if pct >= 45.0 else ("red" if r >= 3 else "yellow")
        diff_table.add_row(f"Round {r}", str(flipped), f"[{color}]{pct}%[/{color}]", dist, target)

    console.print(diff_table)

    # STEP B: Evolus Gateway Structuring & Dispatch
    with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), transient=True) as progress:
        t2 = progress.add_task("[blue]Step B: Routing through Evolus REST API Middleware...", total=100)
        time.sleep(0.4)
        gateway = EvolusGateway()
        structured_payload = gateway.structure_payload(digest)
        evolus_dispatch = gateway.dispatch_workflow(structured_payload)
        progress.update(t2, advance=100)

    console.print(Panel(
        f"[bold white]Evolus Status:[/bold white] [green]{evolus_dispatch['status']}[/green]\n"
        f"[bold white]Target Cluster:[/bold white] [bold cyan]{evolus_dispatch.get('routing_destination')}[/bold cyan]\n"
        f"[bold white]Workspace Schema:[/bold white] {evolus_dispatch.get('workspace')} (Payload: {evolus_dispatch.get('payload_bytes', 1280)} bytes)\n"
        f"[bold white]Safety Threshold:[/bold white] >= 90% Confidence | Strict Human-in-the-Loop Enforced",
        title="[bold blue][STEP B] Evolus Gateway Dispatch[/bold blue]",
        border_style="blue"
    ))

    # STEP C: AMD Instinct vLLM Cryptanalysis & Uncertainty Audit
    with Progress(SpinnerColumn(), TextColumn("[bold magenta]{task.description}"), transient=True) as progress:
        t3 = progress.add_task("[magenta]Step C: Auditing on AMD Instinct MI300X vLLM Node...", total=100)
        time.sleep(0.6)
        auditor = AmdAuditor()
        audit_result = auditor.audit_telemetry(structured_payload)
        progress.update(t3, advance=100)

    # Display Verdict & Uncertainty Badge
    alert_level = audit_result["alert_level"]
    confidence = audit_result["confidence_percentage"]
    model = audit_result["model"]
    source = audit_result["source"]

    if alert_level == "CRITICAL_SYSTEM_HOLE_FOUND":
        badge = f"[bold white on red] [!] [CRITICAL SYSTEM HOLE FOUND] [/bold white on red] Confidence: [bold red]{confidence}[/bold red]"
        box_style = "bold red"
        action = "[bold red]ACTION: LOCKING DOWN DATA ROUTING ENGINE & EDGE FIRMWARE FLASHING HALTED![/bold red]"
    elif alert_level == "UNCERTAIN_WARNING":
        badge = f"[bold black on yellow] [?] [UNCERTAIN WEAKNESS - REVIEW REQUIRED] [/bold black on yellow] Confidence: [bold yellow]{confidence} (<90% threshold)[/bold yellow]"
        box_style = "bold yellow"
        action = "[bold yellow]ACTION: SAFETY PROTOCOL ENGAGED -> HUMAN SECURITY EXPERT NOTIFIED TO REVIEW BEFORE DEPLOYMENT![/bold yellow]"
    else:
        badge = f"[bold white on green] [*] [NIST VERIFIED - SECURE DEPLOYMENT] [/bold white on green] Confidence: [bold green]{confidence}[/bold green]"
        box_style = "bold green"
        action = "[bold green]ACTION: MEDICAL IoT SENSORS APPROVED FOR BIHAR FIELD CLINIC TRANSMISSION.[/bold green]"

    console.print(Panel(
        f"{badge}\n\n"
        f"[bold white]Compute Infrastructure:[/bold white] {source} (Model: {model})\n"
        f"[bold white]Cryptanalytic Verdict:[/bold white] {audit_result['verdict']}\n"
        f"[bold white]Model Reasoning & Proof:[/bold white]\n{audit_result['reasoning']}\n\n"
        f"{action}",
        title="[bold magenta][STEP C] AMD Instinct Cryptanalysis & Uncertainty Audit[/bold magenta]",
        border_style=box_style
    ))
    console.print("\n")

def main():
    display_banner()
    console.print("[bold]Select a Clinical Hardware Threat Scenario to Audit:[/bold]")
    console.print("  [1] 🛡️  NIST SP 800-232 Canonical Telemetry (Katihar Clinic Safe Baseline)")
    console.print("  [2] 🚨  Aggressive Battery-Saver Hack (4-Round Truncation - ML Leak)")
    console.print("  [3] ⚠️   Low-Voltage Hardware Glitch (Silicon Brownout / Linear Rotation Drift)")
    console.print("  [4] 🚀  Run Full End-to-End Clinical Test Suite (All 3 scenarios sequentially)\n")

    choice = input("Enter option [1-4] (default=4): ").strip() or "4"

    if choice == "1":
        run_audit_cycle("NIST_SECURE")
    elif choice == "2":
        run_audit_cycle("BATTERY_HACK_4ROUNDS")
    elif choice == "3":
        run_audit_cycle("VOLTAGE_GLITCH_LINEAR")
    else:
        run_audit_cycle("NIST_SECURE")
        run_audit_cycle("BATTERY_HACK_4ROUNDS")
        run_audit_cycle("VOLTAGE_GLITCH_LINEAR")

if __name__ == "__main__":
    main()
