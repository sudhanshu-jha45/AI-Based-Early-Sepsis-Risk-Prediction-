"""
BioMarkerX V6 — Next-Generation Architectural Improvement Module
Implements advanced enhancements for future clinical deployment:
1. Vasopressor-adjusted MAP physiological gating.
2. Adaptive early-stay window persistence (p=1 for t<6h, p=2 for t<12h, p=3 for t>=12h).
3. Real-time FHIR / HL7 payload parser interface.
"""

import numpy as np
import pandas as pd

class BioMarkerXV6Enhancements:
    def __init__(self, tau_screening=0.015, tau_confirmation=0.300):
        self.tau_screening = tau_screening
        self.tau_confirmation = tau_confirmation

    def calculate_vasopressor_adjusted_map(self, map_val, vasopressor_dose=0.0):
        """
        Adjusts MAP for active vasopressor support.
        If a patient receives vasopressors (e.g. Norepinephrine), their true unassisted MAP
        is lower than observed. Offset prevents post-operative MAP masking.
        """
        # Estimated 5 mmHg MAP drop per standard vasopressor dose tier
        offset = vasopressor_dose * 5.0
        return map_val - offset

    def evaluate_adaptive_persistence(self, risk_series, icu_los_hours):
        """
        Applies adaptive persistence window length based on ICU length of stay.
        - LOS < 6h: p = 1 window (rapid early warning for short-stay patients)
        - LOS < 12h: p = 2 windows
        - LOS >= 12h: p = 3 windows (standard stability filtering)
        """
        alerts = []
        raw_hits = (risk_series >= self.tau_screening).astype(int)
        
        for idx, (hit, los) in enumerate(zip(raw_hits, icu_los_hours)):
            if los < 6.0:
                p = 1
            elif los < 12.0:
                p = 2
            else:
                p = 3
                
            if idx < p - 1:
                alerts.append(0)
            else:
                window_sum = sum(raw_hits[idx - p + 1 : idx + 1])
                alerts.append(1 if window_sum == p else 0)
                
        return pd.Series(alerts, index=risk_series.index)

    def parse_fhir_observation_stream(self, fhir_json_payload):
        """
        Simulates parsing a real-time FHIR Observation bundle into a BioMarkerX feature vector.
        """
        features = {}
        for entry in fhir_json_payload.get("entry", []):
            resource = entry.get("resource", {})
            code = resource.get("code", {}).get("text", "")
            value = resource.get("valueQuantity", {}).get("value", np.nan)
            
            if "Heart Rate" in code or "HR" in code:
                features["HR"] = value
            elif "Mean Arterial Pressure" in code or "MAP" in code:
                features["MAP"] = value
            elif "Temperature" in code or "Temp" in code:
                features["Temp"] = value
            elif "Oxygen Saturation" in code or "O2Sat" in code:
                features["O2Sat"] = value
                
        return features

def run_v6_roadmap_demo():
    print("=========================================================================")
    print("BIOMARKERX V6 — NEXT-GENERATION IMPROVEMENT ROADMAP MODULE")
    print("=========================================================================\n")

    enhancer = BioMarkerXV6Enhancements()

    # Demo 1: Vasopressor Adjustment
    obs_map = 80.0
    vaso_dose = 1.5 # Active Norepinephrine
    adj_map = enhancer.calculate_vasopressor_adjusted_map(obs_map, vaso_dose)
    print(f"[IMPROVEMENT 1] Vasopressor MAP Adjustment:")
    print(f"  Observed MAP: {obs_map} mmHg | Vasopressor Support Level: {vaso_dose}")
    print(f"  Adjusted Unassisted MAP: {adj_map:.1f} mmHg -> Triggers Gate (<= 75 mmHg)!")

    # Demo 2: Adaptive Persistence for Short ICU Stays
    los_hours = pd.Series([2.0, 3.0, 4.0, 7.0, 8.0, 13.0, 14.0, 15.0])
    risks = pd.Series([0.02, 0.02, 0.00, 0.02, 0.02, 0.02, 0.02, 0.02])
    adaptive_alerts = enhancer.evaluate_adaptive_persistence(risks, los_hours)
    print(f"\n[IMPROVEMENT 2] Adaptive Persistence for Short ICU Stays (< 12 Hours):")
    print(f"  LOS Hours: {list(los_hours)}")
    print(f"  Raw Risk Hits (tau >= 0.015): {list((risks >= 0.015).astype(int))}")
    print(f"  Adaptive Alerts Fired:         {list(adaptive_alerts)}")
    print("  -> Short-stay patients trigger alert at p=1 and p=2 without waiting 3 hours!")

    # Demo 3: FHIR Stream Parser
    sample_fhir = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"code": {"text": "Heart Rate"}, "valueQuantity": {"value": 104.0}}},
            {"resource": {"code": {"text": "Mean Arterial Pressure"}, "valueQuantity": {"value": 68.5}}},
            {"resource": {"code": {"text": "Oxygen Saturation"}, "valueQuantity": {"value": 96.0}}}
        ]
    }
    parsed_feats = enhancer.parse_fhir_observation_stream(sample_fhir)
    print(f"\n[IMPROVEMENT 3] Real-Time FHIR Streaming Parser:")
    print(f"  Parsed Features: {parsed_feats}")

    print("\n=========================================================================")

if __name__ == "__main__":
    run_v6_roadmap_demo()
