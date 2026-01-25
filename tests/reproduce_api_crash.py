
import requests
import sys

def test_api_trades_endpoint():
    try:
        url = "http://localhost:8000/api/stats/trades"
        print(f"Testing URL: {url}")
        
        response = requests.get(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ TEST PASSED: Endpoint returned 200 OK")
            sys.exit(0)
        else:
            print(f"❌ TEST FAILED: Expected 200 OK, got {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ TEST FAILED: Exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api_trades_endpoint()
