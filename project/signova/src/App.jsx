import { useState } from "react";
import "./styles.css";
import CameraStage from "./CameraStage";
import Signs from "./Signs";

const signMeanings = {
  HELLO: "A friendly greeting used when meeting someone.",
  YES: "Used to express agreement or confirmation.",
  NO: "Used to express disagreement or refusal.",
  PLEASE: "Used when making a polite request.",
  THANK_YOU: "Used to express gratitude or appreciation.",
  ILOVEYOU: "Used to express love and affection.",
  NAMASTE: "A traditional Indian greeting.",
  HOUSE: "A place where a person lives."
};

const displayName = (sign) => {
  if (!sign) return "";
  if (sign === "ILOVEYOU") return "I Love You";
  return sign
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
};

function Icon({ type, size = 22 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  };

  if (type === "camera") {
    return (
      <svg {...common}>
        <rect x="3" y="6" width="18" height="14" rx="3" />
        <path d="M8 6l1.5-2h5L16 6" />
        <circle cx="12" cy="13" r="3.5" />
      </svg>
    );
  }

  if (type === "book") {
    return (
      <svg {...common}>
        <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z" />
        <path d="M4 5.5v15" />
        <path d="M8 7h8" />
      </svg>
    );
  }

  if (type === "history") {
    return (
      <svg {...common}>
        <path d="M3 12a9 9 0 1 0 3-6.7" />
        <path d="M3 4v5h5" />
        <path d="M12 7v5l3 2" />
      </svg>
    );
  }

  if (type === "info") {
    return (
      <svg {...common}>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 10v6" />
        <circle cx="12" cy="7" r=".7" fill="currentColor" />
      </svg>
    );
  }

  if (type === "sparkle") {
    return (
      <svg {...common}>
        <path d="M12 2l1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z" />
        <path d="M19 16l.6 2.4L22 19l-2.4.6L19 22l-.6-2.4L16 19l2.4-.6z" />
      </svg>
    );
  }

  if (type === "trash") {
    return (
      <svg {...common}>
        <path d="M4 7h16" />
        <path d="M9 7V4h6v3" />
        <path d="M7 7l1 13h8l1-13" />
        <path d="M10 11v5M14 11v5" />
      </svg>
    );
  }

  return null;
}

function App() {
  const [activePage, setActivePage] = useState("recognition");
  const [history, setHistory] = useState([]);

  const addHistory = (sign) => {
    if (!sign || sign === "UNKNOWN") return;

    const item = {
      id: Date.now(),
      sign,
      time: new Date().toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      })
    };

    setHistory((old) => [item, ...old].slice(0, 30));
  };

  return (
    <div className="app">

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-logo">
            <span>S</span>
          </div>

          <div>
            <div className="brand-name">Signova</div>
            <div className="brand-subtitle">
              Sign Language Recognition
            </div>
          </div>
        </div>

        <nav className="navigation">

          <button
            className={`nav-item ${
              activePage === "recognition" ? "active" : ""
            }`}
            onClick={() => setActivePage("recognition")}
          >
            <Icon type="camera" />
            <span>Recognition</span>
          </button>

          <button
            className={`nav-item ${
              activePage === "signs" ? "active" : ""
            }`}
            onClick={() => setActivePage("signs")}
          >
            <Icon type="book" />
            <span>Signs</span>
          </button>

          <button
            className={`nav-item ${
              activePage === "history" ? "active" : ""
            }`}
            onClick={() => setActivePage("history")}
          >
            <Icon type="history" />
            <span>Translation History</span>
          </button>

          <button
            className={`nav-item ${
              activePage === "about" ? "active" : ""
            }`}
            onClick={() => setActivePage("about")}
          >
            <Icon type="info" />
            <span>About</span>
          </button>

        </nav>

        <div className="sidebar-bottom">

          <div className="sidebar-line"></div>

          <p>BRIDGING COMMUNICATION</p>
          <p>THROUGH TECHNOLOGY</p>

          <div className="small-flower">
            <span></span>
            <span></span>
            <span></span>
          </div>

        </div>

      </aside>

      <main className="main-content">

        {activePage === "recognition" && (
          <RecognitionPage
            onRecognized={addHistory}
            history={history}
            setActivePage={setActivePage}
          />
        )}

        {activePage === "signs" && (
          <Signs />
        )}

        {activePage === "history" && (
          <HistoryPage
            history={history}
            setHistory={setHistory}
          />
        )}

        {activePage === "about" && (
          <AboutPage />
        )}

      </main>
    </div>
  );
}


function RecognitionPage({
  onRecognized,
  history,
  setActivePage
}) {
  const [detectedSign, setDetectedSign] = useState("");
  const [sentence, setSentence] = useState([]);

  const handleRecognition = (sign) => {
    setDetectedSign(sign);

    if (sign && sign !== "UNKNOWN") {
      setSentence((old) => {
        const last = old[old.length - 1];

        if (last === sign) {
          return old;
        }

        return [...old, sign];
      });

      onRecognized(sign);
    }
  };

  const clearSentence = () => {
    setSentence([]);
  };

  return (
    <div className="page">

      <div className="top-header">

        <div>
          <div className="eyebrow">
            <span className="eyebrow-dot"></span>
            LIVE RECOGNITION
          </div>

          <h1>Sign Language Recognition</h1>

          <p className="header-description">
            Use your camera to recognize supported sign language
            words in real time.
          </p>
        </div>

        <div className="system-ready">
          <span></span>
          System Ready
        </div>

      </div>

      <div className="recognition-layout">

        <div>

          <CameraStage
            onRecognized={handleRecognition}
          />

          <div className="supported-section">

            <div className="section-heading">
              <div>
                <h3>Supported Signs</h3>
                <p>
                  Words currently available in the recognition system.
                </p>
              </div>

              <button onClick={() => setActivePage("signs")}>
                View All
              </button>
            </div>

            <div className="mini-sign-grid">

              {[
                ["HELLO", "pink"],
                ["YES", "mint"],
                ["NO", "lavender"],
                ["PLEASE", "blue"],
                ["THANK_YOU", "yellow"],
                ["ILOVEYOU", "rose"]
              ].map(([sign, color]) => (
                <div
                  className={`mini-sign-card ${color}`}
                  key={sign}
                >
                  <h4>{displayName(sign)}</h4>
                  <p>{signMeanings[sign]}</p>
                </div>
              ))}

            </div>

          </div>

        </div>


        <div className="right-column">

          <div className="detected-card">

            <div className="card-heading">
              <Icon type="sparkle" />
              <span>Detected Sign</span>
            </div>

            {detectedSign ? (
              <>
                <div className="detected-word">
                  {displayName(detectedSign)}
                </div>

                <p className="detected-meaning">
                  {signMeanings[detectedSign] ||
                    "Recognized sign from the current model."}
                </p>

                <div className="meaning-box">
                  <strong>Meaning</strong>
                  <span>
                    {signMeanings[detectedSign] ||
                      "Recognized sign"}
                  </span>
                </div>
              </>
            ) : (
              <>
                <div className="detected-word muted">
                  Waiting...
                </div>

                <p className="detected-meaning">
                  Show a supported sign in front of the camera.
                </p>
              </>
            )}

          </div>


          <div className="sentence-card">

            <div className="card-heading sentence-heading">

              <div className="heading-left">
                <Icon type="book" />
                <span>Current Sentence</span>
              </div>

              <button
                className="clear-button"
                onClick={clearSentence}
              >
                <Icon type="trash" size={17} />
                Clear
              </button>

            </div>

            <div className="sentence-display">

              {sentence.length > 0
                ? sentence
                    .map((item) => displayName(item))
                    .join(" ")
                : "Recognized words will appear here."}

            </div>

          </div>


          <div className="recent-card">

            <div className="card-heading sentence-heading">

              <div className="heading-left">
                <Icon type="history" />
                <span>Translation History</span>
              </div>

              <button
                className="text-button"
                onClick={() => setActivePage("history")}
              >
                View All
              </button>

            </div>

            {history.length === 0 ? (
              <p className="empty-history">
                No translations recorded yet.
              </p>
            ) : (
              <div className="recent-list">
                {history.slice(0, 4).map((item) => (
                  <div
                    className="recent-item"
                    key={item.id}
                  >
                    <span>{item.time}</span>
                    <strong>{displayName(item.sign)}</strong>
                  </div>
                ))}
              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}


function HistoryPage({ history, setHistory }) {

  const clearHistory = () => {
    setHistory([]);
  };

  return (
    <div className="page">

      <div className="page-heading">

        <div className="eyebrow">
          <span className="eyebrow-dot"></span>
          TRANSLATION RECORD
        </div>

        <h1>Translation History</h1>

        <p>
          Previously recognized signs are listed here for reference.
        </p>

      </div>


      <div className="history-container">

        <div className="history-header">

          <div>
            <h2>Recent Translations</h2>
            <p>
              {history.length} translation
              {history.length !== 1 ? "s" : ""} recorded
            </p>
          </div>

          {history.length > 0 && (
            <button
              className="outline-button"
              onClick={clearHistory}
            >
              Clear History
            </button>
          )}

        </div>


        {history.length === 0 ? (
          <div className="empty-history-large">
            <Icon type="history" size={36} />

            <h3>No translation history</h3>

            <p>
              Recognized signs will appear here after using
              the camera.
            </p>
          </div>
        ) : (
          <div className="history-table">

            <div className="table-head">
              <span>Time</span>
              <span>Detected Sign</span>
              <span>Meaning</span>
            </div>

            {history.map((item) => (
              <div
                className="table-row"
                key={item.id}
              >
                <span>{item.time}</span>

                <strong>
                  {displayName(item.sign)}
                </strong>

                <span>
                  {signMeanings[item.sign] ||
                    "Recognized sign"}
                </span>
              </div>
            ))}

          </div>
        )}

      </div>

    </div>
  );
}


function AboutPage() {

  return (
    <div className="page">

      <div className="page-heading">

        <div className="eyebrow">
          <span className="eyebrow-dot"></span>
          ABOUT THE PROJECT
        </div>

        <h1>About Signova</h1>

        <p>
          A sign language recognition system designed to
          translate selected hand signs into readable words.
        </p>

      </div>


      <div className="about-grid">

        <div className="about-card pink-card">
          <h3>Computer Vision</h3>

          <p>
            Camera input is processed using hand landmark
            detection to identify the position of the hand.
          </p>
        </div>

        <div className="about-card mint-card">
          <h3>Machine Learning</h3>

          <p>
            A trained classification model is used to map
            extracted hand features to supported sign labels.
          </p>
        </div>

        <div className="about-card blue-card">
          <h3>Backend API</h3>

          <p>
            Flask provides the API that connects the recognition
            model with the React frontend.
          </p>
        </div>

        <div className="about-card yellow-card">
          <h3>Database</h3>

          <p>
            MySQL can store sign information and translation
            records used by the application.
          </p>
        </div>

      </div>

    </div>
  );
}


export default App;