from collections import defaultdict
from pathlib import Path

from src.preprocessing.hdfs_parser import extract_block_id, match_event

LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "HDFS.log"


def build_sequences():
    sequences = defaultdict(list)
    line_count = 0

    with open(
        LOG_PATH,
        "r",
        encoding="utf-8",
        errors="replace",
        buffering=1024 * 1024
    ) as f:

        while True:
            try:
                line = f.readline()
            except OSError as e:
                print(f"\nSkipped unreadable position at line {line_count:,}: {e}")
                continue

            if not line:
                break

            line_count += 1

            block_id = extract_block_id(line)

            if block_id:
                event_id = match_event(line)

                if event_id and event_id != "E30":
                    sequences[block_id].append(event_id)

            if line_count % 100000 == 0:
                print(
                    f"Processed {line_count:,} lines | "
                    f"Blocks: {len(sequences):,}",
                    flush=True
                )

    return sequences


if __name__ == "__main__":
    sequences = build_sequences()

    print()
    print("Finished!")
    print("Total blocks:", len(sequences))

    for block_id, events in list(sequences.items())[:5]:
        print(block_id, " ".join(events))