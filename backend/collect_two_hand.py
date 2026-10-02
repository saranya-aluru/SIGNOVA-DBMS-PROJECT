import cv2
import mediapipe as mp
import csv
import time


# ============================================================
# CHANGE ONLY THIS FOR EACH SIGN
# ============================================================

LABEL = "HOUSE"

# ============================================================

OUTPUT_FILE = LABEL + "_2hand.csv"
SAMPLES = 150


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

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


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()


# ============================================================
# FULLSCREEN WINDOW
# ============================================================

WINDOW_NAME = "Two-Hand Data Collection"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ============================================================
# VARIABLES
# ============================================================

collecting = False
sample_count = 0


# ============================================================
# GET LEFT AND RIGHT HANDS
# ============================================================

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


# ============================================================
# MEDIAPIPE
# ============================================================

with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        # ----------------------------------------------------
        # READ CAMERA
        # ----------------------------------------------------

        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break


        # ----------------------------------------------------
        # MIRROR CAMERA
        # ----------------------------------------------------

        frame = cv2.flip(frame, 1)


        # ----------------------------------------------------
        # CONVERT FOR MEDIAPIPE
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        # ----------------------------------------------------
        # DETECT HANDS
        # ----------------------------------------------------

        result = landmarker.detect(mp_image)

        hand_count = len(result.hand_landmarks)

        left_hand, right_hand = get_left_right_hands(result)


        # ====================================================
        # DISPLAY SIGN NAME
        # ====================================================

        cv2.putText(
            frame,
            "SIGN: " + LABEL,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 255),
            3
        )


        # ====================================================
        # DISPLAY HAND COUNT
        # ====================================================

        cv2.putText(
            frame,
            "Hands: " + str(hand_count),
            (30, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3
        )


        # ====================================================
        # COLLECTION
        # ====================================================

        if collecting:

            cv2.putText(
                frame,
                "COLLECTING: "
                + str(sample_count)
                + "/"
                + str(SAMPLES),
                (30, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )


            # ------------------------------------------------
            # BOTH HANDS MUST BE PRESENT
            # ------------------------------------------------

            if left_hand is not None and right_hand is not None:

                row = []


                # ============================================
                # LEFT HAND FIRST
                # ============================================

                for landmark in left_hand:

                    row.extend([
                        landmark.x,
                        landmark.y,
                        landmark.z
                    ])


                # ============================================
                # RIGHT HAND SECOND
                # ============================================

                for landmark in right_hand:

                    row.extend([
                        landmark.x,
                        landmark.y,
                        landmark.z
                    ])


                # ============================================
                # SAVE SAMPLE
                # ============================================

                with open(
                    OUTPUT_FILE,
                    "a",
                    newline=""
                ) as file:

                    writer = csv.writer(file)

                    writer.writerow(row)


                sample_count += 1

                time.sleep(0.03)


                # ============================================
                # FINISHED
                # ============================================

                if sample_count >= SAMPLES:

                    collecting = False

                    print()
                    print("========================================")
                    print("COLLECTION COMPLETE")
                    print("========================================")
                    print("Sign    :", LABEL)
                    print("Samples :", sample_count)
                    print("File    :", OUTPUT_FILE)
                    print("========================================")
                    print()

            else:

                cv2.putText(
                    frame,
                    "BOTH HANDS NOT DETECTED!",
                    (30, 195),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3
                )


        # ====================================================
        # WAITING TO START
        # ====================================================

        else:

            if sample_count >= SAMPLES:

                cv2.putText(
                    frame,
                    "DONE!",
                    (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 0),
                    3
                )

                cv2.putText(
                    frame,
                    "Press Q to close",
                    (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),
                    2
                )

            elif hand_count == 2:

                cv2.putText(
                    frame,
                    "Press S to start",
                    (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    3
                )

            else:

                cv2.putText(
                    frame,
                    "Show BOTH hands",
                    (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    3
                )


        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            WINDOW_NAME,
            frame
        )


        # ====================================================
        # KEYBOARD
        # ====================================================

        key = cv2.waitKey(1) & 0xFF


        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        if key == ord("s"):

            if left_hand is not None and right_hand is not None:

                # Start fresh
                sample_count = 0

                collecting = True

                # Delete old file contents
                open(
                    OUTPUT_FILE,
                    "w"
                ).close()

                print()
                print("Started collecting:", LABEL)
                print("Please perform the sign...")
                print()

            else:

                print(
                    "Please show BOTH hands before pressing S."
                )


        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        elif key == ord("q"):

            print("Exiting...")

            break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print()
print("Program closed.")