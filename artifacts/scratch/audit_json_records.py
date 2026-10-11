import os
import glob
import json

def audit_json_records():
    json_files = glob.glob('**/*.json', recursive=True)
    records = []
    for fpath in json_files:
        if 'node_modules' in fpath or '.git' in fpath or '.gemini' in fpath:
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                content_str = json.dumps(data)
                if 'sensitivity' in content_str.lower() or '82.44' in content_str or '79.93' in content_str or '230' in content_str or '223' in content_str:
                    records.append({
                        'filepath': fpath,
                        'keys': list(data.keys()) if isinstance(data, dict) else 'list',
                        'has_8244': '82.44' in content_str or '0.8244' in content_str,
                        'has_7993': '79.93' in content_str or '0.7993' in content_str,
                        'has_230': '230' in content_str,
                        'has_223': '223' in content_str
                    })
        except Exception as e:
            pass
    print(f"Audit of JSON files found {len(records)} relevant files:")
    for r in records:
        print(f"File: {r['filepath']}")
        print(f"  has_8244={r['has_8244']}, has_7993={r['has_7993']}, has_230={r['has_230']}, has_223={r['has_223']}")

if __name__ == '__main__':
    audit_json_records()
