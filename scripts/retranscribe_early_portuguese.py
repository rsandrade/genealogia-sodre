#!/usr/bin/env python3
"""Retranscribe early_portuguese_printing images using Metagrapho API
with a more appropriate HTR model for old Portuguese/Sephardic handwriting.

Uses model 412437 (Western Sephardic Diaspora 1.2 - por/spa/eng 1676-1800)
as primary, with fallback to 53270 (Portuguese Handwriting 16th-19th c.)

Runs as a background batch - saves results to /home/hermes/genealogia/data/transkribus_results/
"""
import json, time, os, sys
from pathlib import Path
from transkribus_metagrapho_api import transkribus_metagrapho_api
from lxml import etree

# Load credentials
creds = {}
with open('/home/hermes/genealogia/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            creds[k] = v

USERNAME = creds.get('TK_USERNAME', '')
PASSWORD = creds.get('TK_PASSWORD', '')

IMAGES_DIR = Path('/home/hermes/genealogia/data/images/fullres')
RESULTS_DIR = Path('/home/hermes/genealogia/data/transkribus_results/retranscription')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Mapping: page -> image file (early_portuguese_printing only)
PAGE_IMAGE_MAP = {
    'page_001': '33S7-95G9-51Y.jpg',
    'page_002': '33S7-95LB-4PL.jpg',
    'page_003': '33S7-95LT-7WF.jpg',
    'page_004': '33S7-95LT-8B.jpg',
    'page_005': '33S7-95LY-CQM.jpg',
    'page_006': '33S7-95LY-ZV9.jpg',
    'page_007': '33S7-9PXT-3J1.jpg',
    'page_008': '33S7-9RYW-5HN.jpg',
    'page_009': '33S7-9Y3K-9F8.jpg',
    'page_010': '33S7-9Y9W-BV4.jpg',
    'page_011': '33S7-9YFT-SWFC.jpg',
    'page_012': '33SQ-G5GW-NKC.jpg',
    'page_013': '33SQ-G5GX-9P62.jpg',
    'page_014': '33SQ-G5LB-725.jpg',
    'page_015': '33SQ-G5LB-7BY.jpg',
    'page_016': '33SQ-G5LB-7K4.jpg',
    'page_017': '33SQ-G5LR-8TF.jpg',
    'page_018': '33SQ-G5LY-CNB.jpg',
    'page_019': '33SQ-G5LY-DB9.jpg',
    'page_020': '33SQ-G5LY-FSR.jpg',
    'page_021': '33SQ-GR51-L7V.jpg',
    'page_022': '33SQ-GTBK-HF6.jpg',
    'page_023': '33SQ-GY3G-6TN.jpg',
    'page_024': '33SQ-GY3G-FPZ.jpg',
    'page_025': '33SQ-GYFY-J34.jpg',
    'page_026': '33SQ-GYFY-JQB.jpg',
}

# HTR Models - try Sephardic first (better for old Portuguese handwriting)
HTR_MODELS = [
    (412437, 'Western Sephardic Diaspora 1.2 (por/spa/eng 1676-1800)'),
    (53270, 'Portuguese Handwriting 16th-19th c.'),
    (45090, 'Transkribus Portuguese Handwriting M2'),
]

LINE_DETECTION = 49272  # default line detection model

def extract_text_from_page_xml(xml_content):
    """Extract plain text from PAGE XML content."""
    try:
        root = etree.fromstring(xml_content.encode('utf-8') if isinstance(xml_content, str) else xml_content)
        # Try with namespace
        ns = {'pg': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        lines = root.findall('.//pg:TextLine/pg:TextEquiv/pg:Unicode', ns)
        if not lines:
            # Try without namespace
            lines = root.findall('.//TextLine/TextEquiv/Unicode')
        if not lines:
            # Try with 2019 namespace
            ns2 = {'pg': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15'}
            lines = root.findall('.//pg:TextLine/pg:TextEquiv/pg:Unicode', ns2)
        return '\n'.join(l.text for l in lines if l.text)
    except Exception as e:
        return f"ERROR extracting text: {e}"

def main():
    print(f"=== Retranscription Batch Job ===")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Images: {len(PAGE_IMAGE_MAP)}")
    print()
    
    # Use the context manager for auth
    with transkribus_metagrapho_api(USERNAME, PASSWORD) as api:
        print("Authenticated with Metagrapho API")
        
        # Try primary model first
        htr_id, htr_name = HTR_MODELS[0]
        print(f"Using HTR model: {htr_name} (ID={htr_id})")
        
        # Submit all images for processing
        process_ids = {}
        results_log = []
        
        for page_name, img_filename in sorted(PAGE_IMAGE_MAP.items()):
            img_path = IMAGES_DIR / img_filename
            if not img_path.exists():
                print(f"  SKIP {page_name}: image not found {img_path}")
                results_log.append({'page': page_name, 'status': 'skipped', 'error': 'image not found'})
                continue
            
            try:
                pid = api.process(str(img_path), htr_id=htr_id, line_detection=LINE_DETECTION)
                process_ids[page_name] = pid
                print(f"  {page_name} -> {img_filename}: submitted (process_id={pid})")
                results_log.append({'page': page_name, 'image': img_filename, 'process_id': pid, 'status': 'submitted'})
            except Exception as e:
                print(f"  {page_name} -> {img_filename}: ERROR: {e}")
                results_log.append({'page': page_name, 'image': img_filename, 'status': 'error', 'error': str(e)})
        
        print(f"\nSubmitted {len(process_ids)}/{len(PAGE_IMAGE_MAP)} images")
        
        # Save process IDs for tracking
        ids_file = RESULTS_DIR / 'process_ids.json'
        with open(ids_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'htr_model': htr_name,
                'htr_id': htr_id,
                'process_ids': {k: v for k, v in process_ids.items()},
                'results_log': results_log
            }, f, indent=2)
        print(f"Process IDs saved to {ids_file}")
        
        # Now poll for completion
        print(f"\nPolling for results (checking every 30s, timeout 20min per image)...")
        completed = {}
        failed = {}
        
        max_total_wait = 1200  # 20 minutes total
        start_time = time.time()
        check_interval = 30
        
        while process_ids and (time.time() - start_time) < max_total_wait:
            still_pending = {}
            for page_name, pid in process_ids.items():
                try:
                    status = api.status(pid)
                    if status.upper() == 'FINISHED':
                        # Get the PAGE XML result
                        try:
                            page_xml = api.page(pid)
                            # Save PAGE XML
                            xml_path = RESULTS_DIR / f'{page_name}_retranscribed.xml'
                            with open(xml_path, 'w', encoding='utf-8') as xf:
                                xf.write(page_xml)
                            
                            # Extract and save plain text
                            text = extract_text_from_page_xml(page_xml)
                            txt_path = RESULTS_DIR / f'{page_name}_retranscribed.txt'
                            with open(txt_path, 'w', encoding='utf-8') as tf:
                                tf.write(text)
                            
                            completed[page_name] = pid
                            elapsed = time.time() - start_time
                            print(f"  [{elapsed:.0f}s] {page_name}: DONE! Text length: {len(text)} chars")
                        except Exception as e:
                            failed[page_name] = {'pid': pid, 'error': str(e)}
                            print(f"  {page_name}: finished but retrieval failed: {e}")
                    elif status.upper() == 'FAILED':
                        failed[page_name] = {'pid': pid, 'error': 'processing failed'}
                        print(f"  {page_name}: FAILED!")
                    else:
                        still_pending[page_name] = pid
                except Exception as e:
                    # If status check fails, keep trying
                    still_pending[page_name] = pid
            
            process_ids = still_pending
            if process_ids:
                time.sleep(check_interval)
        
        # Handle remaining pending items
        if process_ids:
            for page_name, pid in process_ids.items():
                print(f"  {page_name}: TIMEOUT (still pending after {max_total_wait}s)")
        
        # Final summary
        print(f"\n=== FINAL SUMMARY ===")
        print(f"Completed: {len(completed)}")
        print(f"Failed: {len(failed)}")
        print(f"Timeout/Pending: {len(process_ids)}")
        
        # Update results log
        final_results = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'htr_model': htr_name,
            'htr_id': htr_id,
            'completed': {k: v for k, v in completed.items()},
            'failed': {k: str(v) for k, v in failed.items()},
            'results_log': results_log
        }
        final_file = RESULTS_DIR / 'final_results.json'
        with open(final_file, 'w') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {final_file}")
        
        # Concatenate all completed texts
        all_texts = []
        for page_name in sorted(completed.keys()):
            txt_path = RESULTS_DIR / f'{page_name}_retranscribed.txt'
            if txt_path.exists():
                all_texts.append(f'[{page_name}]')
                all_texts.append(txt_path.read_text(encoding='utf-8'))
                all_texts.append('')
        
        if all_texts:
            combined = '\n'.join(all_texts)
            combined_path = RESULTS_DIR / 'early_portuguese_retranscribed_full.txt'
            combined_path.write_text(combined, encoding='utf-8')
            print(f"Combined text saved to {combined_path} ({len(combined)} chars)")

if __name__ == '__main__':
    main()