"""
Project Eagle Eye - Text & Ferrule Label OCR Engine
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

from typing import Dict, Any, Tuple
import difflib

class LabelOCREngine:
    @staticmethod
    def calculate_similarity(s1: str, s2: str) -> float:
        """Returns string similarity between 0.0 and 1.0."""
        s1_clean = "".join(c for c in s1.upper() if c.isalnum() or c == '-')
        s2_clean = "".join(c for c in s2.upper() if c.isalnum() or c == '-')
        if not s1_clean or not s2_clean:
            return 0.0
        return difflib.SequenceMatcher(None, s1_clean, s2_clean).ratio()

    @staticmethod
    def match_label(observed_text: str, expected_tag: str) -> Tuple[bool, float, str]:
        """
        Matches observed OCR string against expected engineering tag.
        Returns: (is_match, confidence, diagnosis)
        """
        if not observed_text:
            return False, 0.0, "No text detected in OCR target region"

        sim = LabelOCREngine.calculate_similarity(observed_text, expected_tag)
        
        if sim >= 0.95:
            return True, sim, "Exact match with engineering drawing tag"
        elif sim >= 0.65:
            # Subtle typo or OCR misread (e.g., QF2 vs QFZ)
            return False, sim, f"Character mismatch detected: observed '{observed_text}' vs expected '{expected_tag}'"
        else:
            return False, sim, f"Severe label deviation: observed '{observed_text}' does not match '{expected_tag}'"
