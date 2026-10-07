import cv2
import mediapipe as mp
import pickle
import math
import time

from database_helper import save_recognition


# -----------------------------
# Load trained model
# -----------------------------

with open("sign_model.pkl", "rb") as file:
    model = pickle.load(file)

labels = model["labels"]
features = model["features"]


# -----------------------------
# Normalize hand landmarks
# -----------------------------

def normalize_landmarks(hand):
    points = []

    for landmark in hand:
        points.append(
            (landmark.x, landmark.y, landmark.z)
        )

    # Use wrist as origin
    wx, wy, wz = points[0]

    shifted = []

    for x, y, z in points:
        shifted.append(
            (x - wx, y - wy, z - wz)
        )

    # Find largest distance from wrist
    scale = 0

    for x, y, z in shifted[1:]:
        distance_value = math.sqrt(
            x * x + y * y + z * z
        )

        scale = max(scale, distance_value)

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


# -----------------------------
# Calculate distance
# -----------------------------

def distance(a, b):
    total = 0

    for x, y in zip(a, b):
        total += (x - y) ** 2

    return math.sqrt(total)


# -----------------------------
# Predict sign
# -----------------------------

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


# -----------------------------
# MediaPipe setup
# -----------------------------

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


# -----------------------------
# Database logging variables
# -----------------------------

last_prediction = ""
last_saved_time = 0

# Save the same sign only after 2 seconds
SAVE_COOLDOWN = 2


# -----------------------------
# Open webcam
# -----------------------------

cap = cv2.VideoCapture(0)


with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = cap.read()

        if not success:
            print("Could not access webcam")
            break

        # Mirror image
        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Create MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect hand
        result = landmarker.detect(mp_image)

        prediction = "No hand"

        # -----------------------------
        # If hand detected
        # -----------------------------

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

            # -----------------------------
            # Save recognition to database
            # -----------------------------

            current_time = time.time()

            if (
                prediction != "Unknown"
                and
                (
                    prediction != last_prediction
                    or
                    current_time - last_saved_time >= SAVE_COOLDOWN
                )
            ):

                try:

                    save_recognition(prediction)

                    last_prediction = prediction
                    last_saved_time = current_time

                except Exception as error:

                    print(
                        "Database error:",
                        error
                    )


        # -----------------------------
        # Display prediction
        # -----------------------------

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


        # Show webcam
        cv2.imshow(
            "Sign Language Recognition",
            frame
        )


        # Quit with Q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# -----------------------------
# Close webcam
# -----------------------------

cap.release()
cv2.destroyAllWindows()