"""
Project Eagle Eye - Excel & CSV Wire / Label Schedule Parser
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import pandas as pd
import os
from typing import List, Dict, Any

class WireLabelScheduleParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> List[Dict[str, Any]]:
        """Parses component, wire, and label records."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Check extension
        if self.filepath.lower().endswith('.csv'):
            df = pd.read_csv(self.filepath)
        else:
            df = pd.read_excel(self.filepath)

        # Normalize column names (strip, lower, replace spaces with underscores)
        col_map = {c: str(c).strip().lower().replace(' ', '_').replace('/', '_') for c in df.columns}
        df = df.rename(columns=col_map)

        records = []
        for idx, row in df.iterrows():
            tag = str(row.get('tag', row.get('tag_number', row.get('device_tag', f'DEV-{idx+1}')))).strip()
            comp_type = str(row.get('component_type', row.get('type', row.get('device', 'Unknown')))).strip()
            rating = str(row.get('expected_rating', row.get('rating', row.get('specification', 'N/A')))).strip()
            rail = str(row.get('location_rail', row.get('location', row.get('rail', 'Rail 1')))).strip()
            ferrule = str(row.get('ferrule_code', row.get('ferrule', row.get('wire_label', tag)))).strip()
            term_from = str(row.get('terminal_from', row.get('from', 'L1'))).strip()
            term_to = str(row.get('terminal_to', row.get('to', 'T1'))).strip()
            wire_color = str(row.get('wire_color', row.get('color', 'Black'))).strip()

            records.append({
                "tag": tag,
                "component_type": comp_type,
                "rating": rating,
                "rail": rail,
                "ferrule": ferrule,
                "terminal_from": term_from,
                "terminal_to": term_to,
                "wire_color": wire_color,
                "row_index": idx + 1
            })

        return records
