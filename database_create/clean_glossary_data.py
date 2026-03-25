import json
import re
import os

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "glossary_terms.json")
with open(file_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)
#diff cases and extra spaces
def normalize_term(term):
    term = term.strip().lower()
    term = re.sub(r"\s+", " ", term)
    return term


def normalize_transliteration(text):
    if not text:
        return []
    
    parts = re.split(r"[,/]", text)
    
    return [
        re.sub(r"\s+", " ", p.strip().lower())
        for p in parts
        if p.strip()
    ]

def process_glossary(raw_data):
    glossary = {}
    conflicts = []

    for entry in raw_data:
        if not entry.get("en") or not entry.get("gu"):
            continue

        original = entry["en"]
        normalized = normalize_term(original)

        new_value = {
            "gu": entry["gu"],
            "transliteration": normalize_transliteration(entry.get("transliteration"))
        }

        if normalized in glossary:
            conflicts.append({
                "term": normalized,
                "original_term": original,
                "old": glossary[normalized],
                "new": new_value
            })

        glossary[normalized] = new_value

    return glossary, conflicts


if __name__ == "__main__":
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    glossary, conflicts = process_glossary(raw)

    with open("clean_glossary.json", "w", encoding="utf-8") as f:
        json.dump(glossary, f, indent=2, ensure_ascii=False)

    with open("conflicts.json", "w", encoding="utf-8") as f:
        json.dump(conflicts, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(glossary)} terms")
    print(f"Conflicts found: {len(conflicts)}")