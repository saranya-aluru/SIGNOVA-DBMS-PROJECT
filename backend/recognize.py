import cv2
import mediapipe as mp
import pickle
import math


# Load trained model
with open("sign_model.pkl", "rb") as file:
    model = pickle.load(file)

labels = model["labels"]
features = model["features"]


def normalize_landmarks(hand):
    points = []

    for landmark in hand:
        points.append((landmark.x, landmark.y, landmark.z))

    # Use wrist as origin
    wx, wy, wz = points[0]

    shifted = []

    for x, y, z in points:
        shifted.append((x - wx, y - wy, z - wz))

    # Scale normalization
    scale = 0

    for x, y, z in shifted[1:]:
        distance = math.sqrt(x*x + y*y + z*z)
        scale = max(scale, distance)

    if scale == 0:
        scale = 1

    normalized = []

    for x, y, z in shifted:
        normalized.extend([
            x / scale,
            y / scale,
            z / scale
        ])

    return normalized


def distance(a, b):
    total = 0

    for x, y in zip(a, b):
        total += (x - y) ** 2

    return math.sqrt(total)


def predict(hand):
    current = normalize_landmarks(hand)

    best_distance = float("inf")
    best_label = "Unknown"

    for sample, label in zip(features, labels):
        d = distance(current, sample)

        if d < best_distance:
            best_distance = d
            best_label = label

    return best_label


# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1
)


# Start webcam
cap = cv2.VideoCapture(0)

with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = cap.read()

        if not success:
            print("Could not access webcam")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = landmarker.detect(mp_image)

        prediction = "No hand"

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            prediction = predict(hand)

            # Draw landmarks
            h, w, _ = frame.shape

            for landmark in hand:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

        # Display prediction
        cv2.putText(
            frame,
            "Sign: " + prediction,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            "Press Q to quit",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Sign Language Recognition",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


cap.release()
cv2.destroyAllWindows()