import "./styles.css";

const signs = [
  {
    name: "Hello",
    key: "HELLO",
    meaning: "A friendly greeting used when meeting someone.",
    color: "pink"
  },
  {
    name: "Yes",
    key: "YES",
    meaning: "Used to express agreement or confirmation.",
    color: "mint"
  },
  {
    name: "No",
    key: "NO",
    meaning: "Used to express disagreement or refusal.",
    color: "lavender"
  },
  {
    name: "Please",
    key: "PLEASE",
    meaning: "Used when making a polite request.",
    color: "blue"
  },
  {
    name: "Thank You",
    key: "THANK_YOU",
    meaning: "Used to express gratitude or appreciation.",
    color: "yellow"
  },
  {
    name: "I Love You",
    key: "ILOVEYOU",
    meaning: "Used to express love and affection.",
    color: "rose"
  },
  {
    name: "Namaste",
    key: "NAMASTE",
    meaning: "A traditional Indian greeting.",
    color: "peach"
  },
  {
    name: "House",
    key: "HOUSE",
    meaning: "A place where a person lives.",
    color: "green"
  }
];

function Signs() {

  return (
    <div className="page">

      <div className="page-heading">

        <div className="eyebrow">
          <span className="eyebrow-dot"></span>
          ISL SIGN LIBRARY
        </div>

        <h1>Learn the signs.</h1>

        <p>
          Explore the vocabulary currently supported by
          the Signova recognition system.
        </p>

      </div>


      <div className="sign-library">

        {signs.map((sign) => (

          <div
            className={`sign-library-card ${sign.color}`}
            key={sign.key}
          >

            <div className="sign-card-number">
              {sign.key}
            </div>

            <h2>{sign.name}</h2>

            <p>{sign.meaning}</p>

          </div>

        ))}

      </div>

    </div>
  );
}

export default Signs;