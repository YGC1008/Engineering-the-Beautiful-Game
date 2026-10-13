import json
from pathlib import Path
from urllib.request import urlopen

BASE_URL = "https://raw.githubusercontent.com/hudl/open-data/master/data"
RAW_DIR = Path("data/raw")

RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_json(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(url, timeout=60) as response:
        data = json.load(response)

    with destination.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print(f"Saved: {destination}")
    return data


# Step 1: Download the season's match metadata
matches = download_json(
    f"{BASE_URL}/matches/2/27.json",
    RAW_DIR / "matches.json"
)

print(f"Matches listed: {len(matches)}")

# Step 2: Download events for all matches

successful = 0
failed = []

for index, match in enumerate(matches, start=1):
    match_id = match["match_id"]
    destination = RAW_DIR / "events" / f"{match_id}.json"

    # Skip matches already downloaded
    if destination.exists():
        print(f"[{index}/{len(matches)}] Already downloaded: {match_id}")
        successful += 1
        continue

    try:
        download_json(
            f"{BASE_URL}/events/{match_id}.json",
            destination
        )
        successful += 1
    except Exception as error:
        print(f"Failed to download match {match_id}: {error}")
        failed.append(match_id)

print(f"\nSuccessful: {successful}/{len(matches)}")
print(f"Failed: {len(failed)}")
print(f"Failed match IDs: {failed}")