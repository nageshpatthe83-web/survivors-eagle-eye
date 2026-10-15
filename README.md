# Project Eagle Eye 🦅
**AI-Powered Industrial Control Panel Quality Inspection**  
*Track 01 — Emerson | CODE APEX Hackathon (Powered by Verzii)*

---

## 👥 Team Survivors
* **Nagesh Patthe** — *Team Leader*
* **Abhijeet More** — *Team Member*
* **Shubham Yadav** — *Team Member*
* **Prathmesh Dandge** — *Team Member*

---

## 🎯 Problem Statement & Target Need
Industrial control panels must be verified against engineering drawings (PDF blueprints), component bills of materials (BOM), and wire/label schedules (Excel). Today, quality-control inspectors manually cross-check hundreds of wires, labels, and DIN-rail modules.

These repetitive manual checks suffer from:
* **High Human Error:** Small character misprints (e.g., `QFZ` instead of `QF2`) and incorrect wire ferrules slip through.
* **Lack of Visual Evidence:** Hard to document precisely which terminal or wire had the defect.
* **No Closed-Loop Verification:** Difficulty in auditing whether technician corrections actually resolved the open issues.

---

## 💡 The Solution: Project Eagle Eye
**Project Eagle Eye** is a specification-driven, multimodal AI quality-control system:
1. **Multi-Input Ingestion:** Accepts cabinet photographs (JPG/PNG), engineering blueprints (PDF), and wire/label schedules (Excel/CSV).
2. **Computer Vision & OCR:** Detects circuit breakers (MCBs), contactors, safety relays, power supplies, and terminal strips; extracts ferrule tags and component markings.
3. **Deterministic QC Rules Engine:** Evaluates component presence, label accuracy, terminal wiring integrity, and specification ratings.
4. **Explainable QC Evidence:** Links flagged defects directly to high-resolution bounding boxes and zoomed visual crop snippets.
5. **Closed-Loop Verification:** Re-inspects corrected cabinet photos and generates official IEC 61439-2 / UL 508A compliance certificates.

---

## 🏗️ System Architecture

```
                  +--------------------------------------------------------+
                  |                      INPUT LAYER                       |
                  |  Cabinet Photo (JPG) | Blueprint (PDF) | Schedule (XLS)|
                  +--------------------------------------------------------+
                                              |
                                              v
                  +--------------------------------------------------------+
                  |                    PROCESSING LAYER                    |
                  | • PDF Drawing Parser (pypdf)                           |
                  | • Excel Wire Schedule Parser (pandas/openpyxl)         |
                  | • Component & DIN Rail Object Detector (Pillow/NumPy)  |
                  | • Text & Ferrule Label OCR Matcher (Fuzzy Matching)    |
                  +--------------------------------------------------------+
                                              |
                                              v
                  +--------------------------------------------------------+
                  |                     DECISION LAYER                     |
                  | Specification Matching & QC Rules Engine               |
                  | [PASS] Compliant | [FAIL] Fault Flagged | [REVIEW] Low |
                  +--------------------------------------------------------+
                                              |
                                              v
                  +--------------------------------------------------------+
                  |                      OUTPUT LAYER                      |
                  | • Interactive Canvas Bounding Box Overlay              |
                  | • Zoomed Evidence Crops Gallery                        |
                  | • Itemized PASS/FAIL Checklist                         |
                  | • Official Printable/Downloadable QC Certificate (PDF) |
                  | • Closed-Loop Before/After Verification                |
                  +--------------------------------------------------------+
```

---

## 🛠️ Quickstart Guide

### 1. Prerequisites
* Python 3.10+ installed
* Modern Web Browser (Chrome, Edge, Firefox)

### 2. Installation
```bash
git clone https://github.com/nageshpatthe83-web/survivors-eagle-eye.git
cd survivors-eagle-eye
pip install -r requirements.txt
```

### 3. Launch with 1-Click
```bash
python run.py
```
Open **`http://localhost:5050`** in your browser.

---

## 📁 Repository Structure

```
survivors/
├── backend/
│   ├── server.py               # Flask REST server & Static routes
│   ├── models.py               # Dataclasses & schemas
│   ├── database.py             # SQLite persistence layer
│   ├── generate_samples.py     # Synthetic realistic sample data generator
│   ├── parsers/
│   │   ├── pdf_parser.py       # Blueprint CAD/schematic PDF reader
│   │   └── excel_parser.py     # Wire & label schedule Excel parser
│   ├── vision/
│   │   ├── detector.py         # DIN rail & component object detector
│   │   ├── ocr_engine.py       # Text & ferrule label OCR matcher
│   │   └── annotator.py        # Visual bounding box drawer & crop generator
│   ├── rules/
│   │   └── qc_engine.py        # Specification matching QC rules engine
│   └── reports/
│       └── report_generator.py # Emerson QC Certificate generator
├── frontend/
│   ├── static/
│   │   ├── css/style.css       # Obsidian & Cyber-Emerald Dark Mode theme
│   │   └── js/app.js           # Interactive SVG canvas & closed-loop logic
│   └── templates/
│       └── index.html          # Main Single Page Application UI
├── data/
│   ├── sample_inputs/          # Pre-packaged Emerson control panel samples
│   │   ├── cabinet_initial.jpg
│   │   ├── cabinet_corrected.jpg
│   │   ├── blueprint_schematic.pdf
│   │   └── wire_label_list.xlsx
│   ├── evidence/               # Zoomed crops generated during inspection
│   └── db/                     # SQLite database (eagle_eye_qc.db)
├── run.py                      # 1-Click platform runner
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🏆 Hackathon Details
* **Event:** CODE APEX (Powered by Verzii)
* **Track:** Track 01 — Emerson
* **Team:** Team Survivors
* **Members:** Nagesh Patthe (Lead), Abhijeet More, Shubham Yadav, Prathmesh Dandge
