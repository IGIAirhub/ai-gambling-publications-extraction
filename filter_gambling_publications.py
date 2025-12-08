import pyalex
from pyalex import Works
import json

# Read the JSON file
with open('classifier_results.json', 'r') as f:
    data = json.load(f)

# Filter entries containing "artificial intelligence" or "machine learning"
filtered_ids = []

for url, keywords in data.items():
    if "artificial intelligence" in keywords or "machine learning" in keywords:
        work_id = url.split('/')[-1]
        filtered_ids.append(work_id)

# Save filtered IDs to a new file for future use
with open('filtered_ids.json', 'w') as f:
    json.dump(filtered_ids, f, indent=2)

works_data = {}

# Process each work ID
for work_id in filtered_ids:
    # Fetch the work
    work = Works()[work_id]
    
    # Extract the specific fields
    works_data[work_id] = {
        "id": work.get("id"),
        "doi": work.get("doi"),
        "display_name": work.get("display_name"),
        "publication_year": work.get("publication_year"),
        "institutions": list({
            inst.get("id"): {
                "id": inst.get("id"),
                "display_name": inst.get("display_name"),
                "country_code": inst.get("country_code")
            }
            for authorship in work.get("authorships", [])
            for inst in authorship.get("institutions", [])
        }.values()),
        "cited_by_count": work.get("cited_by_count")
    }
        
    print(f"Processed: {work_id}")

# Save to JSON file
with open('filtered_works.json', 'w', encoding='utf-8') as f:
    json.dump(works_data, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete. Processed {len(works_data)} works.")
print("Data saved to 'filtered_works.json'")


    
