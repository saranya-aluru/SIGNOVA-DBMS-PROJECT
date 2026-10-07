import csv
import glob
import pickle
import random

features = []
labels = []

files = glob.glob("*_2hand.csv")

print("Two-hand files found:")

for filename in files:
    print(" -", filename)

    label = filename.replace("_2hand.csv", "")

    with open(filename, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            if not row:
                continue

            try:
                values = [float(value) for value in row]
            except ValueError:
                continue

            if len(values) != 126:
                continue

            features.append(values)
            labels.append(label)


# -----------------------------
# Balance samples
# -----------------------------

data = {}

for x, y in zip(features, labels):
    if y not in data:
        data[y] = []

    data[y].append(x)

minimum = min(len(samples) for samples in data.values())

print("\nBalancing samples...")
print("Using", minimum, "samples per sign")

balanced_features = []
balanced_labels = []

for label in sorted(data.keys()):

    samples = data[label]

    random.shuffle(samples)

    samples = samples[:minimum]

    balanced_features.extend(samples)
    balanced_labels.extend([label] * len(samples))


# -----------------------------
# Save model
# -----------------------------

model = {
    "features": balanced_features,
    "labels": balanced_labels
}

with open("sign_model_two_hand.pkl", "wb") as file:
    pickle.dump(model, file)


print("\n================================")
print("Two-hand model trained!")
print("================================")

print("Total samples:", len(balanced_features))
print("Signs:", sorted(set(balanced_labels)))
print("Samples per sign:", minimum)
print("Model saved as: sign_model_two_hand.pkl")