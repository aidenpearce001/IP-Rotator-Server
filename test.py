import requests
import json

def test_proxy():
        # Use the proxy by setting it in the 'proxies' parameter
        # Make a request to the target URL via the proxy
        response = requests.get("http://127.0.0.1:8000/proxy/?target_url=http://httpbin.org/ip")
        
        ip_info = json.loads(response.text)
        print(ip_info)
        
# Test the proxy
test_proxy()