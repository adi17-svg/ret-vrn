import json
import time
from openai import OpenAI

A4F_KEY = "YOUR_A4F_API_KEY"  # ← replace this with your real A4F key

ENDPOINTS = [
    "https://api.a4f.co/v1",
    "https://a4f.ai/api/v1",
    "https://api.a4f.ai/v1",
]

MODELS = [
    "provider-5/gpt-5-nano",
    "provider-1/chatgpt-4o-latest",
    "provider-2/gpt-4.1",
]

def test_endpoint(base_url):
    print(f"\n🔍 Testing {base_url}")
    client = OpenAI(api_key=A4F_KEY, base_url=base_url)
    for model in MODELS:
        try:
            start = time.time()
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello from A4F test"}]
            )
            elapsed = time.time() - start
            print(f"✅ {model} responded in {elapsed:.2f}s")
            print("   →", json.dumps(resp.choices[0].message.content, indent=2))
        except Exception as e:
            print(f"❌ {model} failed → {e}")

def main():
    for endpoint in ENDPOINTS:
        test_endpoint(endpoint)

if __name__ == "__main__":
    main()
