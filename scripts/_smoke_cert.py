import time
import requests

url = 'http://127.0.0.1:8001/api/certificates'
payload = {"name":"Test Cert","issuer":"CA","serial":"SN-TEST-0001","description":"auto test"}

try:
    # allow a short warmup
    time.sleep(1)
    r = requests.post(url, json=payload, timeout=5)
    print('POST', r.status_code)
    try:
        print(r.text)
    except Exception:
        pass
    r2 = requests.get(url, timeout=5)
    print('GET', r2.status_code)
    try:
        print(r2.text)
    except Exception:
        pass
except Exception as e:
    print('ERROR', e)
