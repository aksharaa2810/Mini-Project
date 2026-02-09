# test_od_data.py
import pandas as pd
import json

# Read CSV
df = pd.read_csv('data/od_requests.csv')

# Fill NaN
df = df.fillna('')

# Convert to dict
data = df.to_dict('records')

# Try to convert to JSON
try:
    json_str = json.dumps(data[0])
    print("✅ JSON conversion successful")
    print(json_str)
except Exception as e:
    print(f"❌ JSON conversion failed: {e}")