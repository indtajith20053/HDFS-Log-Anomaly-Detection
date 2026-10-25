import csv
import re
from pathlib import Path


TEMPLATE_FILE = Path(__file__).parent.parent / "data" / "templates" / "HDFS.log_templates.csv"


def load_templates():
    templates = {}

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            templates[row["EventId"]] = row["EventTemplate"]

    return templates


def template_to_regex(template):
    """
    Convert <*> wildcards in an HDFS template
    into a regex pattern.
    """

    parts = template.split("<*>")

    pattern = ".*?".join(re.escape(part) for part in parts)

    return re.compile(pattern, re.IGNORECASE)


def build_event_matchers():
    templates = load_templates()

    matchers = {}

    for event_id, template in templates.items():
        matchers[event_id] = template_to_regex(template)

    return matchers


EVENT_MATCHERS = build_event_matchers()


def parse_log_line(line):
    """
    Convert one raw HDFS log line into an Event ID.
    """

    line = line.strip()

    if not line:
        return None

    # Remove the timestamp / INFO / component prefix.
    # We only need the actual message.
    parts = line.split(":", 1)

    if len(parts) != 2:
        return None

    message = parts[1].strip()

    for event_id, matcher in EVENT_MATCHERS.items():

        if matcher.fullmatch(message):
            return event_id

    return None


if __name__ == "__main__":

    test_lines = [
        "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010",

        "081109 203519 145 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1608999687919862906 terminating",

        "081109 203519 145 INFO dfs.DataNode$PacketResponder: Received block blk_-1608999687919862906 of size 91178 from /10.250.10.6",
    ]

    for line in test_lines:

        event_id = parse_log_line(line)

        print("RAW:", line)
        print("EVENT:", event_id)
        print("-" * 80)
