"""
deduplicate.py
--------------
Merge the CSV logs from fetch_batman.py and fetch_byline.py, identify
duplicate articles (same Trove ID written by both passes), and produce
a single master CSV for review.

Does NOT delete any .md files — duplicates are flagged in the CSV only.
You can then decide which file to keep and delete the other manually.

Usage:
    python deduplicate.py

Output:
    trove/output/master_results.csv
"""

import os
import csv
import glob

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

RESULT_FILES = [
    "fetch_batman_results.csv",
    "fetch_byline_results.csv",
]


def main():
    seen_ids = {}   # trove_id -> first row seen
    all_rows = []
    duplicates = []

    for result_file in RESULT_FILES:
        path = os.path.join(OUTPUT_DIR, result_file)
        if not os.path.exists(path):
            print(f"  MISSING (run the fetch script first): {result_file}")
            continue

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row.get("trove_id", "")
                row["source_pass"] = result_file.replace("_results.csv", "")

                if tid in seen_ids:
                    row["duplicate_of"] = seen_ids[tid]["filename"]
                    duplicates.append(row)
                else:
                    seen_ids[tid] = row
                    row["duplicate_of"] = ""

                all_rows.append(row)

    master_path = os.path.join(OUTPUT_DIR, "master_results.csv")
    fieldnames = ["trove_id", "title", "date", "url", "filename", "status", "source_pass", "duplicate_of"]

    with open(master_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Total rows across all passes: {len(all_rows)}")
    print(f"Unique articles: {len(seen_ids)}")
    print(f"Duplicates (same Trove ID from multiple passes): {len(duplicates)}")
    if duplicates:
        print("\nDuplicate files to review:")
        for d in duplicates:
            print(f"  {d['filename']}  (duplicate of {d['duplicate_of']})")
    print(f"\nMaster CSV written: {master_path}")


if __name__ == "__main__":
    main()
