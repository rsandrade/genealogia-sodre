#!/usr/bin/env python3
"""Transkribus HTR batch processor for genealogy images"""
import json, time, requests, os, sys, base64, glob

# Config
CREDENTIALS_FILE = '/home/hermes/genealogia/.env'
IMAGES_DIR = '/home/hermes/genealogia/data/images/fullres'
RESULTS_DIR = '/home/hermes/genealogia/data/transkribus_results'
AUTH_URL = 'https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token'
LEGACY_API = 'https://transkribus.eu/TrpServer/rest'

os.makedirs(RESULTS_DIR, exist_ok=True)

def load_credentials():
    creds = {}
    with open(CREDENTIALS_FILE) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                creds[k] = v
    return creds.get('TK_USERNAME', ''), creds.get('TK_PASSWORD', '')

def get_token(username, password):
    r = requests.post(AUTH_URL, data={
        'grant_type': 'password',
        'client_id': 'transkribus-api-client',
        'username': username,
        'password': password
    })
    if r.status_code != 200:
        raise Exception(f"Auth failed: {r.status_code} {r.text[:200]}")
    d = r.json()
    d['expires_at'] = time.time() + d.get('expires_in', 300) - 30
    return d

def ensure_token(session_state, username, password):
    if session_state and time.time() < session_state.get('expires_at', 0):
        return session_state['access_token']
    new_token = get_token(username, password)
    session_state.clear()
    session_state.update(new_token)
    return new_token['access_token']

def api_get(endpoint, token, params=None):
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{LEGACY_API}/{endpoint}', headers=headers, params=params, timeout=30)
    return r

def api_post(endpoint, token, data=None, files=None, params=None):
    headers = {'Authorization': f'Bearer {token}'}
    if files:
        r = requests.post(f'{LEGACY_API}/{endpoint}', headers=headers, 
                          data=data, files=files, params=params, timeout=120)
    else:
        headers['Content-Type'] = 'application/json'
        r = requests.post(f'{LEGACY_API}/{endpoint}', headers=headers,
                          json=data, params=params, timeout=120)
    return r

def list_images():
    imgs = sorted(glob.glob(os.path.join(IMAGES_DIR, '*.jpg')))
    return imgs

def main():
    username, password = load_credentials()
    if not username or not password:
        print("ERROR: Credentials not found in .env")
        sys.exit(1)
    
    session = {}
    token = ensure_token(session, username, password)
    print(f"Authenticated as {username}")
    
    # Step 1: List collections
    r = api_get('collections', token)
    if r.status_code != 200:
        print(f"ERROR listing collections: {r.status_code}")
        sys.exit(1)
    
    cols = r.json()
    cols_list = cols.get('trpCollection', cols) if isinstance(cols, dict) else cols
    print(f"\nCollections ({len(cols_list)}):")
    target_col = None
    for c in cols_list:
        cid = c.get('colId', c.get('collectionId', '?'))
        name = c.get('colName', c.get('name', '?'))
        role = c.get('role', '?')
        ndocs = c.get('nrOfDocuments', '?')
        print(f"  ID={cid} | name={name} | role={role} | docs={ndocs}")
        if 'APEB' in name.upper() or 'genealogia' in name.lower() or 'sodre' in name.lower():
            target_col = cid
    
    # Use "Teste APEB" (224656) as default
    if not target_col:
        target_col = 224656
    print(f"\nUsing collection: {target_col}")
    
    # Step 2: List images to process
    images = list_images()
    print(f"\nImages to process: {len(images)}")
    
    # Step 3: Upload first image and test HTR
    test_img = images[0]
    img_name = os.path.basename(test_img)
    print(f"\nTesting with: {img_name}")
    print(f"File size: {os.path.getsize(test_img)} bytes")
    
    # Upload image to collection
    token = ensure_token(session, username, password)
    with open(test_img, 'rb') as f:
        files = {'file': (img_name, f, 'image/jpeg')}
        r = api_post(f'collections/{target_col}/documents/upload', token, 
                     files=files, data={'title': img_name.replace('.jpg','')})
    
    print(f"Upload response: {r.status_code}")
    resp_text = r.text[:1000]
    print(f"Response: {resp_text}")
    
    if r.status_code in [200, 201]:
        doc_data = r.json()
        doc_id = doc_data.get('docId') or doc_data.get('documentId')
        print(f"Document uploaded! docId={doc_id}")
        
        # Step 4: Run HTR recognition on the document
        # Need to find available HTR models
        token = ensure_token(session, username, password)
        r2 = api_get(f'collections/{target_col}/list', token)
        docs = r2.json()
        print(f"\nDocuments in collection: {len(docs)}")
        for d in docs[:5]:
            did = d.get('docId', '?')
            title = d.get('title', '?')
            pages = d.get('nrOfPages', '?')
            print(f"  docId={did} | title={title} | pages={pages}")
    else:
        print("Upload failed. Trying alternative upload endpoint...")
        # Try multipart form upload
        token = ensure_token(session, username, password)
        with open(test_img, 'rb') as f:
            r3 = requests.post(
                f'{LEGACY_API}/collections/{target_col}/document/upload',
                headers={'Authorization': f'Bearer {token}'},
                files={'img': (img_name, f, 'image/jpeg')},
                timeout=60
            )
        print(f"Alt upload: {r3.status_code}")
        print(f"Response: {r3.text[:500]}")
    
    # Step 5: Check available HTR models
    token = ensure_token(session, username, password)
    r4 = api_get('models/htr', token)
    print(f"\nHTR models response: {r4.status_code}")
    if r4.status_code == 200:
        models = r4.json()
        if isinstance(models, list):
            print(f"Available HTR models: {len(models)}")
            for m in models[:10]:
                mid = m.get('modelId', m.get('id', '?'))
                mname = m.get('name', '?')
                lang = m.get('language', m.get('lang', '?'))
                print(f"  modelId={mid} | name={mname} | lang={lang}")
        else:
            print(f"Models data: {str(models)[:500]}")
    else:
        print(f"No models endpoint. Trying /recognition/models...")
        r5 = api_get('recognition/models', token)
        print(f"  Status: {r5.status_code}")
        if r5.status_code == 200:
            print(f"  Response: {r5.text[:500]}")

if __name__ == '__main__':
    main()