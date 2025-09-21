import time
import json
import os
from configurations import SPECIFICATION_LOCATION

print("Dummy script started.")

# Read configurations
try:
    print("Configurations loaded.")
    print(f"SPECIFICATION_LOCATION: {SPECIFICATION_LOCATION}")
except ImportError:
    print("Could not import configurations.")

# Simulate progress
for i in range(10):
    print(f"Progress: {i * 10}%")
    time.sleep(1)

# Create dummy output files
report = {"summary": {"requests_sent": 100, "errors": 5}}
with open("report.json", "w") as f:
    json.dump(report, f)

results = {
    "results": [
        {"request": "...", "response": "..."},
        {"request": "...", "response": "..."},
    ]
}
with open("results.json", "w") as f:
    json.dump(results, f)

print("Dummy script finished.")
