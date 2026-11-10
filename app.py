

import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v2 as components
from datetime import date, timedelta

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Smart Step Counter",
    page_icon="🚶",
    layout="wide"
)

# ---------------- SESSION DATA ----------------

if "steps" not in st.session_state:
    st.session_state.steps = 0

if "history" not in st.session_state:
    st.session_state.history = {}

today = date.today()

# ---------------- CUSTOM THEME ----------------

st.markdown("""
<style>
.stApp {
    background-color: #050505;
    color: white;
}

header[data-testid="stHeader"] {
    background-color: #050505;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
}

h1, h2, h3, p, label {
    color: white !important;
}

[data-testid="stMetricValue"] {
    color: white;
}

[data-testid="stMetricLabel"] {
    color: #aaaaaa;
}

div.stButton > button {
    background: linear-gradient(
        90deg, #ff3030, #ff9500, #dfff00
    );
    color: black;
    border: none;
    border-radius: 25px;
    font-weight: bold;
}

[data-testid="stRadio"] label {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown("""
<h1 style="text-align:center; letter-spacing:4px;">
SMART STEP COUNTER
</h1>
<p style="text-align:center; color:#999;">
YOUR DAILY WALKING COMPANION
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- ANDROID SENSOR ----------------

HTML = """
<div style="
    background:#050505;
    color:white;
    text-align:center;
    padding:12px;
    font-family:Arial;
">

<button id="start" style="
    background:linear-gradient(90deg,#ff3030,#ff9500,#dfff00);
    color:black;
    padding:12px 28px;
    border:0;
    border-radius:25px;
    font-weight:bold;
    cursor:pointer;
">
START WALKING
</button>

<button id="stop" style="
    background:#333;
    color:white;
    padding:12px 28px;
    border:0;
    border-radius:25px;
    cursor:pointer;
">
STOP
</button>

<p id="status" style="color:#aaa;">
Tracking stopped
</p>

</div>
"""

JS = """
export default function(component) {

    const {setStateValue, parentElement} = component;

    const start = parentElement.querySelector("#start");
    const stop = parentElement.querySelector("#stop");
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

        if (
            movement > 1.3 &&
            !above &&
            now - lastStep > 350
        ) {

            steps++;
            lastStep = now;
            above = true;

            setStateValue("steps", steps);
        }

        if (movement < 0.65) {
            above = false;
        }
    }

    start.onclick = async () => {

        if (!window.isSecureContext) {
            status.textContent = "HTTPS connection required";
            return;
        }

        if (!("DeviceMotionEvent" in window)) {
            status.textContent = "Motion sensor unavailable";
            return;
        }

        if (
            typeof DeviceMotionEvent.requestPermission === "function"
        ) {
            try {

                const permission =
                    await DeviceMotionEvent.requestPermission();

                if (permission !== "granted") {
                    status.textContent = "Sensor permission denied";
                    return;
                }

            } catch (error) {
                status.textContent = "Unable to access sensor";
                return;
            }
        }

        if (active) return;

        active = true;
        baseline = null;
        above = false;

        window.addEventListener("devicemotion", detect);

        status.textContent = "Tracking active! Start walking.";
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

sensor_component = st.components.v2.component(
    "step_sensor",
    html=HTML,
    js=JS
)

result = sensor_component(
    key="step_sensor",
    default={"steps": st.session_state.steps},
    on_steps_change=lambda: None
)

if result.steps is not None:
    st.session_state.steps = max(0, int(result.steps))

steps = st.session_state.steps

# Save today's latest count in session history
st.session_state.history[str(today)] = steps

# ---------------- NAVIGATION ----------------

page = st.radio(
    "Choose Page",
    ["Today", "Weekly Activity"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ---------------- TODAY PAGE ----------------

if page == "Today":

    st.markdown("""
    <h2 style="text-align:center; letter-spacing:3px;">
    TODAY
    </h2>
    """, unsafe_allow_html=True)

    daily_goal = 10000

    progress = min(steps / daily_goal, 1.0)

    # Circular progress gauge

    circumference = 2 * 3.14159265 * 130
    arc_length = circumference * 0.75
    dash_offset = arc_length * (1 - progress)

    st.html(f"""
    <div style="
        display:flex;
        justify-content:center;
        margin:25px 0;
    ">

    <div style="
        width:310px;
        height:310px;
        position:relative;
    ">

    <svg width="310" height="310" viewBox="0 0 300 300">

        <defs>
            <linearGradient id="stepGradient"
                x1="0%" y1="100%" x2="100%" y2="0%">

                <stop offset="0%" stop-color="#ff3030"/>
                <stop offset="45%" stop-color="#ff9500"/>
                <stop offset="75%" stop-color="#ffff00"/>
                <stop offset="100%" stop-color="#7cff00"/>

            </linearGradient>
        </defs>

        <circle
            cx="150" cy="150" r="130"
            fill="none"
            stroke="#252525"
            stroke-width="15"
            stroke-dasharray="{arc_length} {circumference-arc_length}"
            transform="rotate(135 150 150)"
        />

        <circle
            cx="150" cy="150" r="130"
            fill="none"
            stroke="url(#stepGradient)"
            stroke-width="15"
            stroke-linecap="round"
            stroke-dasharray="{arc_length} {circumference-arc_length}"
            stroke-dashoffset="{dash_offset}"
            transform="rotate(135 150 150)"
        />

        <text x="150" y="145"
            text-anchor="middle"
            fill="white"
            font-size="48"
            font-weight="bold">
            {steps:,}
        </text>

        <text x="150" y="180"
            text-anchor="middle"
            fill="#aaaaaa"
            font-size="18"
            letter-spacing="3">
            STEPS
        </text>

    </svg>
    </div>
    </div>
    """)

    st.markdown(
        f"<p style='text-align:center;color:#aaa;'>"
        f"{round(progress * 100)}% OF DAILY GOAL"
        f"</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Distance and calories

    distance = steps * 0.0007
    calories = steps * 0.04

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "DISTANCE",
            f"{distance:.2f} km"
        )

    with col2:
        st.metric(
            "CALORIES",
            f"{calories:.1f} kcal"
        )

    st.markdown("---")

    st.markdown(
        "<h3 style='text-align:center;'>DAILY GOAL</h3>",
        unsafe_allow_html=True
    )

    st.progress(progress)

    st.markdown(
        f"<p style='text-align:center;color:#aaa;'>"
        f"{steps:,} / {daily_goal:,} steps"
        f"</p>",
        unsafe_allow_html=True
    )

    if steps >= daily_goal:
        st.success("Congratulations! Daily goal achieved!")
    else:
        st.info("Keep walking! Every step counts.")

# ---------------- WEEKLY ACTIVITY ----------------

elif page == "Weekly Activity":

    st.markdown("""
    <h2 style="text-align:center; letter-spacing:3px;">
    WEEKLY ACTIVITY
    </h2>
    """, unsafe_allow_html=True)

    dates = [
        today - timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    days = [d.strftime("%a") for d in dates]

    values = [
        st.session_state.history.get(str(d), 0)
        for d in dates
    ]

    # Weekly bar graph

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=days,
        y=values,

        marker=dict(
            color=values,
            colorscale=[
                [0, "#ff3030"],
                [0.35, "#ff9500"],
                [0.7, "#ffff00"],
                [1, "#7cff00"]
            ],
            cmin=0,
            cmax=max(10000, max(values)),
        ),

        text=[f"{v:,}" for v in values],
        textposition="outside"
    ))

    fig.update_layout(
        title=dict(
            text="STEPS WALKED EACH DAY",
            font=dict(color="white")
        ),

        plot_bgcolor="#050505",
        paper_bgcolor="#050505",

        font=dict(color="white"),

        xaxis=dict(
            title="DAY",
            color="white",
            showgrid=False
        ),

        yaxis=dict(
            title="NUMBER OF STEPS",
            color="white",
            gridcolor="#333333",
            rangemode="tozero"
        ),

        showlegend=False,
        height=450,
        margin=dict(t=65, b=50, l=55, r=25)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("DAILY STEP DETAILS")

    for d, value in zip(dates, values):

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(d.strftime("%A, %d %B"))

        with col2:
            st.write(f"**{value:,}**")

    st.markdown("---")

    st.metric(
        "TOTAL STEPS THIS WEEK",
        f"{sum(values):,}"
    )

    st.metric(
        "DAILY AVERAGE",
        f"{sum(values) // 7:,}"
    )

    st.caption(
        "Only steps recorded in the current session are included."
    )
