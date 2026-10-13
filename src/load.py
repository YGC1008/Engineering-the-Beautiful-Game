import os
from pathlib import Path
import psycopg

PROCESSED_DIR = Path("data/processed")

DB_CONFIG = {
    "dbname": "engineering_the_beautiful_game",
    "user": "postgres",
    "password": os.environ["PGPASSWORD"],
    "host": "127.0.0.1",
    "port": 5432,
    "connect_timeout": 10,
}


def load_csv(cursor, table_name, filename):
    file_path = PROCESSED_DIR / filename

    print(f"Loading {filename} into {table_name}...")

    with file_path.open("r", encoding="utf-8") as file:
        with cursor.copy(
            f"COPY {table_name} FROM STDIN "
            "WITH (FORMAT CSV, HEADER TRUE)"
        ) as copy:
            while chunk := file.read(1024 * 1024):
                copy.write(chunk)

    print(f"Finished loading {table_name}.")


def main():
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:

            # Clear existing data so the load can be repeated.
            cursor.execute(
                "TRUNCATE TABLE events, team_match_stats, "
                "matches RESTART IDENTITY;"
            )

            # Load parent table first to satisfy foreign keys.
            load_csv(cursor, "matches", "matches.csv")
            load_csv(cursor, "events", "events.csv")

            cursor.execute(
                "SELECT COUNT(*) FROM matches"
            )
            match_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM events"
            )
            event_count = cursor.fetchone()[0]

            if match_count != 380 or event_count != 1313773:
                raise ValueError(
                    f"Unexpected counts: "
                    f"{match_count} matches, {event_count} events"
                )

            print("\n--- DATABASE LOAD SUMMARY ---")
            print(f"Matches loaded: {match_count:,}")
            print(f"Events loaded: {event_count:,}")

    print("Database transaction committed successfully.")


if __name__ == "__main__":
    main()
