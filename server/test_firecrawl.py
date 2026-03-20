"""
Test Firecrawl Search API with real queries for all scenarios.
Validates that our query patterns return useful results.

Usage: python test_firecrawl.py
Requires: FIRECRAWL_API_KEY in .env or environment
"""

import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from firecrawl import FirecrawlApp

API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
if not API_KEY:
    print("ERROR: FIRECRAWL_API_KEY not set")
    exit(1)

fc = FirecrawlApp(api_key=API_KEY)

QUERIES = {
    "Mechanic": [
        "2019 Toyota Camry brake pads rotors replacement cost",
        "auto repair shops Sacramento California reviews",
        "2019 Toyota Camry brake recall NHTSA",
    ],
    "Landlord": [
        "California security deposit return deadline law",
        "California security deposit penalty landlord violation Civil Code 1950.5",
        "California civil code 1950.5 text",
    ],
    "Salary": [
        "marketing manager salary Sacramento site:glassdoor.com",
        "marketing manager salary California 4 years experience",
        "marketing manager Sacramento job openings salary 2026",
    ],
}

results_log = []

for scenario, queries in QUERIES.items():
    print(f"\n{'='*60}")
    print(f"  SCENARIO: {scenario}")
    print(f"{'='*60}")

    for query in queries:
        print(f"\n  Query: {query}")
        print(f"  {'-'*50}")
        try:
            result = fc.search(
                query=query,
                limit=3,
                scrape_options={"formats": ["markdown"]},
            )

            # SearchData has .web (list of SearchResultWeb)
            if hasattr(result, "web") and result.web:
                items = result.web
            elif hasattr(result, "data") and result.data:
                items = result.data
            elif isinstance(result, list):
                items = result
            else:
                items = []

            print(f"  Results: {len(items)}")
            entry = {"scenario": scenario, "query": query, "count": len(items), "results": []}

            for i, item in enumerate(items[:3]):
                if isinstance(item, dict):
                    title = item.get("title", item.get("metadata", {}).get("title", "N/A"))
                    url = item.get("url", "N/A")
                    content = item.get("markdown", item.get("content", item.get("description", "")))
                    snippet = content[:200] if content else "N/A"
                else:
                    title = getattr(item, "title", "N/A")
                    url = getattr(item, "url", "N/A")
                    content = getattr(item, "markdown", getattr(item, "content", ""))
                    snippet = content[:200] if content else "N/A"

                print(f"\n    [{i+1}] {title}")
                print(f"        URL: {url}")
                print(f"        Snippet: {snippet}...")
                entry["results"].append({"title": title, "url": url, "snippet": snippet})

            results_log.append(entry)

        except Exception as e:
            print(f"  ERROR: {e}")
            results_log.append({"scenario": scenario, "query": query, "count": 0, "error": str(e)})

# Summary
print(f"\n\n{'='*60}")
print(f"  SUMMARY")
print(f"{'='*60}")
for entry in results_log:
    status = "OK" if entry.get("count", 0) > 0 else "FAIL"
    count = entry.get("count", 0)
    print(f"  [{status}] ({count} results) {entry['query']}")

# Save results as JSON for analysis
output_path = os.path.join(os.path.dirname(__file__), "firecrawl_test_results.json")
with open(output_path, "w") as f:
    json.dump(results_log, f, indent=2)
print(f"\nFull results saved to {output_path}")
