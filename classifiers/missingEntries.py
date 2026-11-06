import json
import argparse

# Filenames
parser = argparse.ArgumentParser(description='Stage 2 check: list ids marked true in --master that are absent from --results.')
parser.add_argument("--master", default="master_ai_classification.json", help="classifier output {id: bool} (default: %(default)s)")
parser.add_argument("--results", default="attempt_2_postAIClassifcation.json", help="post-fetch output {id: {title, abstract}} (default: %(default)s)")
parser.add_argument("--output", default="missing_entries.json", help="list of missing ids (default: %(default)s)")
args = parser.parse_args()

MASTER_FILE = args.master
RESULTS_FILE = args.results
MISSING_OUT_FILE = args.output

def find_missing():
    # 1. Load the Master List and filter for True entries
    print(f"Loading {MASTER_FILE}...")
    with open(MASTER_FILE, 'r') as f:
        master_data = json.load(f)
    
    # These are the URLs we expected to have in the final output
    expected_urls = {url for url, status in master_data.items() if status is True}
    
    # 2. Load the Results List
    print(f"Loading {RESULTS_FILE}...")
    try:
        with open(RESULTS_FILE, 'r') as f:
            results_data = json.load(f)
        actual_urls = set(results_data.keys())
    except FileNotFoundError:
        print(f"Error: {RESULTS_FILE} not found.")
        return

    # 3. Identify the gap
    missing_urls = expected_urls - actual_urls
    
    # 4. Report results
    print("-" * 30)
    print(f"Expected (True): {len(expected_urls)}")
    print(f"Actual (Found):  {len(actual_urls)}")
    print(f"Missing count:   {len(missing_urls)}")
    print("-" * 30)

    if missing_urls:
        print("\nMissing URLs list:")
        for url in sorted(list(missing_urls)):
            print(url)
            
        # 5. Save missing to a file for easy re-running
        with open(MISSING_OUT_FILE, 'w') as f:
            json.dump(list(missing_urls), f, indent=2)
        print(f"\nSaved missing IDs to {MISSING_OUT_FILE}")
    else:
        print("No missing entries found!")

if __name__ == "__main__":
    find_missing()