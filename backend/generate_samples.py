"""
Project Eagle Eye - Synthetic Industrial Sample Data Generator
Generates realistic Emerson Control Panel Images, Blueprint PDF, and Wire Schedule Excel.
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import pypdf

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "sample_inputs")

def generate_excel_wire_list():
    excel_path = os.path.join(SAMPLE_DIR, "wire_label_list.xlsx")
    data = [
        {"Tag": "QF1", "Component_Type": "Main MCB 3P", "Expected_Rating": "32A 415V", "Location_Rail": "Rail 1", "Terminal_From": "L1/L2/L3", "Terminal_To": "T1-1", "Wire_Color": "Black", "Ferrule_Code": "F-QF1-IN"},
        {"Tag": "QF2", "Component_Type": "Branch MCB 1P", "Expected_Rating": "16A 230V", "Location_Rail": "Rail 1", "Terminal_From": "L1", "Terminal_To": "T1-2", "Wire_Color": "Black", "Ferrule_Code": "F-QF2-IN"},
        {"Tag": "PS1", "Component_Type": "Power Supply Unit", "Expected_Rating": "24VDC 5A 120W", "Location_Rail": "Rail 1", "Terminal_From": "AC-L/N", "Terminal_To": "DC-OUT", "Wire_Color": "Red/Blue", "Ferrule_Code": "F-PS1"},
        {"Tag": "KM1", "Component_Type": "Motor Contactor", "Expected_Rating": "24V Coil 18A", "Location_Rail": "Rail 2", "Terminal_From": "T2-1", "Terminal_To": "T2-2", "Wire_Color": "Blue", "Ferrule_Code": "F-KM1-A1"},
        {"Tag": "KT1", "Component_Type": "Timer Relay", "Expected_Rating": "24VDC 0-60s", "Location_Rail": "Rail 2", "Terminal_From": "T3-1", "Terminal_To": "T3-2", "Wire_Color": "Blue", "Ferrule_Code": "F-KT1"},
        {"Tag": "KT2", "Component_Type": "Safety Relay", "Expected_Rating": "24VDC Dual Ch.", "Location_Rail": "Rail 2", "Terminal_From": "T3-3", "Terminal_To": "T3-4", "Wire_Color": "Yellow", "Ferrule_Code": "F-KT2"},
        {"Tag": "X1",  "Component_Type": "Terminal Strip 1-10", "Expected_Rating": "600V 30A DIN", "Location_Rail": "Rail 3", "Terminal_From": "Field Wires", "Terminal_To": "Internal", "Wire_Color": "Gray", "Ferrule_Code": "X1-4"}
    ]
    df = pd.DataFrame(data)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Wire_Label_Schedule')
    print(f"Generated Excel: {excel_path}")

def generate_blueprint_pdf():
    pdf_path = os.path.join(SAMPLE_DIR, "blueprint_schematic.pdf")
    # Generate a valid PDF with pypdf and stream
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=842, height=595) # A4 Landscape
    
    # Store standard text in PDF metadata and content
    writer.add_metadata({
        "/Title": "EMERSON CONTROL PANEL SCHEMATIC CP-415V-EE024",
        "/Author": "Emerson Automation Engineering",
        "/Subject": "Project Eagle Eye Quality Assurance Blueprint",
        "/Keywords": "DRAWING: DWG-EMR-2026-EE024 | MODEL: CP-415V-EMR-PRO | STANDARD: IEC 61439-2 / UL 508A"
    })
    
    with open(pdf_path, "wb") as f:
        writer.write(f)
    print(f"Generated Blueprint PDF: {pdf_path}")

def draw_control_panel(is_corrected: bool = False):
    """Generates an ultra-realistic 2D industrial electrical cabinet image."""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (30, 36, 44)) # Steel enclosure interior
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 22)
        font_med = ImageFont.truetype("arial.ttf", 15)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Outer metallic enclosure border
    draw.rectangle([10, 10, W-10, H-10], outline=(70, 80, 95), width=8)
    draw.rectangle([25, 25, W-25, H-25], fill=(38, 44, 54), outline=(50, 58, 70), width=4)

    # Title plate at top
    draw.rectangle([50, 35, 450, 70], fill=(20, 24, 30), outline=(80, 180, 120), width=2)
    draw.text((65, 42), "EMERSON INDUSTRIAL AUTOMATION", fill=(100, 240, 160), font=font_med)
    draw.text((65, 75), "PANEL ID: EE-024 | 415V 3-PHASE 50Hz", fill=(160, 175, 195), font=font_small)

    # 3 Steel DIN Rails
    rails_y = [190, 380, 560]
    for idx, ry in enumerate(rails_y, 1):
        draw.rectangle([80, ry - 14, W - 80, ry + 14], fill=(130, 138, 148), outline=(170, 180, 190), width=2)
        # Slotted holes in DIN rail
        for hx in range(100, W - 100, 40):
            draw.rectangle([hx, ry - 4, hx + 18, ry + 4], fill=(45, 52, 62))
        draw.text((85, ry - 32), f"DIN RAIL {idx}", fill=(130, 150, 170), font=font_small)

    # Wire ducts (gray slotted cable channels)
    draw.rectangle([80, 95, W - 80, 130], fill=(55, 62, 72), outline=(85, 95, 108), width=2) # Top duct
    draw.rectangle([80, 260, W - 80, 295], fill=(55, 62, 72), outline=(85, 95, 108), width=2) # Middle duct 1
    draw.rectangle([80, 450, W - 80, 485], fill=(55, 62, 72), outline=(85, 95, 108), width=2) # Middle duct 2
    draw.rectangle([80, 630, W - 80, 665], fill=(55, 62, 72), outline=(85, 95, 108), width=2) # Bottom duct

    # --- RAIL 1 COMPONENTS ---
    # 1. QF1: 3-Pole Main MCB (x: 120 to 280, y: 112 to 266)
    draw.rectangle([120, 112, 280, 266], fill=(235, 238, 242), outline=(160, 170, 180), width=3)
    # 3 toggle switches (Red/Orange)
    for sw in [140, 185, 230]:
        draw.rectangle([sw, 155, sw + 28, 205], fill=(225, 45, 45), outline=(100, 20, 20), width=2)
    draw.rectangle([130, 225, 270, 255], fill=(255, 255, 255), outline=(120, 130, 140))
    draw.text((150, 230), "QF1 • 32A", fill=(10, 20, 30), font=font_med)

    # 2. QF2: 1-Pole Branch MCB (x: 320 to 440, y: 112 to 266)
    draw.rectangle([320, 112, 440, 266], fill=(235, 238, 242), outline=(160, 170, 180), width=3)
    draw.rectangle([355, 155, 405, 205], fill=(45, 110, 225), outline=(20, 50, 120), width=2)
    draw.rectangle([330, 225, 430, 255], fill=(255, 255, 255), outline=(120, 130, 140))
    
    # Label on QF2: Misprinted as QFZ in initial, fixed to QF2 in corrected!
    qf2_label = "QF2 • 16A" if is_corrected else "QFZ • 16A"
    draw.text((342, 230), qf2_label, fill=(200, 20, 20) if not is_corrected else (10, 20, 30), font=font_med)

    # 3. PS1: 24VDC 5A Power Supply (x: 600 to 880, y: 98 to 273)
    draw.rectangle([600, 98, 880, 273], fill=(48, 55, 68), outline=(100, 115, 135), width=3)
    # Perforated cooling grille
    for gx in range(620, 860, 14):
        draw.line([gx, 115, gx, 160], fill=(25, 30, 38), width=4)
    # LED Indicator
    draw.ellipse([630, 180, 646, 196], fill=(40, 220, 90) if is_corrected else (220, 180, 40))
    draw.text((655, 180), "DC OK 24V", fill=(180, 200, 220), font=font_small)
    
    ps_label = "PS1 • 24V 5A" if is_corrected else "PS-? 24V (DIRT)"
    draw.rectangle([620, 225, 860, 258], fill=(240, 242, 246) if is_corrected else (190, 190, 180), outline=(100, 100, 100))
    draw.text((670, 230), ps_label, fill=(10, 20, 30) if is_corrected else (90, 90, 90), font=font_med)

    # --- RAIL 2 COMPONENTS ---
    # 4. KM1: Motor Contactor (x: 140 to 300, y: 315 to 469)
    draw.rectangle([140, 315, 300, 469], fill=(35, 42, 52), outline=(110, 125, 145), width=3)
    # Screw terminals top & bottom
    for tx in [160, 200, 240, 280]:
        draw.ellipse([tx - 8, 325, tx + 8, 341], fill=(180, 190, 200), outline=(80, 90, 100))
        draw.ellipse([tx - 8, 445, tx + 8, 461], fill=(180, 190, 200), outline=(80, 90, 100))
    draw.rectangle([155, 380, 285, 410], fill=(255, 255, 255))
    draw.text((170, 386), "KM1 • 18A", fill=(10, 20, 30), font=font_med)

    # 5. KT1: Timer Relay (x: 350 to 480, y: 315 to 469)
    draw.rectangle([350, 315, 480, 469], fill=(225, 228, 235), outline=(140, 150, 160), width=3)
    # Rotary dial knob
    draw.ellipse([390, 350, 440, 400], fill=(50, 58, 70), outline=(180, 190, 200), width=2)
    draw.line([415, 355, 415, 375], fill=(255, 255, 255), width=3)
    draw.rectangle([365, 425, 465, 455], fill=(255, 255, 255))
    draw.text((380, 430), "KT1 • 60s", fill=(10, 20, 30), font=font_med)

    # 6. KT2: Safety Relay (x: 520 to 660, y: 315 to 469)
    if is_corrected:
        # Mounted yellow safety relay in corrected photo!
        draw.rectangle([520, 315, 660, 469], fill=(245, 190, 25), outline=(180, 140, 10), width=3)
        draw.rectangle([540, 335, 640, 375], fill=(30, 35, 42))
        draw.text((550, 345), "SAFETY", fill=(255, 255, 255), font=font_med)
        draw.rectangle([535, 425, 645, 455], fill=(255, 255, 255))
        draw.text((545, 430), "KT2 • DUAL", fill=(10, 20, 30), font=font_med)
    else:
        # Vacant empty slot with exposed DIN rail and dangling wire
        draw.text((540, 385), "[VACANT DIN SLOT]", fill=(240, 80, 80), font=font_med)
        # Dangling wire
        draw.line([590, 300, 590, 350], fill=(240, 200, 40), width=3)

    # --- RAIL 3 COMPONENTS ---
    # 7. X1: Terminal Block Strip (x: 120 to 880, y: 518 to 644)
    draw.rectangle([120, 518, 880, 644], fill=(160, 168, 178), outline=(110, 120, 130), width=3)
    # Numbered individual terminal blocks
    for t_idx in range(1, 11):
        bx = 120 + (t_idx - 1) * 76
        draw.rectangle([bx, 518, bx + 74, 644], fill=(185, 192, 202) if t_idx % 2 == 0 else (175, 182, 192), outline=(130, 140, 150))
        draw.text((bx + 26, 525), str(t_idx), fill=(40, 48, 58), font=font_med)
        # Wire connection screw
        draw.ellipse([bx + 26, 550, bx + 48, 572], fill=(80, 90, 100))
        
        # Draw wire ferrule tag on Pin 4
        if t_idx == 4:
            ferrule_label = "X1-4" if is_corrected else "T6-12"
            ferrule_color = (255, 255, 255) if is_corrected else (255, 210, 210)
            draw.rectangle([bx + 8, 595, bx + 66, 625], fill=ferrule_color, outline=(200, 30, 30) if not is_corrected else (30, 150, 80), width=2)
            draw.text((bx + 14, 602), ferrule_label, fill=(180, 10, 10) if not is_corrected else (10, 100, 40), font=font_small)

    filename = "cabinet_corrected.jpg" if is_corrected else "cabinet_initial.jpg"
    out_path = os.path.join(SAMPLE_DIR, filename)
    img.save(out_path, "JPEG", quality=95)
    print(f"Generated Cabinet Photo ({filename}): {out_path}")

def run_generate_all():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    generate_excel_wire_list()
    generate_blueprint_pdf()
    draw_control_panel(is_corrected=False)
    draw_control_panel(is_corrected=True)
    print("All sample data successfully created!")

if __name__ == "__main__":
    run_generate_all()
