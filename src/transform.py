import csv
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
EVENTS_DIR = RAW_DIR / "events"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def transform_matches(matches):
    rows = []

    for match in matches:
        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_score > away_score:
            home_result = "Win"
            away_result = "Loss"
        elif home_score < away_score:
            home_result = "Loss"
            away_result = "Win"
        else:
            home_result = "Draw"
            away_result = "Draw"

        rows.append({
            "match_id": match["match_id"],
            "match_date": match["match_date"],
            "home_team_id": match["home_team"]["home_team_id"],
            "home_team": match["home_team"]["home_team_name"],
            "away_team_id": match["away_team"]["away_team_id"],
            "away_team": match["away_team"]["away_team_name"],
            "home_score": home_score,
            "away_score": away_score,
            "home_result": home_result,
            "away_result": away_result
        })

    return rows


def transform_events(match_id, events):
    rows = []

    for event in events:
        event_type = event.get("type", {}).get("name")
        location = event.get("location") or [None, None]

        pass_data = event.get("pass") or {}
        carry_data = event.get("carry") or {}
        shot_data = event.get("shot") or {}

        end_location = (
            pass_data.get("end_location")
            or carry_data.get("end_location")
            or [None, None]
        )

        rows.append({
            "match_id": match_id,
            "event_id": event.get("id"),
            "event_index": event.get("index"),
            "period": event.get("period"),
            "minute": event.get("minute"),
            "second": event.get("second"),
            "event_type": event_type,
            "team_id": (event.get("team") or {}).get("id"),
            "team_name": (event.get("team") or {}).get("name"),
            "player_id": (event.get("player") or {}).get("id"),
            "possession": event.get("possession"),
            "possession_team_id": (
                event.get("possession_team") or {}
            ).get("id"),
            "start_x": location[0] if len(location) > 0 else None,
            "start_y": location[1] if len(location) > 1 else None,
            "end_x": (
                end_location[0] if len(end_location) > 0 else None
            ),
            "end_y": (
                end_location[1] if len(end_location) > 1 else None
            ),
            "pass_outcome": (
                (pass_data.get("outcome") or {}).get("name")
            ),
            "pass_length": pass_data.get("length"),
            "pass_angle": pass_data.get("angle"),
            "shot_outcome": (
                (shot_data.get("outcome") or {}).get("name")
            ),
            "shot_xg": shot_data.get("statsbomb_xg")
        })

    return rows


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows to write: {path}")

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    with (RAW_DIR / "matches.json").open(
        "r", encoding="utf-8"
    ) as file:
        matches = json.load(file)

    match_rows = transform_matches(matches)
    write_csv(PROCESSED_DIR / "matches.csv", match_rows)

    event_path = PROCESSED_DIR / "events.csv"

    event_count = 0

    with event_path.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = None

        for index, match in enumerate(matches, start=1):
            match_id = match["match_id"]
            source = EVENTS_DIR / f"{match_id}.json"

            with source.open("r", encoding="utf-8") as file:
                events = json.load(file)

            rows = transform_events(match_id, events)

            if rows:
                if writer is None:
                    writer = csv.DictWriter(
                        output, fieldnames=rows[0].keys()
                    )
                    writer.writeheader()

                writer.writerows(rows)
                event_count += len(rows)

            print(
                f"[{index}/{len(matches)}] "
                f"Transformed match {match_id}"
            )

    print("\n--- TRANSFORMATION SUMMARY ---")
    print(f"Matches transformed: {len(match_rows)}")
    print(f"Events transformed: {event_count:,}")
    print(f"Saved: {PROCESSED_DIR / 'matches.csv'}")
    print(f"Saved: {event_path}")


if __name__ == "__main__":
    main()