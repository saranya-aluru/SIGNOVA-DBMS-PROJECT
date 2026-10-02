import os
import csv
import cv2
import mediapipe as mp

DATASET_DIR = "isl_dataset"
OUTPUT_FILE = "backend/isl_landmarks.csv"
TASK_MODEL = "backend/hand_landmarker.task"

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


def get_hand_features(result):

    if not result.hand_landmarks:
        return None

    hands = []

    for hand in result.hand_landmarks:
        if len(hand) == 21:
            hands.append(normalize_hand(hand))

    if len(hands) == 0:
        return None

    # One hand = 63 features
    if len(hands) == 1:
        return hands[0]

    # Two hands = 126 features
    # Keep the first two detected hands
    if len(hands) >= 2:
        return hands[0] + hands[1]

    return None


def process_video(video_path, label, landmarker, writer):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Could not open:", video_path)
        return 0

    count = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Process every 3rd frame
        # This prevents the dataset from becoming unnecessarily huge.
        if count % 3 != 0:
            count += 1
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = landmarker.detect(mp_image)

        features = get_hand_features(result)

        if features is not None:

            # Record whether this is a one-hand or two-hand sample
            hand_count = len(features) // 63

            writer.writerow(
                features + [label, hand_count]
            )

        count += 1

    cap.release()

    return count


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

    total_frames = 0
    total_samples = 0

    with HandLandmarker.create_from_options(options) as landmarker:

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            # 126 possible landmark features
            header = [f"f{i}" for i in range(126)]

            header.append("label")
            header.append("hand_count")

            writer.writerow(header)

            for label in sorted(os.listdir(DATASET_DIR)):

                folder = os.path.join(DATASET_DIR, label)

                if not os.path.isdir(folder):
                    continue

                if label.startswith("."):
                    continue

                videos = [
                    f for f in os.listdir(folder)
                    if f.lower().endswith(".mp4")
                ]

                print()
                print("=" * 50)
                print("SIGN:", label)
                print("VIDEOS:", len(videos))
                print("=" * 50)

                for video in videos:

                    path = os.path.join(folder, video)

                    print("Processing:", video)

                    before = total_samples

                    frames = process_video(
                        path,
                        label,
                        landmarker,
                        writer
                    )

                    total_frames += frames

                    print("  processed frames:", frames)

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print("Output:", OUTPUT_FILE)
    print("=" * 60)


if __name__ == "__main__":
    main()