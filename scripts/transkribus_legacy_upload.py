#!/usr/bin/env python3
"""Transkribus Legacy API — Upload + HTR for genealogy images"""
import json, time, requests, os, sys, glob
from pathlib import Path
from lxml import etree

# Load credentials from .env
def load_env(path):
    creds = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                creds[k.strip()] = v.strip()
    return creds

env = load_env('/home/hermes/genealogia/.env')
USERNAME = env.get('TK_USERNAME', '')
PASSWORD = env.get('TK_PASSWORD', '')

if not USERNAME or not PASSWORD:
    print("ERROR: Credentials missing in .env")
    sys.exit(1)

API = 'https://transkribus.eu/TrpServer/rest'
COL_ID = 224656  # "Teste APEB"
IMG_DIR = '/home/hermes/genealogia/data/images/fullres'
RESULTS_DIR = '/home/hermes/genealogia/data/transkribus_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

# Step 1: Login (legacy — returns JSESSIONID)
print("Step 1: Logging in...")
r = requests.post(f'{API}/auth/login', data={'user': USERNAME, 'pw': PASSWORD}, timeout=30)
if r.status_code != 200:
    print(f"Login failed: {r.status_code}")
    sys.exit(1)

doc = etree.fromstring(r.content)
session_id = doc.xpath('//sessionId/text()')[0]
print(f"Logged in! JSESSIONID={session_id[:10]}...")
cookie = {'Cookie': f'JSESSIONID={session_id}'}

# Step 2: List HTR models
print("\nStep 2: Finding HTR models...")
r2 = requests.get(f'{API}/models/htr', headers=cookie, timeout=15)
print(f"Models endpoint: {r2.status_code}")
if r2.status_code == 200:
    try:
        models_data = r2.json()
    except:
        from lxml import etree as et2
        models_data = None
        try:
            models_doc = et2.fromstring(r2.content)
            print("(XML response)")
        except:
            print(f"Raw response: {r2.text[:300]}")
    
    if models_data:
        if isinstance(models_data, dict):
            total = models_data.get('total', '??')
            models = models_data.get('trpModelMetadata', [])
            print(f"Total models: {total} (returned: {len(models)})")
            for m in models[:20]:
                mid = m.get('modelId', '?')
                name = m.get('name', '?')
                lang = m.get('language', '?')
                mtype = m.get('type', '?')
                print(f"  ID={mid} type={mtype} name={name} lang={lang}")
        elif isinstance(models_data, list):
            print(f"Models list: {len(models_data)}")
            for m in models_data[:20]:
                print(f"  {m}")
else:
    print(f"Error: {r2.text[:300]}")

# Step 3: Upload test image
test_img = os.path.join(IMG_DIR, '33SQ-GY3G-6TN.jpg')
img_name = os.path.basename(test_img)
print(f"\nStep 3: Uploading {img_name}...")

# 3a: Create upload structure
data = {
    "md": {"title": f"Genealogia {img_name.replace('.jpg','')}"},
    "pageList": {
        "pages": [{
            "fileName": img_name,
            "pageXmlName": None,
            "pageNr": 1,
        }]
    }
}
r3 = requests.post(f'{API}/uploads', headers=cookie, 
                   params={'collId': COL_ID}, json=data, timeout=60)
print(f"Create upload: {r3.status_code}")
if r3.status_code in [200, 201]:
    upload_doc = etree.fromstring(r3.content)
    upload_id_el = upload_doc.xpath('//uploadId/text()')
    if upload_id_el:
        upload_id = int(upload_id_el[0])
        print(f"Upload ID: {upload_id}")
        
        # 3b: Upload image file
        with open(test_img, 'rb') as f:
            r4 = requests.put(f'{API}/uploads/{upload_id}', headers=cookie,
                             files={'img': (img_name, f, 'image/jpeg')}, timeout=120)
        print(f"Image upload: {r4.status_code}")
        print(f"Response: {r4.text[:300]}")
        
        if r4.status_code in [200, 201]:
            # Get job status
            r5 = requests.get(f'{API}/uploads/{upload_id}', headers=cookie, timeout=15)
            print(f"Upload status: {r5.status_code}")
            if r5.status_code == 200:
                status_doc = etree.fromstring(r5.content)
                job_id = status_doc.xpath('//jobId/text()')
                doc_id = status_doc.xpath('//docId/text()')
                print(f"Job ID: {job_id[0] if job_id else '?'}")
                print(f"Doc ID: {doc_id[0] if doc_id else '?'}")
    else:
        print(f"No uploadId in response: {r3.text[:300]}")
else:
    print(f"Error: {r3.text[:300]}")

# Step 4: List documents in collection
print(f"\nStep 4: Documents in collection {COL_ID}...")
r6 = requests.get(f'{API}/collections/{COL_ID}/list', headers=cookie, timeout=15)
if r6.status_code == 200:
    docs_doc = etree.fromstring(r6.content)
    docs = docs_doc.xpath('//trpDocMetadata')
    print(f"Documents: {len(docs)}")
    for d in docs[:10]:
        did = d.xpath('./docId/text()')
        title = d.xpath('./title/text()')
        pages = d.xpath('./nrOfPages/text()')
        print(f"  docId={did[0] if did else '?'} title={title[0] if title else '?'} pages={pages[0] if pages else '?'}")
else:
    print(f"Error: {r6.status_code}")

print("\nDone!")