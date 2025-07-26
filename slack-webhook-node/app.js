require("dotenv").config();
const axios =  require("axios");

const sendSlackMessage = async text => {
    try {
        const webhookURL = process.env.SLACK_WEBHOOK_URL;

        const payload = {
            text:text || "Hello from Node.js!"
        };


        const response = await axios.post(webhookURL, payload);
        console.log("Message sent:", response.status);
    } catch (error) {
        console.error("Error sending message:", error);
    }
}
