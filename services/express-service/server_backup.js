const express = require("express");
const cors = require("cors");
const { Kafka } = require("kafkajs");

const app = express();

const PORT = 3001;

// ============================================================
// MIDDLEWARE
// ============================================================

app.use(cors());
app.use(express.json());


// ============================================================
// KAFKA
// ============================================================

const kafka = new Kafka({
    clientId: "signova-express",
    brokers: ["localhost:9092"]
});

const producer = kafka.producer();

const KAFKA_TOPIC = "sign-recognition";


// ============================================================
// KAFKA CONNECTION
// ============================================================

async function startKafka() {

    try {

        await producer.connect();

        console.log("Kafka Producer : Connected");

    } catch (error) {

        console.error(
            "Kafka connection failed:",
            error.message
        );

    }

}

startKafka();


// ============================================================
// HEALTH
// ============================================================

app.get("/api/health", (req, res) => {

    res.json({
        success: true,
        service: "Signova Express Service",
        status: "running"
    });

});


// ============================================================
// ARCHITECTURE
// ============================================================

app.get("/api/architecture", (req, res) => {

    res.json({

        success: true,

        architecture: {

            frontend: "React",

            recognition_backend:
                "Python Flask + MediaPipe + Machine Learning",

            database:
                "MySQL",

            api_service:
                "Node.js + Express",

            message_broker:
                "Apache Kafka"

        }

    });

});


// ============================================================
// SIGNS SUMMARY
// ============================================================

app.get("/api/signs-summary", (req, res) => {

    res.json({

        success: true,

        service: "Signova",

        message:
            "Sign recognition data can be processed through the Express service.",

        kafka_topic:
            KAFKA_TOPIC

    });

});


// ============================================================
// KAFKA EVENT API
// ============================================================

app.post("/api/events", async (req, res) => {

    try {

        const {
            sign,
            word,
            hand_count
        } = req.body;


        if (!sign) {

            return res.status(400).json({

                success: false,

                error:
                    "Sign is required"

            });

        }


        const event = {

            sign: sign,

            word: word || sign,

            hand_count:
                hand_count || 0,

            timestamp:
                new Date().toISOString()

        };


        await producer.send({

            topic: KAFKA_TOPIC,

            messages: [

                {
                    value:
                        JSON.stringify(event)
                }

            ]

        });


        console.log(
            "Kafka event sent:",
            event
        );


        res.json({

            success: true,

            message:
                "Recognition event sent to Kafka",

            event: event

        });


    } catch (error) {

        console.error(
            "Kafka event error:",
            error
        );


        res.status(500).json({

            success: false,

            error:
                error.message

        });

    }

});


// ============================================================
// KAFKA STATUS
// ============================================================

app.get("/api/kafka-status", (req, res) => {

    res.json({

        success: true,

        kafka: {

            broker:
                "localhost:9092",

            topic:
                KAFKA_TOPIC,

            producer:
                "Signova Express Producer"

        }

    });

});


// ============================================================
// START SERVER
// ============================================================

app.listen(PORT, () => {

    console.log("");

    console.log(
        "======================================"
    );

    console.log(
        "       SIGNOVA EXPRESS SERVICE"
    );

    console.log(
        "======================================"
    );

    console.log(
        "Technology : Node.js + Express"
    );

    console.log(
        "Server     : http://127.0.0.1:3001"
    );

    console.log(
        "Health     : http://127.0.0.1:3001/api/health"
    );

    console.log(
        "Architecture: http://127.0.0.1:3001/api/architecture"
    );

    console.log(
        "Signs      : http://127.0.0.1:3001/api/signs-summary"
    );

    console.log(
        "Kafka      : localhost:9092"
    );

    console.log(
        "Kafka Topic: sign-recognition"
    );

    console.log(
        "======================================"
    );

    console.log("");

});