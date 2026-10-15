"""
Project Eagle Eye - Database Manager
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from .models import InspectionRun, ChecklistItem

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'eagle_eye_qc.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for inspection runs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inspection_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cabinet_id TEXT NOT NULL,
        cabinet_name TEXT NOT NULL,
        run_type TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        total_checks INTEGER NOT NULL,
        passed_checks INTEGER NOT NULL,
        failed_checks INTEGER NOT NULL,
        review_checks INTEGER NOT NULL,
        confidence_avg REAL NOT NULL,
        image_path TEXT NOT NULL,
        annotated_image_path TEXT NOT NULL,
        blueprint_file TEXT NOT NULL,
        wire_list_file TEXT NOT NULL,
        report_path TEXT,
        notes TEXT
    )
    ''')

    # Table for itemized checklist items
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        item_code TEXT NOT NULL,
        component_type TEXT NOT NULL,
        expected_val TEXT NOT NULL,
        observed_val TEXT NOT NULL,
        location TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        status TEXT NOT NULL,
        fault_type TEXT,
        confidence REAL NOT NULL,
        bbox TEXT NOT NULL,
        evidence_crop TEXT,
        notes TEXT,
        FOREIGN KEY (run_id) REFERENCES inspection_runs(id) ON DELETE CASCADE
    )
    ''')

    # Table for re-check links
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recheck_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_run_id INTEGER NOT NULL,
        recheck_run_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        resolved_count INTEGER NOT NULL,
        still_open_count INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY (original_run_id) REFERENCES inspection_runs(id),
        FOREIGN KEY (recheck_run_id) REFERENCES inspection_runs(id)
    )
    ''')

    conn.commit()
    conn.close()

def save_inspection_run(run: InspectionRun, items: List[ChecklistItem]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO inspection_runs (
        cabinet_id, cabinet_name, run_type, timestamp, status,
        total_checks, passed_checks, failed_checks, review_checks,
        confidence_avg, image_path, annotated_image_path,
        blueprint_file, wire_list_file, report_path, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        run.cabinet_id, run.cabinet_name, run.run_type, run.timestamp, run.status,
        run.total_checks, run.passed_checks, run.failed_checks, run.review_checks,
        run.confidence_avg, run.image_path, run.annotated_image_path,
        run.blueprint_file, run.wire_list_file, run.report_path, run.notes
    ))
    
    run_id = cursor.lastrowid

    for item in items:
        cursor.execute('''
        INSERT INTO checklist_items (
            run_id, item_code, component_type, expected_val, observed_val,
            location, rule_type, status, fault_type, confidence,
            bbox, evidence_crop, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id, item.item_code, item.component_type, item.expected_val, item.observed_val,
            item.location, item.rule_type, item.status, item.fault_type, item.confidence,
            json.dumps(item.bbox), item.evidence_crop, item.notes
        ))

    conn.commit()
    conn.close()
    return run_id

def get_all_runs() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inspection_runs ORDER BY id DESC')
    rows = cursor.fetchall()
    runs = [dict(r) for r in rows]
    conn.close()
    return runs

def get_run_by_id(run_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inspection_runs WHERE id = ?', (run_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    run = dict(row)
    cursor.execute('SELECT * FROM checklist_items WHERE run_id = ? ORDER BY id ASC', (run_id,))
    items = []
    for item_row in cursor.fetchall():
        item_dict = dict(item_row)
        try:
            item_dict['bbox'] = json.loads(item_dict['bbox'])
        except Exception:
            item_dict['bbox'] = [0, 0, 0, 0]
        items.append(item_dict)
    
    run['checklist'] = items
    conn.close()
    return run

def log_recheck(orig_id: int, recheck_id: int, resolved: int, still_open: int, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    import time
    cursor.execute('''
    INSERT INTO recheck_logs (original_run_id, recheck_run_id, timestamp, resolved_count, still_open_count, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (orig_id, recheck_id, time.strftime('%Y-%m-%d %H:%M:%S'), resolved, still_open, notes))
    conn.commit()
    conn.close()
