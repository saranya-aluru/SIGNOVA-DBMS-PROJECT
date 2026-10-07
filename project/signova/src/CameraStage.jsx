import { useEffect, useRef, useState } from "react";

function CameraStage({ onRecognized }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const busyRef = useRef(false);

  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");
  const [lastSign, setLastSign] = useState("");

  // ============================================================
  // START CAMERA
  // ============================================================

  const startCamera = async () => {
    try {
      setError("");

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser does not support camera access.");
        return;
      }

      // Stop any previous stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: {
            ideal: 1280,
          },
          height: {
            ideal: 720,
          },
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

      console.log("Camera started successfully");
    } catch (err) {
      console.error("Camera error:", err);

      setCameraOn(false);

      setError(
        "Camera access could not be started. Please allow camera permission."
      );
    }
  };

  // ============================================================
  // STOP CAMERA
  // ============================================================

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

    setCameraOn(false);

    console.log("Camera stopped");
  };

  // ============================================================
  // RECOGNIZE FRAME
  // ============================================================

  const recognizeFrame = async () => {
    if (busyRef.current) {
      return;
    }

    if (
      !videoRef.current ||
      !canvasRef.current ||
      videoRef.current.readyState < 2
    ) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (
      video.videoWidth === 0 ||
      video.videoHeight === 0
    ) {
      return;
    }

    busyRef.current = true;

    try {
      // --------------------------------------------------------
      // Set canvas size
      // --------------------------------------------------------

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext("2d");

      if (!ctx) {
        console.error("Could not get canvas context");
        return;
      }

      // --------------------------------------------------------
      // Copy camera frame to canvas
      // --------------------------------------------------------

      ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
      );

      // --------------------------------------------------------
      // Convert frame to base64 JPEG
      // --------------------------------------------------------

      const imageData = canvas.toDataURL(
        "image/jpeg",
        0.85
      );

      // --------------------------------------------------------
      // Send JSON to Flask
      //
      // IMPORTANT:
      // Flask expects:
      //
      // request.get_json()
      // data["image"]
      //
      // --------------------------------------------------------

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

      // --------------------------------------------------------
      // Check HTTP response
      // --------------------------------------------------------

      if (!response.ok) {
        console.error(
          "Recognition server returned HTTP status:",
          response.status
        );

        return;
      }

      // --------------------------------------------------------
      // Read JSON response
      // --------------------------------------------------------

      const data = await response.json();

      console.log(
        "Recognition response:",
        data
      );

      // --------------------------------------------------------
      // Handle backend errors
      // --------------------------------------------------------

      if (data.success === false) {
        console.error(
          "Recognition backend error:",
          data.error
        );

        return;
      }

      // --------------------------------------------------------
      // Get detected hand count
      // --------------------------------------------------------

      const handCount = data.hand_count;

      console.log(
        "Hands detected:",
        handCount
      );

      // --------------------------------------------------------
      // Get recognized sign
      // --------------------------------------------------------

      const sign =
        data.sign ||
        data.label ||
        data.prediction ||
        data.word ||
        "";

      // --------------------------------------------------------
      // Update UI
      // --------------------------------------------------------

      if (sign) {
        setLastSign(sign);

        if (onRecognized) {
          onRecognized(sign);
        }
      }
    } catch (err) {
      console.error(
        "Recognition request failed:",
        err
      );
    } finally {
      busyRef.current = false;
    }
  };

  // ============================================================
  // START CAMERA WHEN COMPONENT LOADS
  // ============================================================

  useEffect(() => {
    startCamera();

    return () => {
      stopCamera();
    };
  }, []);

  // ============================================================
  // RECOGNITION LOOP
  // ============================================================

  useEffect(() => {
    if (!cameraOn) {
      return;
    }

    console.log(
      "Starting recognition loop..."
    );

    intervalRef.current = setInterval(() => {
      recognizeFrame();
    }, 900);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [cameraOn]);

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="camera-card">

      {/* ======================================================
          HEADER
      ====================================================== */}

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


      {/* ======================================================
          CAMERA
      ====================================================== */}

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
              Start the camera to begin recognition.
            </p>

            <button
              onClick={startCamera}
            >
              Start Camera
            </button>

          </div>
        )}

      </div>


      {/* ======================================================
          HIDDEN CANVAS
      ====================================================== */}

      <canvas
        ref={canvasRef}
        style={{
          display: "none",
        }}
      />


      {/* ======================================================
          CONTROLS
      ====================================================== */}

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
          Take Snapshot
        </button>

      </div>


      {/* ======================================================
          LAST RECOGNIZED SIGN
      ====================================================== */}

      {lastSign && (
        <div className="camera-recognition-note">

          Latest camera result:

          <strong>
            {" "}{lastSign}
          </strong>

        </div>
      )}


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="camera-error">
          {error}
        </div>
      )}

    </div>
  );
}

export default CameraStage;