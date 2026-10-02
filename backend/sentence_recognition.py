import cv2
import mediapipe as mp
import pickle
import math
from database_helper import save_recognition, get_words


# ==============================
# Load models
# ==============================

with open("sign_model.pkl", "rb") as file:
    one_hand_model = pickle.load(file)

with open("sign_model_two_hand.pkl", "rb") as file:
    two_hand_model = pickle.load(file)


# ==============================
# Load vocabulary from MySQL
# ==============================

words = get_words()

print("Vocabulary loaded from MySQL:")
print(words)


# ==============================
# MediaPipe
# ==============================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)


# ==============================
# Get Left and Right hands
# ==============================

def get_left_right_hands(result):

    left_hand = None
    right_hand = None

    for i, handedness in enumerate(result.handedness):

        label = handedness[0].category_name

        if label == "Left":
            left_hand = result.hand_landmarks[i]

        elif label == "Right":
            right_hand = result.hand_landmarks[i]

    return left_hand, right_hand


# ==============================
# Normalize one hand
# ==============================

def normalize_hand(hand):

    wrist = hand[0]

    points = []

    for landmark in hand:

        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        points.append((x, y, z))

    max_distance = 0

    for x, y, z in points:

        distance = math.sqrt(
            x * x +
            y * y +
            z * z
        )

        if distance > max_distance:
            max_distance = distance

    if max_distance == 0:
        max_distance = 1

    values = []

    for x, y, z in points:

        values.extend([
            x / max_distance,
            y / max_distance,
            z / max_distance
        ])

    return values


# ==============================
# One-hand prediction
# ==============================

def predict_one_hand(hand):

    values = normalize_hand(hand)

    best_distance = float("inf")
    best_label = None

    for sample, label in zip(
        one_hand_model["features"],
        one_hand_model["labels"]
    ):

        distance = 0

        for a, b in zip(values, sample):
            distance += (a - b) ** 2

        distance = math.sqrt(distance)

        if distance < best_distance:
            best_distance = distance
            best_label = label

    return best_label


# ==============================
# Two-hand prediction
# ==============================

def predict_two_hands(left_hand, right_hand):

    left_values = normalize_hand(left_hand)
    right_values = normalize_hand(right_hand)

    values = left_values + right_values

    best_distance = float("inf")
    best_label = None

    for sample, label in zip(
        two_hand_model["features"],
        two_hand_model["labels"]
    ):

        distance = 0

        for a, b in zip(values, sample):
            distance += (a - b) ** 2

        distance = math.sqrt(distance)

        if distance < best_distance:
            best_distance = distance
            best_label = label

    return best_label


# ==============================
# Camera
# ==============================

cap = cv2.VideoCapture(0)

sentence = []
last_sign = None
stable_count = 0

STABLE_FRAMES = 8


# ==============================
# Start MediaPipe
# ==============================

with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = cap.read()

        if not success:
            print("Camera error")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = landmarker.detect(mp_image)

        hand_count = len(result.hand_landmarks)

        recognized_sign = None


        # ==============================
        # One hand
        # ==============================

        if hand_count == 1:

            hand = result.hand_landmarks[0]

            recognized_sign = predict_one_hand(hand)


        # ==============================
        # Two hands
        # ==============================

        elif hand_count == 2:

            left_hand, right_hand = get_left_right_hands(result)

            if left_hand is not None and right_hand is not None:

                recognized_sign = predict_two_hands(
                    left_hand,
                    right_hand
                )


        # ==============================
        # Stabilize recognition
        # ==============================

        if recognized_sign is not None:

            if recognized_sign == last_sign:

                stable_count += 1

            else:

                last_sign = recognized_sign
                stable_count = 1


            # Add only after stable recognition
            if stable_count == STABLE_FRAMES:

                if recognized_sign not in sentence:

                    sentence.append(recognized_sign)

                    save_recognition(recognized_sign)

                    print(
                        "Recognized:",
                        recognized_sign
                    )


        # ==============================
        # Display sentence
        # ==============================

        sentence_text = " ".join(
            words.get(sign, sign)
            for sign in sentence
        )


        # ==============================
        # Display information
        # ==============================

        cv2.putText(
            frame,
            "Hands: " + str(hand_count),
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Sign: " + str(recognized_sign),
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Sentence: " + sentence_text,
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Q = Quit | C = Clear",
            (20, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            2
        )


        cv2.imshow(
            "Sign Language Recognition",
            frame
        )


        # ==============================
        # Keyboard
        # ==============================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("c"):

            sentence.clear()

            last_sign = None
            stable_count = 0

            print("Sentence cleared")


cap.release()
cv2.destroyAllWindows()