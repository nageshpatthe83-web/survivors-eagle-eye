"""
Project Eagle Eye - Models and Schemas
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class ChecklistItem:
    id: Optional[int]
    run_id: int
    item_code: str
    component_type: str
    expected_val: str
    observed_val: str
    location: str
    rule_type: str
    status: str  # 'PASS', 'FAIL', 'NEEDS_REVIEW'
    fault_type: Optional[str]
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    evidence_crop: Optional[str]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class InspectionRun:
    id: Optional[int]
    cabinet_id: str
    cabinet_name: str
    run_type: str  # 'INITIAL' or 'RECHECK'
    timestamp: str
    status: str  # 'PASS', 'FAIL', 'NEEDS_REVIEW'
    total_checks: int
    passed_checks: int
    failed_checks: int
    review_checks: int
    confidence_avg: float
    image_path: str
    annotated_image_path: str
    blueprint_file: str
    wire_list_file: str
    report_path: Optional[str] = None
    notes: Optional[str] = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
