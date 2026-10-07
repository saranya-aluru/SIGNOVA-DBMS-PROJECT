import os
import csv
import cv2
import mediapipe as mp

DATASET_DIR = "isl_dataset"
OUTPUT_FILE = "backend/isl_landmarks.csv"
TASK_MODEL = "backend/hand_landmarker.task"

# Keep the project simple: only 10 signs
SELECTED_SIGNS = [
    "hello",
    "yes",
    "no",
    "please",
    "thank_you",
    "stop",
    "home",
    "tea",
    "water",
    "help"
]

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


def normalize_hand(hand):
    wrist = hand[0]
    features = []

    for lm in hand:
        features.extend([
            lm.x - wrist.x,
            lm.y - wrist.y,
            lm.z - wrist.z
        ])

    return features


def get_features(result):

    if not result.hand_landmarks:
        return None

    hands = []

    for hand in result.hand_landmarks:
        if len(hand) == 21:
            hands.append(normalize_hand(hand))

    if not hands:
        return None

    # One-hand sign
    if len(hands) == 1:
        return hands[0] + [1]

    # Two-hand sign
    return hands[0] + hands[1] + [2]


def process_video(video_path, label, landmarker, writer):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Could not open:", video_path)
        return 0

    frame_number = 0
    samples = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Use every 5th frame
        if frame_number % 5 != 0:
            frame_number += 1
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = landmarker.detect(image)

        features = get_features(result)

        if features is not None:

            hand_count = features[-1]
            landmark_features = features[:-1]

            # Keep separate formats:
            # 63 features for one hand
            # 126 features for two hands
            if hand_count == 1:
                row = landmark_features + [label, 1]
                writer.writerow(row)
                samples += 1

            elif hand_count == 2:
                row = landmark_features + [label, 2]
                writer.writerow(row)
                samples += 1

        frame_number += 1

    cap.release()

    return samples


def main():

    os.makedirs("backend", exist_ok=True)

    options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=TASK_MODEL
        ),
        running_mode=RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    total = 0

    with HandLandmarker.create_from_options(options) as landmarker:

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            # 126 feature columns + label + hand_count
            header = [f"f{i}" for i in range(126)]
            header += ["label", "hand_count"]

            writer = csv.writer(file)
            writer.writerow(header)

            for label in SELECTED_SIGNS:

                folder = os.path.join(DATASET_DIR, label)

                if not os.path.isdir(folder):
                    print("Missing folder:", label)
                    continue

                videos = [
                    f for f in os.listdir(folder)
                    if f.lower().endswith(".mp4")
                ]

                print()
                print("=" * 45)
                print("SIGN:", label)
                print("VIDEOS:", len(videos))
                print("=" * 45)

                for video in videos:

                    path = os.path.join(folder, video)

                    print("Processing:", video)

                    samples = process_video(
                        path,
                        label,
                        landmarker,
                        writer
                    )

                    print("Samples:", samples)

                    total += samples

    print()
    print("=" * 50)
    print("EXTRACTION COMPLETE")
    print("Total samples:", total)
    print("Output:", OUTPUT_FILE)
    print("=" * 50)


if __name__ == "__main__":
    main()