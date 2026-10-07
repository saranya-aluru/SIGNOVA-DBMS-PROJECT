import csv
import os

# Existing one-hand CSV files
files = [
    "HELLO.csv",
    "YES.csv",
    "NO.csv",
    "PLEASE.csv",
    "THANK_YOU.csv",
    "ILOVEYOU.csv"
]

output_file = "one_hand_dataset.csv"

all_rows = []

for filename in files:
    if not os.path.exists(filename):
        print(f"WARNING: {filename} not found")
        continue

    label = os.path.splitext(filename)[0]

    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print(f"WARNING: {filename} is empty")
        continue

    # Detect whether the CSV has a header
    first_row = rows[0]

    try:
        [float(x) for x in first_row]
        has_header = False
    except ValueError:
        has_header = True

    data_rows = rows[1:] if has_header else rows

    for row in data_rows:
        if not row:
            continue

        # Keep the 63 landmark values and add the sign label
        all_rows.append(row + [label])

    print(f"{label}: {len(data_rows)} samples")

# Write the new master dataset
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    # 63 landmark values + label
    header = [f"feature_{i}" for i in range(1, 64)]
    header.append("label")

    writer.writerow(header)
    writer.writerows(all_rows)

print()
print("=" * 50)
print("MASTER DATASET CREATED")
print("=" * 50)
print(f"File: {output_file}")
print(f"Total samples: {len(all_rows)}")
print()

# Count samples per sign
counts = {}

for row in all_rows:
    label = row[-1]
    counts[label] = counts.get(label, 0) + 1

for label, count in counts.items():
    print(f"{label}: {count}")