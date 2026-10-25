import re
import csv
from pathlib import Path
from functools import lru_cache

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "data" / "templates" / "HDFS.log_templates.csv"


def extract_block_id(line: str):
    match = re.search(r"blk_-?\d+", line)
    return match.group(0) if match else None


@lru_cache(maxsize=1)
def load_templates():
    templates = []

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            templates.append(
                (row["EventId"], row["EventTemplate"])
            )

    return templates


def match_event(line: str):
    templates = load_templates()

    for event_id, template in templates:
        parts = template.split("<*>")

        pattern = ".*".join(
            re.escape(part) for part in parts
        )

        if re.search(pattern, line, re.IGNORECASE):
            return event_id

    return None