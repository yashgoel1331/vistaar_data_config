import argparse
import json
import os
import dotenv
from pathlib import Path
from typing import Optional

from supabase import create_client, Client

dotenv.load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ddpmzibgajndovcnuicm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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


def load_json_file(file_path: Path):
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def seed_config_versions(
    supabase: Client,
    base_dir: Path,
    triggered_by: str,
    note: Optional[str] = "Initial config seed (version 1)",
):
    for filename, config_type in FILE_TO_CONFIG_TYPE.items():
        file_path = base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        payload = load_json_file(file_path)

        supabase.table("config_versions").upsert(
            {
                "config_type":    config_type,
                "version_number": 1,
                "snapshot":       payload,
                "note":           note,
                "triggered_by":   triggered_by,
            },
            on_conflict="config_type,version_number",
        ).execute()

        print(f"Seeded  {config_type}  ←  {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Seed config_versions table from JSON files."
    )
    parser.add_argument(
        "--supabase-url",
        default=SUPABASE_URL,
        help="Supabase project URL. Falls back to SUPABASE_URL env var.",
    )
    parser.add_argument(
        "--supabase-key",
        default=SUPABASE_KEY,
        help="Supabase service-role or anon key. Falls back to SUPABASE_KEY env var.",
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

    if not args.supabase_url or not args.supabase_key:
        raise ValueError(
            "Supabase URL and key are required. "
            "Pass --supabase-url / --supabase-key or set SUPABASE_URL / SUPABASE_KEY."
        )

    base_dir = args.base_dir or Path(__file__).resolve().parent
    client = create_client(args.supabase_url, args.supabase_key)

    try:    
        seed_config_versions(
            supabase=client,
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


if __name__ == "__main__":
    main()