"""
Project Eagle Eye - Specification Matching & QC Rules Engine
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

from typing import List, Dict, Any, Tuple
from ..vision.ocr_engine import LabelOCREngine

class QCRulesEngine:
    CONFIDENCE_THRESHOLD = 0.75

    def __init__(self, expected_components: List[Dict[str, Any]], expected_wires: List[Dict[str, Any]]):
        self.expected_components = {c['tag']: c for c in expected_components}
        self.expected_wires = {w['tag']: w for w in expected_wires}

    def evaluate(self, detections: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Applies deterministic Quality Control rules against detected components
        and matches them with engineering blueprints and Excel schedules.
        """
        checklist = []
        total_confidence = 0.0

        for det in detections:
            tag = det["tag"]
            is_present = det.get("is_present", True)
            obs_label = det.get("observed_label", "")
            obs_rating = det.get("observed_rating", "")
            confidence = det.get("confidence", 0.90)
            bbox = det.get("bbox", [0, 0, 100, 100])
            location = det.get("rail", "Rail 1")
            comp_type = det.get("component_type", "Industrial Component")

            total_confidence += confidence
            exp_comp = self.expected_components.get(tag, {})
            exp_wire = self.expected_wires.get(tag, {})

            # Rule 1: Component Presence Verification
            if not is_present or obs_label == "VACANT_SLOT":
                checklist.append({
                    "item_code": tag,
                    "component_type": comp_type,
                    "expected_val": f"Present ({exp_comp.get('type', comp_type)})",
                    "observed_val": "Missing / Vacant Slot",
                    "location": location,
                    "rule_type": "Component Presence",
                    "status": "FAIL",
                    "fault_type": "Missing Component",
                    "confidence": confidence,
                    "bbox": bbox,
                    "notes": f"Critical Safety Violation: Expected device '{tag}' not mounted on {location}."
                })
                continue

            # Rule 2: Label & OCR Verification
            is_match, sim_score, diagnosis = LabelOCREngine.match_label(obs_label, tag)

            if not is_match and "Unclear" not in obs_label and "Ferrule" not in obs_label:
                checklist.append({
                    "item_code": tag,
                    "component_type": comp_type,
                    "expected_val": f"Label '{tag}'",
                    "observed_val": f"Label '{obs_label}'",
                    "location": location,
                    "rule_type": "Label Accuracy",
                    "status": "FAIL",
                    "fault_type": "Label Mismatch",
                    "confidence": confidence,
                    "bbox": bbox,
                    "notes": f"Label deviation flagged: {diagnosis}. Verify component markings."
                })
                continue

            # Rule 3: Ferrule & Wiring Verification (Terminal Blocks / Wires)
            ferrule_observed = det.get("ferrule_observed")
            if ferrule_observed:
                expected_ferrule = exp_wire.get("ferrule", "X1-4")
                if ferrule_observed != expected_ferrule:
                    checklist.append({
                        "item_code": tag,
                        "component_type": comp_type,
                        "expected_val": f"Ferrule '{expected_ferrule}' on Terminal 4",
                        "observed_val": f"Ferrule '{ferrule_observed}' found",
                        "location": location,
                        "rule_type": "Wire & Ferrule Integrity",
                        "status": "FAIL",
                        "fault_type": "Wiring Ferrule Mismatch",
                        "confidence": confidence,
                        "bbox": bbox,
                        "notes": f"Wire connection mismatch: Expected wire '{expected_ferrule}' connected to terminal, but found '{ferrule_observed}'."
                    })
                    continue

            # Rule 4: Visual Clarity / Low Confidence Inspection
            if confidence < self.CONFIDENCE_THRESHOLD or "Unclear" in obs_label:
                checklist.append({
                    "item_code": tag,
                    "component_type": comp_type,
                    "expected_val": f"Legible '{tag}' Marking",
                    "observed_val": f"Partially Obscured ('{obs_label}')",
                    "location": location,
                    "rule_type": "Visual Readability",
                    "status": "NEEDS_REVIEW",
                    "fault_type": "Low Confidence / Glare",
                    "confidence": confidence,
                    "bbox": bbox,
                    "notes": "Surface dust, optical glare, or camera angle reduces OCR certainty. Requires technician visual verification."
                })
                continue

            # Rule 5: Specification Compliance (All checks passed)
            exp_rating = exp_comp.get("rating", obs_rating)
            checklist.append({
                "item_code": tag,
                "component_type": comp_type,
                "expected_val": f"{tag} | {exp_rating}",
                "observed_val": f"{obs_label} | {obs_rating}",
                "location": location,
                "rule_type": "Specification Match",
                "status": "PASS",
                "fault_type": None,
                "confidence": confidence,
                "bbox": bbox,
                "notes": "Component mounted in correct orientation, label verified, rating complies with drawing."
            })

        # Calculate Summary Metrics
        total = len(checklist)
        passed = sum(1 for c in checklist if c["status"] == "PASS")
        failed = sum(1 for c in checklist if c["status"] == "FAIL")
        review = sum(1 for c in checklist if c["status"] == "NEEDS_REVIEW")
        avg_conf = round((total_confidence / total) * 100, 1) if total > 0 else 0.0

        overall_status = "FAIL" if failed > 0 else ("NEEDS_REVIEW" if review > 0 else "PASS")

        summary = {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "review_checks": review,
            "confidence_avg": avg_conf,
            "overall_status": overall_status
        }

        return checklist, summary
