
from flask import Flask, render_template_string, request, jsonify, session

app = Flask(__name__)
app.secret_key = "step-counter-demo-key"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Step Counter</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2ff;
            text-align: center;
            padding: 25px;
        }

        .container {
            background: white;
            padding: 25px;
            border-radius: 18px;
            max-width: 420px;
            margin: auto;
            box-shadow: 0 4px 15px #cccccc;
        }

        h1 { color: #4338ca; }

        .steps {
            font-size: 55px;
            font-weight: bold;
            color: #4338ca;
            margin: 20px;
        }

        .stats {
            background: #eef2ff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 12px;
        }

        button {
            padding: 13px 20px;
            margin: 7px;
            border: none;
            border-radius: 9px;
            background: #4f46e5;
            color: white;
            font-size: 15px;
            cursor: pointer;
        }

        .stop {
            background: #dc2626;
        }

        .progress {
            background: #ddd;
            height: 15px;
            border-radius: 10px;
        }

        .bar {
            background: #4f46e5;
            height: 15px;
            border-radius: 10px;
            width: 0%;
        }

        #status {
            color: #555;
            font-size: 14px;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>Smart Step Counter</h1>
    <p>Track your walking automatically!</p>

    <div class="steps" id="steps">{{ steps }}</div>
    <p>Steps walked today</p>

    <div class="progress">
        <div class="bar" id="bar"></div>
    </div>

    <p id="progressText">0% of daily goal</p>

    <button onclick="startTracking()">Start Walking</button>
    <button class="stop" onclick="stopTracking()">Stop</button>

    <p id="status">Tracking is stopped.</p>

    <div class="stats">
        <h3>Distance: <span id="distance">0</span> km</h3>
        <h3>Estimated Calories: <span id="calories">0</span> kcal</h3>
        <h3>Daily Goal: 10,000 steps</h3>
    </div>

    <button class="stop" onclick="resetSteps()">Reset Steps</button>

</div>

<script>
    let steps = Number("{{ steps }}");
    let tracking = false;
    let lastStepTime = 0;
    let baseline = null;
    let aboveThreshold = false;

    const threshold = 1.3;

    function updateDisplay() {
        document.getElementById("steps").innerText = steps;

        let progress = Math.min(steps / 10000 * 100, 100);

        document.getElementById("bar").style.width =
            progress + "%";

        document.getElementById("progressText").innerText =
            Math.round(progress) + "% of daily goal";

        document.getElementById("distance").innerText =
            (steps * 0.0007).toFixed(2);

        document.getElementById("calories").innerText =
            (steps * 0.04).toFixed(1);
    }

    async function saveSteps() {
        await fetch("/update_steps", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({steps: steps})
        });
    }

    async function startTracking() {

        if (!window.isSecureContext) {
            document.getElementById("status").innerText =
                "Please open this website using HTTPS.";
            return;
        }

        if (!("DeviceMotionEvent" in window)) {
            document.getElementById("status").innerText =
                "Motion sensors are not supported by this browser.";
            return;
        }

        tracking = true;
        baseline = null;
        aboveThreshold = false;

        window.addEventListener("devicemotion", detectSteps);

        document.getElementById("status").innerText =
            "Tracking started! Keep your phone with you while walking.";
    }

    function detectSteps(event) {

        if (!tracking) return;

        let acceleration = event.accelerationIncludingGravity;

        if (!acceleration ||
            acceleration.x === null ||
            acceleration.y === null ||
            acceleration.z === null) {
            return;
        }

        let magnitude = Math.sqrt(
            acceleration.x ** 2 +
            acceleration.y ** 2 +
            acceleration.z ** 2
        );

        if (baseline === null) {
            baseline = magnitude;
            return;
        }

        baseline = baseline * 0.9 + magnitude * 0.1;

        let movement = Math.abs(magnitude - baseline);
        let now = Date.now();

        if (movement > threshold && !aboveThreshold &&
            now - lastStepTime > 350) {

            steps++;
            lastStepTime = now;
            aboveThreshold = true;

            updateDisplay();
            saveSteps();
        }

        if (movement < threshold * 0.5) {
            aboveThreshold = false;
        }
    }

    function stopTracking() {

        tracking = false;

        window.removeEventListener("devicemotion", detectSteps);

        document.getElementById("status").innerText =
            "Tracking stopped.";
    }

    async function resetSteps() {

        stopTracking();

        steps = 0;
        updateDisplay();

        await fetch("/reset", {method: "POST"});
        
        document.getElementById("status").innerText =
            "Step count reset.";
    }

    updateDisplay();
</script>

</body>
</html>
"""

@app.route("/")
def home():
    steps = session.get("steps", 0)
    return render_template_string(HTML, steps=steps)


@app.route("/update_steps", methods=["POST"])
def update_steps():
    data = request.get_json()
    steps = max(0, int(data.get("steps", 0)))
    session["steps"] = steps
    return jsonify({"success": True, "steps": steps})


@app.route("/reset", methods=["POST"])
def reset():
    session["steps"] = 0
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

