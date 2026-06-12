#!/usr/bin/env python3
"""Transkribus Metagrapho HTR processor - batch for genealogy images"""
import json, time, os, sys
from pathlib import Path
from transkribus_metagrapho_api import transkribus_metagrapho_api

# Load credentials
env = {}
with open('/home/hermes/genealogia/.env') as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

IMAGES_DIR = Path('/home/hermes/genealogia/data/images/fullres')
RESULTS_DIR = Path('/home/hermes/genealogia/data/transkribus_results')
RESULTS_DIR.mkdir(exist_ok=True)

# HTR models to try
HTR_MODELS = {
    'portuguese_16_19': 53270,       # Portuguese Handwriting 16th-19th c.
    'portuguese_m2': 45090,           # Transkribus portuguese handwriting M2
    'brazilian_19th': 272569,         # Brazilian 19th Century Handwritten Documents
    'text_titan': 51170,              # The Text Titan I (Super Model)
    'western_sephardic': 412437,      # Western Sephardic Diaspora 1.2 (1676-1800) - por/spa/eng
}
LINE_DETECTION = 49272  # default

# Get images to process
images = sorted(IMAGES_DIR.glob('*.jpg'))
print(f"Found {len(images)} images to process")

# Process first image as test
test_img = images[0]
print(f"\nTest image: {test_img.name} ({test_img.stat().st_size / 1024:.0f} KB)")
print(f"Using model: Portuguese Handwriting 16th-19th c. (ID={HTR_MODELS['portuguese_16_19']})")

try:
    with transkribus_metagrapho_api(env['TK_USERNAME'], env['TK_PASSWORD']) as api:
        print("Authenticated with Metagrapho!")
        
        # Process test image
        process_id = api.process(str(test_img), line_detection=LINE_DETECTION, htr_id=HTR_MODELS['portuguese_16_19'])
        print(f"Process submitted! ID={process_id}")
        
        # Poll for completion
        max_wait = 600  # 10 minutes
        start = time.time()
        while time.time() - start < max_wait:
            status = api.status(process_id)
            elapsed = time.time() - start
            print(f"  [{elapsed:.0f}s] Status: {status}")
            
            if status.upper() == 'FINISHED':
                print(f"\nHTR completed after {elapsed:.0f}s!")
                
                # Get PAGE XML
                page_xml = api.page(process_id)
                
                # Save PAGE XML
                xml_out = RESULTS_DIR / f'{test_img.stem}_page.xml'
                with open(xml_out, 'w', encoding='utf-8') as f:
                    f.write(page_xml)
                print(f"PAGE XML saved: {xml_out}")
                
                # Extract plain text from PAGE XML
                from lxml import etree
                doc = etree.fromstring(page_xml.encode('utf-8'))
                lines = doc.xpath('//TextLine/Unicode/text()')
                plain_text = '\n'.join(lines)
                
                txt_out = RESULTS_DIR / f'{test_img.stem}.txt'
                with open(txt_out, 'w', encoding='utf-8') as f:
                    f.write(plain_text)
                print(f"Plain text saved: {txt_out} ({len(plain_text)} chars)")
                
                # Search for Sodré/Gramilo
                text_lower = plain_text.lower()
                for kw in ['sodré', 'sodore', 'gramilo', 'gramilho', 'pereira', 'jerônimo', 'tomaz', 'francisco']:
                    if kw in text_lower:
                        print(f"  *** FOUND: '{kw}' ***")
                
                print(f"\n=== TRANSCRIPTION ===")
                print(plain_text[:3000])
                break
                
            elif status.upper() == 'FAILED':
                print("HTR FAILED!")
                break
            
            time.sleep(15)
        else:
            print(f"Timeout after {max_wait}s")
            
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()