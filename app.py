
import streamlit as st
import streamlit.components.v2 as components

st.set_page_config(
    page_title="Smart Step Counter",
    page_icon="🚶",
    layout="centered"
)

st.title("🚶 Smart Step Counter")
st.write("Automatically track your walking activity.")

if "steps" not in st.session_state:
    st.session_state.steps = 0

HTML = """
<div>
    <button id="start">Start Walking</button>
    <button id="stop">Stop Tracking</button>
    <p id="status">Tracking stopped</p>
    <h2>Detected steps: <span id="count">0</span></h2>
</div>
"""

JS = """
export default function(component) {
    const { setStateValue, parentElement } = component;

    const start = parentElement.querySelector("#start");
    const stop = parentElement.querySelector("#stop");
    const countDisplay = parentElement.querySelector("#count");
    const status = parentElement.querySelector("#status");

    let steps = 0;
    let active = false;
    let baseline = null;
    let above = false;
    let lastStep = 0;

    function detect(event) {
        if (!active) return;

        const a = event.accelerationIncludingGravity;
        if (!a || a.x == null || a.y == null || a.z == null)
            return;

        const magnitude = Math.sqrt(
            a.x*a.x + a.y*a.y + a.z*a.z
        );

        if (baseline === null) {
            baseline = magnitude;
            return;
        }

        baseline = baseline * 0.9 + magnitude * 0.1;
        const movement = Math.abs(magnitude - baseline);
        const now = Date.now();

        if (movement > 1.3 && !above && now-lastStep > 350) {
            steps++;
            lastStep = now;
            above = true;

            countDisplay.textContent = steps;
            setStateValue("steps", steps);
        }

        if (movement < 0.65) above = false;
    }

    start.onclick = () => {
        if (!window.isSecureContext) {
            status.textContent = "HTTPS connection required.";
            return;
        }

        if (!("DeviceMotionEvent" in window)) {
            status.textContent = "Motion sensor unavailable.";
            return;
        }

        active = true;
        baseline = null;
        above = false;

        window.addEventListener("devicemotion", detect);
        status.textContent = "Tracking active. Start walking!";
    };

    stop.onclick = () => {
        active = false;
        window.removeEventListener("devicemotion", detect);
        status.textContent = "Tracking stopped.";
    };

    return () => {
        active = false;
        window.removeEventListener("devicemotion", detect);
    };
}
"""

sensor = components.component(
    "step_sensor",
    html=HTML,
    js=JS
)

result = sensor(
    key="step_sensor",
    on_steps_change=lambda: None
)

if result.steps is not None:
    st.session_state.steps = max(
        0, int(result.steps)
    )

steps = st.session_state.steps

st.metric("Steps walked today", steps)

distance = steps * 0.0007
calories = steps * 0.04
progress = min(steps / 10000, 1.0)

st.progress(progress)

st.write(f"Daily goal: {steps}/10,000 steps")
st.write(f"Estimated distance: {distance:.2f} km")
st.write(f"Estimated calories: {calories:.1f} kcal")

if steps >= 10000:
    st.success("Congratulations! Daily goal achieved!")
else:
    st.info("Keep going! You're making progress.")

