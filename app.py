
import streamlit as st
import plotly.graph_objects as go
import datetime
import math

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="Smart Step Counter",
    page_icon="🚶",
    layout="wide"
)

# ================= SESSION DATA =================

if "steps" not in st.session_state:
    st.session_state.steps = 0

if "history" not in st.session_state:
    st.session_state.history = {}

today = datetime.date.today()

# ================= CUSTOM DESIGN =================

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
    max-width: 1000px;
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
        90deg, #ff3030, #ff9500, #ffff00, #7cff00
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

# ================= TITLE =================

st.markdown("""
<h1 style="text-align:center;letter-spacing:4px;">
SMART STEP COUNTER
</h1>

<p style="text-align:center;color:#999;">
YOUR DAILY WALKING COMPANION
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ================= ANDROID STEP SENSOR =================

HTML = """
<div style="
    background:#050505;
    color:white;
    text-align:center;
    padding:12px;
    font-family:Arial;
">

<button id="start" style="
    background:linear-gradient(90deg,#ff3030,#ff9500,#ffff00,#7cff00);
    color:black;
    padding:12px 25px;
    border:0;
    border-radius:25px;
    font-weight:bold;
">
START WALKING
</button>

<button id="stop" style="
    background:#333;
    color:white;
    padding:12px 25px;
    border:0;
    border-radius:25px;
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

    let steps = component.data.initial_steps || 0;
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

step_sensor = st.components.v2.component(
    "step_sensor",
    html=HTML,
    js=JS
)

# Register component state and receive updated steps

result = step_sensor(
    data={"initial_steps": st.session_state.steps},
    default={"steps": st.session_state.steps},
    key="step_sensor",
    on_steps_change=lambda: None
)

if result.steps is not None:
    st.session_state.steps = max(
        0,
        int(result.steps)
    )

steps = st.session_state.steps

# Save today's count in session history

st.session_state.history[str(today)] = steps

# ================= NAVIGATION =================

page = st.radio(
    "Navigation",
    ["Today", "Weekly Activity"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ================= TODAY PAGE =================

if page == "Today":

    st.markdown("""
    <h2 style="text-align:center;letter-spacing:3px;">
    TODAY
    </h2>
    """, unsafe_allow_html=True)

    daily_goal = 10000

    progress = min(steps / daily_goal, 1.0)

    # CIRCULAR STEP GAUGE

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=steps,
            number={
                "valueformat": ",.0f",
                "font": {
                    "size": 42,
                    "color": "white"
                }
            },
            title={
                "text": "STEPS",
                "font": {
                    "size": 18,
                    "color": "#aaaaaa"
                }
            },
            gauge={
                "shape": "angular",
                "axis": {
                    "range": [0, daily_goal],
                    "visible": False
                },
                "bar": {
                    "color": "#7cff00",
                    "thickness": 0.22
                },
                "bgcolor": "#252525",
                "borderwidth": 0,
                "steps": [
                    {
                        "range": [0, 2500],
                        "color": "#ff3030"
                    },
                    {
                        "range": [2500, 5000],
                        "color": "#ff9500"
                    },
                    {
                        "range": [5000, 7500],
                        "color": "#ffff00"
                    },
                    {
                        "range": [7500, 10000],
                        "color": "#7cff00"
                    }
                ]
            }
        )
    )

    gauge.update_layout(
        paper_bgcolor="#050505",
        font_color="white",
        height=340,
        margin=dict(t=65, b=25, l=35, r=35)
    )

    st.plotly_chart(
        gauge,
        width="stretch",
        theme=None,
        config={"displayModeBar": False}
    )

    st.markdown(
        f"""
        <p style="text-align:center;color:#aaa;">
        {round(progress * 100)}% OF DAILY GOAL
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # DISTANCE AND CALORIES

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
        f"""
        <p style="text-align:center;color:#aaa;">
        {steps:,} / {daily_goal:,} steps
        </p>
        """,
        unsafe_allow_html=True
    )

    if steps >= daily_goal:
        st.success("Congratulations! Daily goal achieved!")
    else:
        st.info("Keep walking! Every step counts.")

# ================= WEEKLY ACTIVITY =================

elif page == "Weekly Activity":

    st.markdown("""
    <h2 style="text-align:center;letter-spacing:3px;">
    WEEKLY ACTIVITY
    </h2>
    """, unsafe_allow_html=True)

    dates = [
        today - datetime.timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    days = [
        d.strftime("%a")
        for d in dates
    ]

    values = [
        st.session_state.history.get(str(d), 0)
        for d in dates
    ]

    # WEEKLY BAR GRAPH

    graph = go.Figure()

    graph.add_trace(
        go.Bar(
            x=days,
            y=values,
            marker={
                "color": values,
                "colorscale": [
                    [0, "#ff3030"],
                    [0.35, "#ff9500"],
                    [0.7, "#ffff00"],
                    [1, "#7cff00"]
                ],
                "cmin": 0,
                "cmax": max(10000, max(values))
            },
            text=[f"{v:,}" for v in values],
            textposition="outside"
        )
    )

    graph.update_layout(
        title={
            "text": "STEPS WALKED EACH DAY",
            "font": {"color": "white"}
        },
        paper_bgcolor="#050505",
        plot_bgcolor="#050505",
        font={"color": "white"},
        xaxis={
            "title": "DAY",
            "showgrid": False
        },
        yaxis={
            "title": "NUMBER OF STEPS",
            "gridcolor": "#333333",
            "rangemode": "tozero"
        },
        showlegend=False,
        height=430,
        margin=dict(t=65, b=45, l=45, r=20)
    )

    st.plotly_chart(
        graph,
        width="stretch",
        theme=None,
        config={"displayModeBar": False}
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
        "Daily records are currently stored only for this session."
    )


