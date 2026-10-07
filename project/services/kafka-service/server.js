const express = require("express");
const cors = require("cors");
const { Kafka } = require("kafkajs");

const app = express();
const PORT = 3002;

app.use(cors());
app.use(express.json());

const kafka = new Kafka({
    clientId: "signova-recognition-service",
    brokers: ["localhost:9092"]
});

const producer = kafka.producer();


// ============================================================
// HOME
// ============================================================

app.get("/", (req, res) => {
    res.json({
        success: true,
        service: "Signova Kafka Recognition Service",
        status: "running"
    });
});


// ============================================================
// HEALTH
// ============================================================

app.get("/api/health", (req, res) => {
    res.json({
        success: true,
        service: "kafka-service",
        status: "healthy"
    });
});


// ============================================================
// PUBLISH RECOGNITION EVENT
// ============================================================

app.post("/api/recognition-event", async (req, res) => {

    try {

        const {
            sign,
            hand_count = 1
        } = req.body;

        if (!sign) {
            return res.status(400).json({
                success: false,
                error: "Sign is required"
            });
        }

        const event = {
            sign: sign,
            hand_count: hand_count,
            timestamp: new Date().toISOString()
        };

        await producer.send({
            topic: "sign-recognition",
            messages: [
                {
                    value: JSON.stringify(event)
                }
            ]
        });

        console.log(
            "Recognition event published:",
            event
        );

        res.json({
            success: true,
            message: "Recognition event published",
            event: event
        });

    } catch (error) {

        console.error(
            "Kafka error:",
            error.message
        );

        res.status(500).json({
            success: false,
            error: "Could not publish Kafka event"
        });
    }
});


// ============================================================
// START
// ============================================================

async function startServer() {

    try {

        await producer.connect();

        console.log(
            "Kafka producer connected"
        );

        app.listen(PORT, () => {

            console.log("");
            console.log("======================================");
            console.log(" SIGNOVA KAFKA SERVICE");
            console.log("======================================");
            console.log(
                `Server: http://127.0.0.1:${PORT}`
            );
            console.log(
                "Topic : sign-recognition"
            );
            console.log("======================================");
            console.log("");

        });

    } catch (error) {

        console.error(
            "Kafka connection failed:"
        );

        console.error(
            error.message
        );
    }
}

startServer();