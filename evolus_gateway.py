"""
Ascon-Guard AI: Evolus REST API Orchestration Gateway
=====================================================
Acts as middleware orchestrator compliant with the Evolus Partner Track.
Structures messy cryptographic hex bitstreams into structured workflow payloads,
dispatches execution tasks to the AMD Cloud GPU node, and manages pipeline routing.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

# Load .env if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

EVOLUS_API_BASE = os.getenv("EVOLUS_API_BASE", "https://api.evolus.ai")
EVOLUS_API_KEY = os.getenv("EVOLUS_API_KEY", "")
EVOLUS_WORKSPACE_ID = os.getenv("EVOLUS_WORKSPACE_ID", "8b7b8b9d-4217-49ee-b6d9-c5e467b78a6b")

class EvolusGateway:
    def __init__(self, api_key: Optional[str] = None, workspace_id: Optional[str] = None):
        self.api_key = api_key or EVOLUS_API_KEY
        self.workspace_id = workspace_id or EVOLUS_WORKSPACE_ID
        self.headers = {
            "X-ApiKey": self.api_key,
            "X-Application-Id": self.workspace_id,
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

    def structure_payload(self, telemetry_digest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structures the raw Ascon cryptographic data into an Evolus Workflow schema.
        Maps the 5 registers (x0..x4), round-by-round diffusion, and metadata into
        a standardized cryptanalytic audit request.
        """
        return {
            "workflow_name": "ascon_iot_cryptanalysis_audit",
            "version": "1.0.0",
            "source_node": {
                "origin": "Bihar_Rural_Health_SubCentre",
                "device_type": "IoT_LowPower_CortexM4",
                "cipher_standard": "NIST_SP_800_232_Ascon128"
            },
            "cryptographic_telemetry": {
                "fault_mode": telemetry_digest.get("engine_mode", "SECURE"),
                "sample_patient_id": telemetry_digest.get("sample_patient_id"),
                "ciphertext_sample": telemetry_digest.get("ciphertext_hex"),
                "tag": telemetry_digest.get("tag_hex"),
                "avalanche_diffusion_summary": telemetry_digest.get("avalanche_profile", []),
                "linear_bias": telemetry_digest.get("linear_bias_metrics", {}),
                "early_rounds": telemetry_digest.get("early_round_states", [])
            },
            "routing_target": "AMD_INSTINCT_MI300X_VLLM",
            "audit_criteria": {
                "strict_uncertainty_threshold": 0.90,
                "human_in_the_loop_required": True,
                "action_on_critical_flaw": "LOCK_DEVICE_DEPLOYMENT"
            }
        }

    def dispatch_workflow(self, structured_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches the structured payload to the Evolus Workflow engine.
        If live EVOLUS_API_KEY is present, sends HTTP POST to Evolus REST API.
        Otherwise, runs in local high-fidelity gateway simulation mode.
        """
        if self.api_key and "evolus.ai" in EVOLUS_API_BASE:
            try:
                response = requests.post(
                    f"{EVOLUS_API_BASE}/workflows/dispatch",
                    headers=self.headers,
                    json=structured_payload,
                    timeout=10
                )
                if response.status_code == 200:
                    return {
                        "status": "DISPATCHED_LIVE",
                        "evolus_job_id": response.json().get("job_id"),
                        "payload": structured_payload
                    }
            except Exception as e:
                pass  # Fall back to simulated pipeline if remote endpoint unreachable

        # High-Fidelity Gateway Emulation (Used before hackathon kickoff or offline testing)
        return {
            "status": "DISPATCHED_SIMULATED",
            "gateway_node": "Evolus-API-Middleware-v1.4",
            "workspace": self.workspace_id,
            "routing_destination": "AMD_INSTINCT_VLLM_CLUSTER",
            "payload_bytes": len(json.dumps(structured_payload)),
            "payload": structured_payload
        }
