from ddgs import DDGS
import sys

print("Testing DuckDuckGo Search API (using new ddgs package)...")

try:
    with DDGS() as ddgs:
        print("Initialised DDGS client.")
        results = ddgs.text("Cucumber", max_results=5)
        print(f"Results type: {type(results)}")
        print(f"Raw results content: {results}")
        
        results_list = list(results)
        print(f"Extracted list length: {len(results_list)}")
        for idx, r in enumerate(results_list):
            print(f"Result {idx+1}: {r.get('href')}")
            
except Exception as e:
    import traceback
    print(f"Error encountered: {e}")
    traceback.print_exc()

print("Test finished.")
