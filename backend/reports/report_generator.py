"""
Project Eagle Eye - Official QC Inspection Report Generator
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import os
from typing import Dict, Any, List

class QCReportGenerator:
    @staticmethod
    def generate_html_report(run_data: Dict[str, Any], output_path: str) -> str:
        """Generates an Emerson-compliant industrial QC Certificate and Report."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        run = run_data
        checklist = run.get("checklist", [])
        
        status_color = "#10b981" if run["status"] == "PASS" else ("#f43f5e" if run["status"] == "FAIL" else "#f59e0b")

        # Build table rows
        rows_html = ""
        for idx, item in enumerate(checklist, 1):
            st = item["status"]
            badge_class = "badge-pass" if st == "PASS" else ("badge-fail" if st == "FAIL" else "badge-review")
            evidence_img = ""
            if item.get("evidence_crop"):
                evidence_img = f'<img src="{item["evidence_crop"]}" class="report-thumb" alt="Evidence">'
            else:
                evidence_img = '<span class="text-muted">N/A</span>'

            rows_html += f"""
            <tr>
                <td>{idx}</td>
                <td><strong>{item['item_code']}</strong><br><small>{item['component_type']}</small></td>
                <td>{item['location']}</td>
                <td><code>{item['expected_val']}</code></td>
                <td><code>{item['observed_val']}</code></td>
                <td><span class="report-badge {badge_class}">{st}</span></td>
                <td>{int(item['confidence'] * 100)}%</td>
                <td>{evidence_img}</td>
                <td><small>{item['notes']}</small></td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QC Inspection Certificate - {run['cabinet_id']}</title>
    <style>
        @page {{ size: A4 landscape; margin: 12mm; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #fff;
            color: #1e293b;
            margin: 0;
            padding: 24px;
        }}
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #0f172a;
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .brand-title {{
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.5px;
        }}
        .brand-sub {{
            color: #059669;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
        }}
        .meta-item {{ font-size: 13px; }}
        .meta-label {{ color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
        .meta-val {{ font-size: 15px; font-weight: 700; color: #0f172a; margin-top: 4px; }}
        .status-pill {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            color: #fff;
            font-weight: 800;
            font-size: 14px;
            background: {status_color};
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-bottom: 24px;
        }}
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background: #0f172a;
            color: #fff;
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        .report-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 11px;
            color: #fff;
        }}
        .badge-pass {{ background: #10b981; }}
        .badge-fail {{ background: #f43f5e; }}
        .badge-review {{ background: #f59e0b; }}
        .report-thumb {{
            width: 70px;
            height: 45px;
            object-fit: cover;
            border-radius: 4px;
            border: 1px solid #94a3b8;
        }}
        .signoff-section {{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px dashed #cbd5e1;
            font-size: 13px;
        }}
        .sign-box {{ width: 220px; text-align: center; border-top: 1px solid #000; padding-top: 8px; margin-top: 40px; }}
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 16px; text-align: right;">
        <button onclick="window.print()" style="background:#0f172a; color:#fff; padding:8px 16px; border:none; border-radius:4px; cursor:pointer; font-weight:700;">🖨️ Print / Save as PDF</button>
    </div>

    <div class="report-header">
        <div>
            <div class="brand-title">EMERSON • PROJECT EAGLE EYE</div>
            <div class="brand-sub">Industrial Control Panel Quality Inspection Certificate</div>
        </div>
        <div style="text-align: right;">
            <div class="status-pill">{run['status']}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Run #{run.get('id', 1)} • {run['run_type']}</div>
        </div>
    </div>

    <div class="meta-grid">
        <div class="meta-item">
            <div class="meta-label">Cabinet ID & Model</div>
            <div class="meta-val">{run['cabinet_id']} ({run['cabinet_name']})</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Inspection Timestamp</div>
            <div class="meta-val">{run['timestamp']}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Assessment Team</div>
            <div class="meta-val">Team Survivors (Lead: Nagesh Patthe)</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Pass Rate / Total Checks</div>
            <div class="meta-val">{run['passed_checks']} / {run['total_checks']} Passed ({int((run['passed_checks']/max(1, run['total_checks']))*100)}%)</div>
        </div>
    </div>

    <h3>Itemized Quality Control (QC) Checklist & Evidence</h3>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Component / Tag</th>
                <th>Location</th>
                <th>Expected Spec</th>
                <th>Observed Spec</th>
                <th>Status</th>
                <th>Conf</th>
                <th>Evidence</th>
                <th>Findings / Remarks</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div class="signoff-section">
        <div>
            <strong>Inspection System:</strong> Project Eagle Eye Multimodal AI v2.4<br>
            <strong>Standard:</strong> IEC 61439-2 / UL 508A Industrial Control Standards<br>
            <strong>Engineering Drawings:</strong> {run['blueprint_file']} • {run['wire_list_file']}
        </div>
        <div>
            <div class="sign-box">Lead QC Inspector: Nagesh Patthe</div>
        </div>
        <div>
            <div class="sign-box">Quality Assurance Manager Sign-off</div>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path
