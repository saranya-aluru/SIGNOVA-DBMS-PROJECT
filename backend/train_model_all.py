import csv
import math
import pickle
import os

FILES = [
    "HELLO.csv",
    "YES.csv",
    "NO.csv",
    "PLEASE.csv",
    "THANK_YOU.csv",
    "ILOVEYOU.csv"
]


def normalize(values):
    points = []

    for i in range(0, 63, 3):
        points.append((
            values[i],
            values[i + 1],
            values[i + 2]
        ))

    # Use wrist as origin
    wx, wy, wz = points[0]

    shifted = []

    for x, y, z in points:
        shifted.append((
            x - wx,
            y - wy,
            z - wz
        ))

    # Find scale
    scale = 0

    for x, y, z in shifted[1:]:
        d = math.sqrt(
            x * x +
            y * y +
            z * z
        )

        scale = max(scale, d)

    if scale == 0:
        scale = 1

    result = []

    for x, y, z in shifted:
        result.extend([
            x / scale,
            y / scale,
            z / scale
        ])

    return result


features = []
labels = []


# -----------------------------
# Load all CSV files
# -----------------------------

for filename in FILES:

    if not os.path.exists(filename):
        print("Missing file:", filename)
        continue

    with open(filename, "r", newline="") as file:

        reader = csv.reader(file)

        # Skip header
        next(reader, None)

        for row in reader:

            if len(row) < 64:
                continue

            label = row[0]

            values = []

            for value in row[1:64]:
                values.append(float(value))

            normalized = normalize(values)

            features.append(normalized)
            labels.append(label)


# -----------------------------
# Display training information
# -----------------------------

print()
print("Training data loaded!")
print("Total samples:", len(features))

for sign in [
    "HELLO",
    "YES",
    "NO",
    "PLEASE",
    "THANK_YOU",
    "ILOVEYOU"
]:
    print(sign, "samples:", labels.count(sign))


# -----------------------------
# Create model
# -----------------------------

model = {
    "features": features,
    "labels": labels
}


# -----------------------------
# Save model
# -----------------------------

with open("sign_model.pkl", "wb") as file:
    pickle.dump(model, file)


print()
print("Model saved successfully as sign_model.pkl")