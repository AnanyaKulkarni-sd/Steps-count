
from flask import Flask, render_template_string, request

app = Flask(__name__)

steps_data = 0
daily_goal = 10000

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Step Counter</title>
    <style>
        body {
            font-family: Arial;
            background: #eef2ff;
            text-align: center;
            padding: 40px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 450px;
            margin: auto;
            box-shadow: 0 4px 15px #cccccc;
        }

        h1 { color: #4338ca; }

        input, button {
            padding: 12px;
            margin: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }

        button {
            background: #4f46e5;
            color: white;
            cursor: pointer;
        }

        .stats {
            background: #eef2ff;
            padding: 15px;
            margin-top: 15px;
            border-radius: 10px;
        }

        .progress {
            background: #ddd;
            border-radius: 10px;
            height: 20px;
        }

        .bar {
            background: #4f46e5;
            height: 20px;
            border-radius: 10px;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>🚶 Smart Step Counter</h1>
    <p>Track your daily walking progress!</p>

    <form method="POST">
        <input type="number" name="steps"
               placeholder="Enter your steps"
               min="0" required>
        <br>
        <button type="submit">Update Steps</button>
    </form>

    <div class="stats">
        <h2>{{ steps }}</h2>
        <p>Steps Walked Today</p>

        <div class="progress">
            <div class="bar" style="width: {{ progress }}%;"></div>
        </div>

        <p>{{ progress }}% of daily goal</p>
    </div>

    <div class="stats">
        <h3>Distance: {{ distance }} km</h3>
        <h3>Estimated Calories: {{ calories }}</h3>
        <h3>Daily Goal: 10,000 steps</h3>
    </div>

    <h3>{{ message }}</h3>

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    global steps_data

    if request.method == "POST":
        steps_data = int(request.form["steps"])

    progress = min(round((steps_data / daily_goal) * 100), 100)

    distance = round(steps_data * 0.0007, 2)
    calories = round(steps_data * 0.04, 1)

    if steps_data >= daily_goal:
        message = "Congratulations! Daily goal achieved!"
    else:
        message = "Keep walking! You can do it!"

    return render_template_string(
        HTML,
        steps=steps_data,
        progress=progress,
        distance=distance,
        calories=calories,
        message=message
    )

if __name__ == "__main__":
    app.run(debug=True)
