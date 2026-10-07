import os
import base64
import pickle

import cv2
import numpy as np
import mediapipe as mp

from flask import Flask, request, jsonify
from flask_cors import CORS

from database_helper import get_sign, get_signs, save_recognition


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TASK_MODEL_PATH = os.path.join(
    BASE_DIR,
    "hand_landmarker.task"
)

ONE_HAND_MODEL_PATH = os.path.join(
    BASE_DIR,
    "sign_model.pkl"
)

TWO_HAND_MODEL_PATH = os.path.join(
    BASE_DIR,
    "sign_model_two_hand.pkl"
)


# ============================================================
# LOAD ONE-HAND MODEL
# ============================================================

one_hand_model = None

try:
    with open(ONE_HAND_MODEL_PATH, "rb") as file:
        one_hand_model = pickle.load(file)

    print("One-hand model loaded: True")

except Exception as e:
    print("One-hand model loading failed:")
    print(e)


# ============================================================
# LOAD TWO-HAND MODEL
# ============================================================

two_hand_model = None

try:
    with open(TWO_HAND_MODEL_PATH, "rb") as file:
        two_hand_model = pickle.load(file)

    print("Two-hand model loaded: True")

except Exception as e:
    print("Two-hand model loading failed:")
    print(e)


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=TASK_MODEL_PATH
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


try:

    landmarker = HandLandmarker.create_from_options(
        options
    )

    print("MediaPipe loaded: True")

except Exception as e:

    print("MediaPipe loading failed:")
    print(e)

    landmarker = None


# ============================================================
# NORMALIZE LANDMARKS
# ============================================================

def normalize_landmarks(landmarks):

    if not landmarks:
        return None

    points = []

    for landmark in landmarks:

        points.append([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    # --------------------------------------------------------
    # Use wrist as origin
    # --------------------------------------------------------

    wrist_x = points[0][0]
    wrist_y = points[0][1]
    wrist_z = points[0][2]

    normalized = []

    for point in points:

        normalized.append([
            point[0] - wrist_x,
            point[1] - wrist_y,
            point[2] - wrist_z
        ])

    # --------------------------------------------------------
    # Scale normalization
    # --------------------------------------------------------

    max_distance = 0.0

    for point in normalized:

        distance = (
            point[0] ** 2
            + point[1] ** 2
            + point[2] ** 2
        ) ** 0.5

        if distance > max_distance:
            max_distance = distance

    if max_distance == 0:

        max_distance = 1.0

    for i in range(len(normalized)):

        normalized[i][0] /= max_distance
        normalized[i][1] /= max_distance
        normalized[i][2] /= max_distance

    # --------------------------------------------------------
    # Flatten 21 x 3 = 63 features
    # --------------------------------------------------------

    features = []

    for point in normalized:

        features.extend(point)

    return features


# ============================================================
# ORDER HANDS
# ============================================================

def get_ordered_hands(result):

    if not result.hand_landmarks:

        return []

    hands = []

    for i, landmarks in enumerate(
        result.hand_landmarks
    ):

        handedness = "Unknown"

        if (
            result.handedness
            and i < len(result.handedness)
            and result.handedness[i]
        ):

            handedness = (
                result.handedness[i][0].category_name
            )

        hands.append({
            "landmarks": landmarks,
            "handedness": handedness
        })

    # --------------------------------------------------------
    # LEFT FIRST, RIGHT SECOND
    # --------------------------------------------------------

    hands.sort(
        key=lambda hand: (
            0
            if hand["handedness"].lower() == "left"
            else 1
        )
    )

    return hands


# ============================================================
# PREDICT MODEL
# ============================================================

def predict_model(model, features):

    if model is None:

        return None, None

    training_features = model.get(
        "features",
        []
    )

    training_labels = model.get(
        "labels",
        []
    )

    if not training_features:

        return None, None

    distances = []

    # --------------------------------------------------------
    # Compare current frame with every training sample
    # --------------------------------------------------------

    for sample, label in zip(
        training_features,
        training_labels
    ):

        if len(sample) != len(features):

            continue

        distance = 0.0

        for a, b in zip(
            sample,
            features
        ):

            difference = a - b

            distance += (
                difference * difference
            )

        distance = distance ** 0.5

        distances.append(
            (distance, label)
        )

    if not distances:

        return None, None

    # --------------------------------------------------------
    # Closest samples first
    # --------------------------------------------------------

    distances.sort(
        key=lambda item: item[0]
    )

    # --------------------------------------------------------
    # Use K = 5
    # --------------------------------------------------------

    k = min(
        5,
        len(distances)
    )

    nearest = distances[:k]

    # --------------------------------------------------------
    # Count votes
    # --------------------------------------------------------

    votes = {}

    for distance, label in nearest:

        if label not in votes:

            votes[label] = 0

        votes[label] += 1

    # --------------------------------------------------------
    # Select majority vote
    # --------------------------------------------------------

    best_label = max(
        votes,
        key=votes.get
    )

    best_distance = nearest[0][0]

    return best_label, best_distance


# ============================================================
# DECODE IMAGE
# ============================================================

def decode_image(image_data):

    try:

        # ----------------------------------------------------
        # Remove data URL prefix
        # ----------------------------------------------------

        if "," in image_data:

            image_data = image_data.split(
                ",",
                1
            )[1]

        # ----------------------------------------------------
        # Base64 -> bytes
        # ----------------------------------------------------

        image_bytes = base64.b64decode(
            image_data
        )

        # ----------------------------------------------------
        # Bytes -> NumPy
        # ----------------------------------------------------

        np_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        # ----------------------------------------------------
        # NumPy -> OpenCV image
        # ----------------------------------------------------

        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR
        )

        return frame

    except Exception as e:

        print(
            "Image decoding error:",
            e
        )

        return None


# ============================================================
# RECOGNIZE
# ============================================================

@app.route(
    "/recognize",
    methods=["POST"]
)
def recognize():

    try:

        # ----------------------------------------------------
        # Check JSON
        # ----------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received"
            })

        # ----------------------------------------------------
        # Get image
        # ----------------------------------------------------

        image_data = data.get(
            "image"
        )

        if not image_data:

            return jsonify({
                "success": False,
                "error": "No image received"
            })

        # ----------------------------------------------------
        # Decode image
        # ----------------------------------------------------

        frame = decode_image(
            image_data
        )

        if frame is None:

            return jsonify({
                "success": False,
                "error": "Could not decode image"
            })

        # ----------------------------------------------------
        # BGR -> RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # ----------------------------------------------------
        # Create MediaPipe image
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # ----------------------------------------------------
        # Detect hands
        # ----------------------------------------------------

        if landmarker is None:

            return jsonify({
                "success": False,
                "error": "MediaPipe is not loaded"
            })

        result = landmarker.detect(
            mp_image
        )

        hands = get_ordered_hands(
            result
        )

        hand_count = len(hands)

        # ====================================================
        # NO HAND
        # ====================================================

        if hand_count == 0:

            return jsonify({

                "success": True,

                "sign": None,

                "word": None,

                "hand_count": 0,

                "distance": None,

                "sign_info": None

            })

        # ====================================================
        # ONE HAND
        # ====================================================

        if hand_count == 1:

            if one_hand_model is None:

                return jsonify({

                    "success": False,

                    "error":
                    "One-hand model is not loaded"

                })

            features = normalize_landmarks(
                hands[0]["landmarks"]
            )

            if features is None:

                return jsonify({

                    "success": True,

                    "sign": None,

                    "word": None,

                    "hand_count": 1,

                    "distance": None,

                    "sign_info": None

                })

            # ------------------------------------------------
            # IMPORTANT:
            # One-hand model should have 63 features
            # ------------------------------------------------

            if len(features) != 63:

                print(
                    "WARNING: Expected 63 features,"
                    f" got {len(features)}"
                )

                return jsonify({

                    "success": False,

                    "error":
                    "One-hand feature size mismatch"

                })

            sign, distance = predict_model(
                one_hand_model,
                features
            )

        # ====================================================
        # TWO HANDS
        # ====================================================

        elif hand_count == 2:

            if two_hand_model is None:

                return jsonify({

                    "success": False,

                    "error":
                    "Two-hand model is not loaded"

                })

            first_hand = normalize_landmarks(
                hands[0]["landmarks"]
            )

            second_hand = normalize_landmarks(
                hands[1]["landmarks"]
            )

            if (
                first_hand is None
                or second_hand is None
            ):

                return jsonify({

                    "success": True,

                    "sign": None,

                    "word": None,

                    "hand_count": 2,

                    "distance": None,

                    "sign_info": None

                })

            # ------------------------------------------------
            # 63 + 63 = 126 features
            # ------------------------------------------------

            features = (
                first_hand
                + second_hand
            )

            if len(features) != 126:

                print(
                    "WARNING: Expected 126 features,"
                    f" got {len(features)}"
                )

                return jsonify({

                    "success": False,

                    "error":
                    "Two-hand feature size mismatch"

                })

            sign, distance = predict_model(
                two_hand_model,
                features
            )

        # ====================================================
        # MORE THAN TWO HANDS
        # ====================================================

        else:

            return jsonify({

                "success": True,

                "sign": None,

                "word": None,

                "hand_count": hand_count,

                "distance": None,

                "sign_info": None

            })

        # ====================================================
        # NOTHING PREDICTED
        # ====================================================

        if sign is None:

            return jsonify({

                "success": True,

                "sign": None,

                "word": None,

                "hand_count": hand_count,

                "distance": distance,

                "sign_info": None

            })

        # ====================================================
        # MYSQL LOOKUP
        # ====================================================

        sign_info = None

        word = sign

        try:

            sign_info = get_sign(
                sign
            )

            if sign_info:

                word = sign_info.get(
                    "display_word",
                    sign
                )

        except Exception as e:

            print(
                "MySQL lookup error:",
                e
            )

        # ====================================================
        # SAVE HISTORY
        # ====================================================

        try:

            save_recognition(
                sign
            )

        except Exception as e:

            print(
                "History save error:",
                e
            )

        # ====================================================
        # RETURN RESULT
        # ====================================================

        return jsonify({

            "success": True,

            "sign": sign,

            "word": word,

            "hand_count": hand_count,

            "distance": distance,

            "sign_info": sign_info

        })

    except Exception as e:

        print(
            "Recognition error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        })


# ============================================================
# GET ALL SIGNS
# ============================================================

@app.route(
    "/signs",
    methods=["GET"]
)
def signs():

    try:

        signs_data = get_signs()

        return jsonify({

            "success": True,

            "signs": signs_data

        })

    except Exception as e:

        print(
            "Signs error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        })


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({

        "success": True,

        "message":
        "Signova backend is running",

        "recognition":
        "/recognize",

        "signs":
        "/signs"

    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("SIGNOVA BACKEND")
    print("=" * 50)

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "Recognition: "
        "http://127.0.0.1:5000/recognize"
    )

    print(
        "Signs: "
        "http://127.0.0.1:5000/signs"
    )

    print("=" * 50)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )