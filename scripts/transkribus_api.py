#!/usr/bin/env python3
"""Transkribus API client for genealogia project"""
import json, os, sys, time, requests

TOKEN_FILE = '/home/hermes/genealogia/data/.transkribus_tokens.json'
CREDENTIALS = {
    'username': os.environ.get('TK_USERNAME', ''),
    'password': os.environ.get('TK_PASSWORD', ''),
}

AUTH_URL = 'https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token'
API_BASE = 'https://transkribus.eu/TrpServer/rest'

def get_token():
    """Get or refresh access token"""
    # Try loading existing token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        # Check if token is still valid (with 30s margin)
        if data.get('expires_at', 0) > time.time() + 30:
            return data['access_token']
        # Try refresh
        if 'refresh_token' in data:
            try:
                r = requests.post(AUTH_URL, data={
                    'grant_type': 'refresh_token',
                    'client_id': 'transkribus-api-client',
                    'refresh_token': data['refresh_token']
                })
                if r.status_code == 200:
                    new_data = r.json()
                    new_data['expires_at'] = time.time() + new_data.get('expires_in', 300)
                    with open(TOKEN_FILE, 'w') as f:
                        json.dump(new_data, f)
                    os.chmod(TOKEN_FILE, 0o600)
                    return new_data['access_token']
            except:
                pass
    
    # Fresh login
    r = requests.post(AUTH_URL, data={
        'grant_type': 'password',
        'client_id': 'transkribus-api-client',
        'username': CREDENTIALS['username'],
        'password': CREDENTIALS['password']
    })
    if r.status_code != 200:
        raise Exception(f"Auth failed: {r.status_code} {r.text[:200]}")
    
    data = r.json()
    data['expires_at'] = time.time() + data.get('expires_in', 300)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f)
    os.chmod(TOKEN_FILE, 0o600)
    return data['access_token']

def api_get(endpoint, params=None):
    """Make authenticated GET request to Transkribus API"""
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE}/{endpoint}'
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 401:
        # Token expired, retry with fresh one
        os.remove(TOKEN_FILE)
        token = get_token()
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(url, headers=headers, params=params)
    return r

def list_collections():
    """List user's collections"""
    r = api_get('collections')
    if r.status_code != 200:
        return f"Error: {r.status_code} {r.text[:200]}"
    data = r.json()
    result = [f"Collections: {len(data)}"]
    for c in data[:30]:
        cid = c.get('collectionId', '?')
        name = c.get('name', '?')
        role = c.get('role', '?')
        ndocs = c.get('nrOfDocuments', '?')
        result.append(f"  ID={cid} | name={name} | role={role} | docs={ndocs}")
    return '\n'.join(result)

def search_fulltext(query, collection_id=None, search_type='LinesLc'):
    """Search full-text across collections"""
    params = {'query': query, 'type': search_type}
    if collection_id:
        params['filter'] = f'collectionId:{collection_id}'
    r = api_get('search/fulltext', params=params)
    if r.status_code != 200:
        return f"Error: {r.status_code} {r.text[:200]}"
    return r.json()

def list_documents(collection_id, start=0, max_results=50):
    """List documents in a collection"""
    r = api_get(f'collections/{collection_id}/list', params={'start': start, 'maxResults': max_results})
    if r.status_code != 200:
        return f"Error: {r.status_code} {r.text[:200]}"
    return r.json()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Transkribus API client')
    parser.add_argument('--action', default='collections', choices=['collections', 'search', 'docs', 'upload'])
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--collection-id', type=int, help='Collection ID')
    parser.add_argument('--username', help='Transkribus username')
    parser.add_argument('--password', help='Transkribus password')
    args = parser.parse_args()
    
    if args.username:
        CREDENTIALS['username'] = args.username
    if args.password:
        CREDENTIALS['password'] = args.password
    
    # Also try from env or .env file
    if not CREDENTIALS['username']:
        env_file = '/home/hermes/genealogia/.env'
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith('TK_USERNAME='):
                        CREDENTIALS['username'] = line.strip().split('=',1)[1]
                    elif line.startswith('TK_PASSWORD='):
                        CREDENTIALS['password'] = line.strip().split('=',1)[1]
    
    if args.action == 'collections':
        print(list_collections())
    elif args.action == 'search':
        if not args.query:
            print("Error: --query required for search")
            sys.exit(1)
        result = search_fulltext(args.query, args.collection_id)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])
    elif args.action == 'docs':
        if not args.collection_id:
            print("Error: --collection-id required for docs")
            sys.exit(1)
        result = list_documents(args.collection_id)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])