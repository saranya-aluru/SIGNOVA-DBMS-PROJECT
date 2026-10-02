import { useEffect, useRef, useState } from "react";

function CameraStage({ onRecognized }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const processingRef = useRef(false);

  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");
  const [lastSign, setLastSign] = useState("");
  const [handCount, setHandCount] = useState(0);

  const startCamera = async () => {
    try {
      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;

        await videoRef.current.play();
      }

      setCameraOn(true);
    } catch (err) {
      console.error("Camera error:", err);

      setError(
        "Camera access could not be started. Please allow camera permission."
      );
    }
  };

  const stopCamera = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    processingRef.current = false;

    setCameraOn(false);
    setHandCount(0);
  };

  const recognizeFrame = async () => {
    if (processingRef.current) {
      return;
    }

    if (
      !videoRef.current ||
      !canvasRef.current ||
      videoRef.current.readyState < 2
    ) {
      return;
    }

    processingRef.current = true;

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      const width = video.videoWidth;
      const height = video.videoHeight;

      if (!width || !height) {
        processingRef.current = false;
        return;
      }

      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext("2d");

      ctx.drawImage(
        video,
        0,
        0,
        width,
        height
      );

      /*
       * Convert the camera frame into a Base64 data URL.
       *
       * The Signova backend expects:
       *
       * {
       *   "image": "data:image/jpeg;base64,..."
       * }
       */

      const imageData = canvas.toDataURL(
        "image/jpeg",
        0.8
      );

      const response = await fetch(
        "http://127.0.0.1:5000/recognize",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            image: imageData,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const data = await response.json();

      console.log("Recognition response:", data);

      /*
       * Backend returns:
       *
       * success
       * sign
       * word
       * hand_count
       * distance
       * sign_info
       */

      setHandCount(
        data.hand_count || 0
      );

      if (
        data.success &&
        data.sign
      ) {
        const recognizedSign =
          data.word ||
          data.sign;

        setLastSign(
          recognizedSign
        );

        if (onRecognized) {
          onRecognized(
            recognizedSign
          );
        }
      }
    } catch (err) {
      console.error(
        "Recognition request failed:",
        err
      );

      /*
       * Don't constantly display the error
       * while the backend is starting.
       */
    } finally {
      processingRef.current = false;
    }
  };

  useEffect(() => {
    startCamera();

    return () => {
      stopCamera();
    };
  }, []);

  useEffect(() => {
    if (!cameraOn) {
      return;
    }

    intervalRef.current = setInterval(
      recognizeFrame,
      700
    );

    return () => {
      if (intervalRef.current) {
        clearInterval(
          intervalRef.current
        );

        intervalRef.current = null;
      }
    };
  }, [cameraOn]);

  return (
    <div className="camera-card">

      <div className="camera-card-header">

        <div className="camera-title">
          <div className="camera-title-icon">
            Camera
          </div>

          <span>
            Camera Input
          </span>
        </div>

        <div className="camera-live">

          <span></span>

          {cameraOn
            ? "Live"
            : "Offline"}

        </div>

      </div>

      <div className="camera-window">

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
        />

        {!cameraOn && (
          <div className="camera-off">

            <h3>
              Camera is off
            </h3>

            <p>
              Start the camera to begin
              recognition.
            </p>

            <button
              onClick={startCamera}
            >
              Start Camera
            </button>

          </div>
        )}

        {cameraOn && (
          <div className="camera-hand-status">
            {handCount > 0
              ? `${handCount} hand${
                  handCount > 1
                    ? "s"
                    : ""
                } detected`
              : "Show your hand to the camera"}
          </div>
        )}

      </div>

      <canvas
        ref={canvasRef}
        style={{
          display: "none",
        }}
      />

      <div className="camera-controls">

        <button
          className="stop-button"
          onClick={
            cameraOn
              ? stopCamera
              : startCamera
          }
        >
          {cameraOn
            ? "Stop Camera"
            : "Start Camera"}
        </button>

        <button
          className="snapshot-button"
          onClick={recognizeFrame}
          disabled={!cameraOn}
        >
          Recognize Now
        </button>

      </div>

      {lastSign && (
        <div className="camera-recognition-note">
          Latest recognition:{" "}
          <strong>
            {lastSign}
          </strong>
        </div>
      )}

      {error && (
        <div className="camera-error">
          {error}
        </div>
      )}

    </div>
  );
}

export default CameraStage;