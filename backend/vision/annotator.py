"""
Project Eagle Eye - Image Annotator & Zoom Evidence Snippet Generator
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any

class ImageAnnotator:
    COLOR_PASS = (16, 185, 129, 255)       # Emerald Green
    COLOR_FAIL = (244, 63, 94, 255)        # Neon Crimson / Rose
    COLOR_REVIEW = (245, 158, 11, 255)     # Amber Gold

    @staticmethod
    def annotate_and_crop(
        image_path: str,
        checklist_items: List[Dict[str, Any]],
        output_annotated_path: str,
        evidence_dir: str,
        run_id: int
    ) -> List[Dict[str, Any]]:
        """
        Draws bounding boxes and labels on the cabinet image,
        and generates cropped evidence snippets for flagged faults.
        """
        os.makedirs(os.path.dirname(output_annotated_path), exist_ok=True)
        os.makedirs(evidence_dir, exist_ok=True)

        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Default system font or fallback
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 13)
        except Exception:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        updated_items = []

        for item in checklist_items:
            bbox = item.get("bbox", [0, 0, 50, 50])
            status = item.get("status", "PASS")
            tag = item.get("item_code", "DEV")
            obs_val = item.get("observed_val", "")

            # Select color based on status
            if status == "FAIL":
                stroke_color = ImageAnnotator.COLOR_FAIL
                fill_color = (244, 63, 94, 40)
            elif status == "NEEDS_REVIEW":
                stroke_color = ImageAnnotator.COLOR_REVIEW
                fill_color = (245, 158, 11, 40)
            else:
                stroke_color = ImageAnnotator.COLOR_PASS
                fill_color = (16, 185, 129, 30)

            x1, y1, x2, y2 = bbox
            # Draw translucent fill box
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=stroke_color, width=3)
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)

            # Draw tag badge at top of bounding box
            badge_text = f"[{status}] {tag}"
            badge_w = len(badge_text) * 9 + 10
            badge_h = 24
            badge_y1 = max(0, y1 - badge_h)
            draw.rectangle([x1, badge_y1, x1 + badge_w, badge_y1 + badge_h], fill=stroke_color)
            draw.text((x1 + 6, badge_y1 + 4), badge_text, fill=(255, 255, 255, 255), font=font_small)

            # Generate zoomed evidence crop for items
            evidence_rel_path = None
            try:
                # Add 25px margin around component for context
                margin = 25
                crop_x1 = max(0, x1 - margin)
                crop_y1 = max(0, y1 - margin)
                crop_x2 = min(img.width, x2 + margin)
                crop_y2 = min(img.height, y2 + margin)
                
                with Image.open(image_path) as orig_img:
                    crop = orig_img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                    # Resize snippet to consistent card size if too small
                    if crop.width < 160 or crop.height < 120:
                        crop = crop.resize((max(180, crop.width * 2), max(140, crop.height * 2)), Image.Resampling.LANCZOS)
                    
                    crop_filename = f"crop_run{run_id}_{tag}.jpg"
                    crop_full_path = os.path.join(evidence_dir, crop_filename)
                    crop.convert("RGB").save(crop_full_path, "JPEG", quality=90)
                    evidence_rel_path = f"/evidence/{crop_filename}"
            except Exception as e:
                print(f"Error generating crop for {tag}: {e}")

            item_copy = dict(item)
            item_copy["evidence_crop"] = evidence_rel_path
            updated_items.append(item_copy)

        # Convert back to RGB and save annotated master image
        img.convert("RGB").save(output_annotated_path, "JPEG", quality=92)
        return updated_items
