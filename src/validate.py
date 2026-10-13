import json
import csv
from pathlib import Path
from collections import Counter

RAW_DIR = Path("data/raw")
EVENTS_DIR = RAW_DIR / "events"
REPORT_DIR = Path("data/processed")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FIELDS = [
    "id",
    "index",
    "period",
    "timestamp",
    "minute",
    "second",
    "type",
    "team",
    "possession",
    "possession_team"
]


def validate_events(match_id, events):
    missing_fields = Counter()
    event_types = Counter()
    event_ids = set()
    duplicate_ids = 0

    for event in events:
        for field in REQUIRED_FIELDS:
            if field not in event or event[field] is None:
                missing_fields[field] += 1

        event_type = event.get("type", {}).get("name", "Unknown")
        event_types[event_type] += 1

        event_id = event.get("id")

        if event_id is not None:
            if event_id in event_ids:
                duplicate_ids += 1
            event_ids.add(event_id)

    return {
        "match_id": match_id,
        "event_count": len(events),
        "duplicate_event_ids": duplicate_ids,
        "missing_fields": dict(missing_fields),
        "passes": event_types["Pass"],
        "carries": event_types["Carry"],
        "shots": event_types["Shot"]
    }


def main():
    with (RAW_DIR / "matches.json").open(
        "r", encoding="utf-8"
    ) as file:
        matches = json.load(file)

    results = []
    failed_files = []

    for match in matches:
        match_id = match["match_id"]
        event_file = EVENTS_DIR / f"{match_id}.json"

        try:
            with event_file.open("r", encoding="utf-8") as file:
                events = json.load(file)

            if not isinstance(events, list) or not events:
                raise ValueError("Empty or invalid event list")

            results.append(validate_events(match_id, events))

        except (OSError, json.JSONDecodeError, ValueError) as error:
            failed_files.append((match_id, str(error)))
            print(f"Failed: {match_id} - {error}")

    report_path = REPORT_DIR / "data_quality_report.csv"

    with report_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "match_id",
            "event_count",
            "duplicate_event_ids",
            "missing_fields",
            "passes",
            "carries",
            "shots"
        ])

        for result in results:
            writer.writerow([
                result["match_id"],
                result["event_count"],
                result["duplicate_event_ids"],
                json.dumps(result["missing_fields"]),
                result["passes"],
                result["carries"],
                result["shots"]
            ])

    print("\n--- DATA VALIDATION SUMMARY ---")
    print(f"Expected matches: {len(matches)}")
    print(f"Validated matches: {len(results)}")
    print(f"Failed files: {len(failed_files)}")
    print(
        f"Total events: "
        f"{sum(r['event_count'] for r in results):,}"
    )
    print(
        f"Duplicate event IDs: "
        f"{sum(r['duplicate_event_ids'] for r in results)}"
    )
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()