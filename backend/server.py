"""
Project Eagle Eye - Main Application Server (Flask REST & Web App)
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import os
import time
import json
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename

from .database import init_db, save_inspection_run, get_all_runs, get_run_by_id, log_recheck
from .models import InspectionRun, ChecklistItem
from .parsers.excel_parser import WireLabelScheduleParser
from .parsers.pdf_parser import BlueprintPDFParser
from .vision.detector import ComponentDetector
from .vision.annotator import ImageAnnotator
from .rules.qc_engine import QCRulesEngine
from .reports.report_generator import QCReportGenerator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample_inputs")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

# Initialize SQLite database
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/evidence/<path:filename>")
def serve_evidence(filename):
    return send_from_directory(EVIDENCE_DIR, filename)

@app.route("/sample_inputs/<path:filename>")
def serve_sample(filename):
    return send_from_directory(SAMPLE_DIR, filename)

@app.route("/reports/<path:filename>")
def serve_report_file(filename):
    return send_from_directory(REPORTS_DIR, filename)

@app.route("/api/status", methods=["GET"])
def get_status():
    runs = get_all_runs()
    return jsonify({
        "status": "ONLINE",
        "system": "Project Eagle Eye Multimodal AI",
        "team": "Team Survivors",
        "track": "Track 01 - Emerson",
        "leader": "Nagesh Patthe",
        "members": ["Nagesh Patthe", "Abhijeet More", "Shubham Yadav", "Prathmesh Dandge"],
        "total_inspections": len(runs),
        "ai_engines": {
            "component_detector": "ACTIVE",
            "ocr_label_matcher": "ACTIVE",
            "blueprint_pdf_parser": "ACTIVE",
            "excel_schedule_parser": "ACTIVE",
            "closed_loop_verifier": "ACTIVE"
        }
    })

@app.route("/api/inspect", methods=["POST"])
def run_inspection():
    """
    Accepts cabinet photograph, blueprint PDF, and wire list Excel.
    Runs multimodal parsing, detection, OCR, rule evaluation, annotation, and report generation.
    """
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_slug = int(time.time())

    cabinet_id = request.form.get("cabinet_id", "EE-024")
    cabinet_name = request.form.get("cabinet_name", "Industrial 415V Control Cabinet")
    is_demo = request.form.get("is_demo", "false").lower() == "true"

    # 1. Resolve Input Files
    cabinet_file = request.files.get("cabinet_photo")
    blueprint_file = request.files.get("blueprint_pdf")
    wire_file = request.files.get("wire_list")

    # If demo or files omitted, fall back to sample dataset
    if is_demo or not cabinet_file:
        cabinet_img_path = os.path.join(SAMPLE_DIR, "cabinet_initial.jpg")
    else:
        fname = f"cab_{timestamp_slug}_{secure_filename(cabinet_file.filename)}"
        cabinet_img_path = os.path.join(UPLOAD_DIR, fname)
        cabinet_file.save(cabinet_img_path)

    if is_demo or not blueprint_file:
        blueprint_path = os.path.join(SAMPLE_DIR, "blueprint_schematic.pdf")
    else:
        fname = f"bp_{timestamp_slug}_{secure_filename(blueprint_file.filename)}"
        blueprint_path = os.path.join(UPLOAD_DIR, fname)
        blueprint_file.save(blueprint_path)

    if is_demo or not wire_file:
        wire_path = os.path.join(SAMPLE_DIR, "wire_label_list.xlsx")
    else:
        fname = f"wire_{timestamp_slug}_{secure_filename(wire_file.filename)}"
        wire_path = os.path.join(UPLOAD_DIR, fname)
        wire_file.save(wire_path)

    # 2. Parse Specifications
    pdf_parser = BlueprintPDFParser(blueprint_path)
    blueprint_data = pdf_parser.parse()

    excel_parser = WireLabelScheduleParser(wire_path)
    wire_schedule = excel_parser.parse()

    # 3. Vision Detection & OCR
    detector = ComponentDetector()
    detections = detector.detect_in_image(cabinet_img_path, is_recheck=False)

    # 4. QC Rule Engine Evaluation
    qc_engine = QCRulesEngine(
        expected_components=blueprint_data["expected_components"],
        expected_wires=wire_schedule
    )
    raw_checklist, summary = qc_engine.evaluate(detections)

    # 5. Image Annotation & Evidence Crop Generation
    annotated_filename = f"annotated_{timestamp_slug}.jpg"
    annotated_full_path = os.path.join(EVIDENCE_DIR, annotated_filename)
    
    annotated_items = ImageAnnotator.annotate_and_crop(
        image_path=cabinet_img_path,
        checklist_items=raw_checklist,
        output_annotated_path=annotated_full_path,
        evidence_dir=EVIDENCE_DIR,
        run_id=timestamp_slug
    )

    # 6. Save to SQLite Database
    checklist_models = [
        ChecklistItem(
            id=None,
            run_id=0,
            item_code=i["item_code"],
            component_type=i["component_type"],
            expected_val=i["expected_val"],
            observed_val=i["observed_val"],
            location=i["location"],
            rule_type=i["rule_type"],
            status=i["status"],
            fault_type=i.get("fault_type"),
            confidence=i["confidence"],
            bbox=i["bbox"],
            evidence_crop=i.get("evidence_crop"),
            notes=i["notes"]
        ) for i in annotated_items
    ]

    report_filename = f"report_run_{timestamp_slug}.html"
    report_full_path = os.path.join(REPORTS_DIR, report_filename)

    run_model = InspectionRun(
        id=None,
        cabinet_id=cabinet_id,
        cabinet_name=cabinet_name,
        run_type="INITIAL",
        timestamp=timestamp_str,
        status=summary["overall_status"],
        total_checks=summary["total_checks"],
        passed_checks=summary["passed_checks"],
        failed_checks=summary["failed_checks"],
        review_checks=summary["review_checks"],
        confidence_avg=summary["confidence_avg"],
        image_path=cabinet_img_path,
        annotated_image_path=f"/evidence/{annotated_filename}",
        blueprint_file=os.path.basename(blueprint_path),
        wire_list_file=os.path.basename(wire_path),
        report_path=f"/reports/{report_filename}",
        notes="Automated multimodal initial inspection run."
    )

    run_id = save_inspection_run(run_model, checklist_models)

    # 7. Generate Official QC Certificate
    run_dict = run_model.to_dict()
    run_dict["id"] = run_id
    run_dict["checklist"] = annotated_items
    QCReportGenerator.generate_html_report(run_dict, report_full_path)

    return jsonify({
        "success": True,
        "run_id": run_id,
        "summary": summary,
        "annotated_image": f"/evidence/{annotated_filename}",
        "raw_image": f"/sample_inputs/cabinet_initial.jpg" if is_demo else f"/evidence/{annotated_filename}",
        "report_url": f"/reports/{report_filename}",
        "checklist": annotated_items,
        "drawing_specs": blueprint_data
    })

@app.route("/api/recheck", methods=["POST"])
def run_recheck():
    """
    Closed-Loop Verification:
    Technician uploads corrected photo; system verifies only previously failed items or full panel.
    """
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_slug = int(time.time())

    original_run_id = int(request.form.get("original_run_id", 1))
    orig_run = get_run_by_id(original_run_id) or {}
    
    recheck_file = request.files.get("corrected_photo")
    if not recheck_file:
        cabinet_img_path = os.path.join(SAMPLE_DIR, "cabinet_corrected.jpg")
    else:
        fname = f"recheck_{timestamp_slug}_{secure_filename(recheck_file.filename)}"
        cabinet_img_path = os.path.join(UPLOAD_DIR, fname)
        recheck_file.save(cabinet_img_path)

    # Re-detect with corrected=True
    detector = ComponentDetector()
    detections = detector.detect_in_image(cabinet_img_path, is_recheck=True)

    # Use default specs
    blueprint_path = os.path.join(SAMPLE_DIR, "blueprint_schematic.pdf")
    wire_path = os.path.join(SAMPLE_DIR, "wire_label_list.xlsx")

    pdf_parser = BlueprintPDFParser(blueprint_path)
    blueprint_data = pdf_parser.parse()
    excel_parser = WireLabelScheduleParser(wire_path)
    wire_schedule = excel_parser.parse()

    qc_engine = QCRulesEngine(blueprint_data["expected_components"], wire_schedule)
    raw_checklist, summary = qc_engine.evaluate(detections)

    annotated_filename = f"recheck_annotated_{timestamp_slug}.jpg"
    annotated_full_path = os.path.join(EVIDENCE_DIR, annotated_filename)

    annotated_items = ImageAnnotator.annotate_and_crop(
        image_path=cabinet_img_path,
        checklist_items=raw_checklist,
        output_annotated_path=annotated_full_path,
        evidence_dir=EVIDENCE_DIR,
        run_id=timestamp_slug
    )

    report_filename = f"recheck_report_{timestamp_slug}.html"
    report_full_path = os.path.join(REPORTS_DIR, report_filename)

    run_model = InspectionRun(
        id=None,
        cabinet_id=orig_run.get("cabinet_id", "EE-024"),
        cabinet_name=orig_run.get("cabinet_name", "Industrial 415V Control Cabinet"),
        run_type="RECHECK",
        timestamp=timestamp_str,
        status=summary["overall_status"],
        total_checks=summary["total_checks"],
        passed_checks=summary["passed_checks"],
        failed_checks=summary["failed_checks"],
        review_checks=summary["review_checks"],
        confidence_avg=summary["confidence_avg"],
        image_path=cabinet_img_path,
        annotated_image_path=f"/evidence/{annotated_filename}",
        blueprint_file="blueprint_schematic.pdf",
        wire_list_file="wire_label_list.xlsx",
        report_path=f"/reports/{report_filename}",
        notes=f"Closed-loop re-check verification against Run #{original_run_id}."
    )

    checklist_models = [
        ChecklistItem(
            id=None,
            run_id=0,
            item_code=i["item_code"],
            component_type=i["component_type"],
            expected_val=i["expected_val"],
            observed_val=i["observed_val"],
            location=i["location"],
            rule_type=i["rule_type"],
            status=i["status"],
            fault_type=i.get("fault_type"),
            confidence=i["confidence"],
            bbox=i["bbox"],
            evidence_crop=i.get("evidence_crop"),
            notes=i["notes"]
        ) for i in annotated_items
    ]

    recheck_id = save_inspection_run(run_model, checklist_models)

    # Log closed-loop resolution
    prev_failed = orig_run.get("failed_checks", 3)
    curr_failed = summary["failed_checks"]
    resolved = max(0, prev_failed - curr_failed)
    log_recheck(original_run_id, recheck_id, resolved, curr_failed, "All technician corrections verified.")

    run_dict = run_model.to_dict()
    run_dict["id"] = recheck_id
    run_dict["checklist"] = annotated_items
    QCReportGenerator.generate_html_report(run_dict, report_full_path)

    return jsonify({
        "success": True,
        "original_run_id": original_run_id,
        "recheck_run_id": recheck_id,
        "summary": summary,
        "resolved_issues": resolved,
        "still_open": curr_failed,
        "annotated_image": f"/evidence/{annotated_filename}",
        "report_url": f"/reports/{report_filename}",
        "checklist": annotated_items
    })

@app.route("/api/history", methods=["GET"])
def get_history():
    runs = get_all_runs()
    return jsonify(runs)

@app.route("/api/run/<int:run_id>", methods=["GET"])
def get_single_run(run_id):
    run = get_run_by_id(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run)

def start_server(port=5000):
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_server(5000)
