import cv2
import csv
import os
import time
import mediapipe as mp

# ==============================
# SETTINGS
# ==============================

SAMPLES = 150
OUTPUT_FILE = "one_hand_dataset.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")


# ==============================
# SIGN NAME
# ==============================

sign_name = input("Enter sign name: ").strip().upper()

if not sign_name:
    print("Invalid sign name.")
    exit()


# ==============================
# CHECK MODEL
# ==============================

if not os.path.exists(MODEL_PATH):
    print("ERROR: hand_landmarker.task not found.")
    print("Expected:", MODEL_PATH)
    exit()


# ==============================
# MEDIAPIPE
# ==============================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)


landmarker = HandLandmarker.create_from_options(options)


# ==============================
# CAMERA
# ==============================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    landmarker.close()
    exit()


print()
print("=" * 50)
print("SIGN:", sign_name)
print("TARGET:", SAMPLES, "samples")
print("=" * 50)
print()
print("Press S to start collecting.")
print("Press Q to quit.")
print()


started = False
count = 0


# ==============================
# CAMERA LOOP
# ==============================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not read camera.")
        break

    # Mirror image
    frame = cv2.flip(frame, 1)

    # Convert BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    # Detect hand
    result = landmarker.detect(mp_image)


    # ==============================
    # HAND DETECTED
    # ==============================

    if result.hand_landmarks:

        hand = result.hand_landmarks[0]

        # Draw landmarks
        for landmark in hand:

            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )


        # ==============================
        # COLLECT SAMPLE
        # ==============================

        if started and count < SAMPLES:

            features = []

            for landmark in hand:

                features.extend([
                    landmark.x,
                    landmark.y,
                    landmark.z
                ])


            if len(features) == 63:

                with open(
                    OUTPUT_FILE,
                    "a",
                    newline=""
                ) as file:

                    writer = csv.writer(file)

                    writer.writerow(
                        features + [sign_name]
                    )

                count += 1

                print(
                    f"\rCollected: {count}/{SAMPLES}",
                    end=""
                )

                time.sleep(0.03)


    # ==============================
    # SCREEN TEXT
    # ==============================

    cv2.putText(
        frame,
        f"Sign: {sign_name}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Samples: {count}/{SAMPLES}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    if not started:

        cv2.putText(
            frame,
            "Press S to start",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "COLLECTING...",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    cv2.imshow(
        "One-Hand Sign Collection",
        frame
    )


    # ==============================
    # KEYBOARD
    # ==============================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("s"):

        if not started:

            started = True

            print()
            print("Starting collection...")


    elif key == ord("q"):

        break


    # ==============================
    # FINISHED
    # ==============================

    if count >= SAMPLES:

        print()
        print()
        print("=" * 50)
        print("COLLECTION COMPLETE")
        print("Sign:", sign_name)
        print("Samples:", count)
        print("Saved to:", OUTPUT_FILE)
        print("=" * 50)

        time.sleep(2)

        break


# ==============================
# CLEANUP
# ==============================

cap.release()
cv2.destroyAllWindows()
landmarker.close()