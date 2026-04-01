import argparse
import json
import os
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

DATABASE_URL_DEFAULT = (
    "postgresql://postgres:efwzThw2KHTNx6tLko6uy9dLtBratJYuxOy2mgBgc4Q"
    "@localhost:5432/postgres"
)

BASE_DIR = os.path.dirname(__file__)

FILE_TO_CONFIG_TYPE = {
    os.path.join(BASE_DIR, "clean_glossary.json"):           "glossary_terms",
    os.path.join(BASE_DIR, "ambiguity_terms.json"):          "ambiguous_terms",
    os.path.join(BASE_DIR, "allowed_aliases_en-gu.json"):    "en-gujarati_aliases",
    os.path.join(BASE_DIR, "gujarati_terms_forbidden.json"): "forbidden",
    os.path.join(BASE_DIR, "preferred.json"):           "preferred",
    os.path.join(BASE_DIR, "scheme_list.json"):              "schemes",
    os.path.join(BASE_DIR, "english_aliases.json"):          "english_aliases",
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS config_versions (
    config_type    TEXT    NOT NULL,
    version_number INTEGER NOT NULL,
    snapshot       JSONB   NOT NULL,
    triggered_by   TEXT,
    note           TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (config_type, version_number)
);
"""


def load_json_file(file_path: Path):
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def seed_config_versions(
    conn,
    base_dir: Path,
    triggered_by: str,
    note: Optional[str] = "Initial config seed (version 1)",
):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()

        for filename, config_type in FILE_TO_CONFIG_TYPE.items():
            file_path = base_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            payload = load_json_file(file_path)

            cur.execute(
                """
                INSERT INTO config_versions (config_type, version_number, snapshot, note, triggered_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (config_type, version_number) DO UPDATE
                    SET snapshot = EXCLUDED.snapshot,
                        triggered_by = EXCLUDED.triggered_by,
                        note = EXCLUDED.note
                """,
                (
                    config_type,
                    1,
                    json.dumps(payload, ensure_ascii=False),
                    note,
                    triggered_by,
                ),
            )
            conn.commit()
            print(f"Seeded  {config_type}  \u2190  {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Seed config_versions table from JSON files."
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DATABASE_URL_DEFAULT),
        help="PostgreSQL connection string. Falls back to DATABASE_URL env var.",
    )
    parser.add_argument(
        "--triggered-by",
        default=os.getenv("USER") or os.getenv("USERNAME") or "seed_script",
        help="Value stored in config_versions.triggered_by",
    )
    parser.add_argument(
        "--note",
        default="Initial config seed (version 1)",
        help="Optional note stored in config_versions.note",
    )
    parser.add_argument(
        "--base-dir",
        default=None,
        type=Path,
        help="Directory containing JSON files (default: same folder as this script).",
    )
    args = parser.parse_args()

    base_dir = args.base_dir or Path(__file__).resolve().parent
    conn = psycopg2.connect(args.database_url)

    try:
        seed_config_versions(
            conn=conn,
            base_dir=base_dir,
            triggered_by=args.triggered_by,
            note=args.note,
        )
        print("\nDone seeding config_versions.")
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
