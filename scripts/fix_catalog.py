import json
import re

with open("data/catalog.json", "rb") as f:
    raw = f.read()

# Decode bytes, ignore bad chars
text = raw.decode("utf-8", errors="ignore")

# Use strict=False to allow control characters
decoder = json.JSONDecoder(strict=False)
data = decoder.decode(text)

print(f"Type: {type(data)}")
if isinstance(data, list):
    print(f"Total items: {len(data)}")
    print("First item keys:", list(data[0].keys()))
    print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500])
elif isinstance(data, dict):
    print(f"Top level keys: {list(data.keys())[:5]}")
    # Get first nested item
    first_val = list(data.values())[0]
    if isinstance(first_val, list):
        print(f"Total items: {len(first_val)}")
        print("First item:", json.dumps(first_val[0], indent=2)[:500])

# Save clean version
with open("data/catalog.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nFixed and saved ✅")