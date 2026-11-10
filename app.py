
import streamlit as st
import streamlit.components.v2 as components
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(
    page_title="Smart Step Counter",
    page_icon="🚶",
    layout="wide"
)

# ---------- SESSION DATA ----------

if "steps" not in st.session_state:
    st.session_state.steps = 0

if "history" not in st.session_state:
    st.session_state.history = {}

today = date.today()

# ---------- DARK THEME DESIGN ----------


    st.html(f"""
    <div style="display:flex;justify-content:center;margin:30px 0;">
      <div style="
        width:300px;
        height:300px;
        border-radius:50%;
        background:conic-gradient(
          from 135deg,
          #ff3030,
          #ff7a00,
          #ffff00,
          #7cff00 {angle}deg,
          #252525 {angle}deg 360deg
        );
        display:flex;
        align-items:center;
        justify-content:center;
      ">
        <div style="
          width:245px;
          height:245px;
          background:#050505;
          border-radius:50%;
          display:flex;
          flex-direction:column;
          align-items:center;
          justify-content:center;
        ">
          <div style="font-size:55px;font-weight:bold;color:white;">
            {steps:,}
          </div>
          <div style="font-size:20px;color:#aaa;letter-spacing:3px;">
            STEPS
          </div>
        </div>
      </div>
    </div>
    """)


# ---------- NAVIGATION ----------

st.markdown(
    "<h1 style='text-align:center; letter-spacing:3px;'>SMART STEP COUNTER</h1>",
    unsafe_allow_html=True
)

page = st.radio(
    "Navigation",
    ["Today", "Weekly Activity"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ---------- SENSOR COMPONENT ----------

HTML = """
<div style="background:#050505;color:white;text-align:center;
padding:10px;font-family:Arial;">

<button id="start" style="background:#b7ff00;color:black;
padding:12px 25px;border:0;border-radius:25px;font-weight:bold;">
START WALKING
</button>

<button id="stop" style="background:#333;color:white;
padding:12px 25px;border:0;border-radius:25px;">
STOP
</button>

<p id="status" style="color:#aaa;">Tracking stopped</p>

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

        if (movement > 1.3 && !above && now-lastStep > 350) {

            steps++;
            lastStep = now;
            above = true;

            setStateValue("steps", steps);
        }

        if (movement < 0.65) above = false;
    }

    start.onclick = async () => {

        if (!window.isSecureContext) {
            status.textContent = "HTTPS required";
            return;
        }

        if (!("DeviceMotionEvent" in window)) {
            status.textContent = "Motion sensor unavailable";
            return;
        }

        if (typeof DeviceMotionEvent.requestPermission === "function") {
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
    st.session_state.steps = max(0, int(result.steps))

steps = st.session_state.steps

# ---------- SAVE DAILY HISTORY ----------

st.session_state.history[str(today)] = steps

# ---------- TODAY PAGE ----------

if page == "Today":

    st.markdown(
        "<h2 style='text-align:center;color:white;'>TODAY</h2>",
        unsafe_allow_html=True
    )

    progress = min(steps / 10000, 1)
    angle = progress * 360

    st.markdown(f"""
    <div style="display:flex;justify-content:center;
    margin:30px 0;">

        <div style="
        width:300px;
        height:300px;
        border-radius:50%;
        background:conic-gradient(
            from 135deg,
            #ff3030,
            #ff7a00,
            #ffff00,
            #7cff00 {angle}deg,
            #252525 {angle}deg 360deg
        );
        display:flex;
        align-items:center;
        justify-content:center;">

            <div style="
            width:245px;
            height:245px;
            background:#050505;
            border-radius:50%;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;">

                <div style="font-size:55px;font-weight:bold;
                color:white;">{steps:,}</div>

                <div style="font-size:20px;color:#aaa;
                letter-spacing:3px;">STEPS</div>

            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='text-align:center;color:#aaa;'>"
        f"{round(progress*100)}% OF DAILY GOAL</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    distance = steps * 0.0007
    calories = steps * 0.04

    with col1:
        st.metric("DISTANCE", f"{distance:.2f} km")

    with col2:
        st.metric("CALORIES", f"{calories:.1f} kcal")

    st.markdown("---")

    st.markdown(
        "<h3 style='text-align:center;'>DAILY GOAL</h3>",
        unsafe_allow_html=True
    )

    st.progress(progress)

    st.markdown(
        f"<p style='text-align:center;color:#aaa;'>"
        f"{steps:,} / 10,000 steps</p>",
        unsafe_allow_html=True
    )

    if steps >= 10000:
        st.success("Congratulations! You reached your goal!")
    else:
        st.info("Keep walking! Every step counts.")

# ---------- WEEKLY ACTIVITY PAGE ----------

elif page == "Weekly Activity":

    st.markdown(
        "<h2 style='text-align:center;'>WEEKLY ACTIVITY</h2>",
        unsafe_allow_html=True
    )

    dates = [
        today - timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    labels = [d.strftime("%a") for d in dates]

    values = [
        st.session_state.history.get(str(d), 0)
        for d in dates
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=values,
            colorscale=[
                [0, "#ff3030"],
                [0.4, "#ff9500"],
                [0.7, "#ffff00"],
                [1, "#7cff00"]
            ],
            cmin=0,
            cmax=max(10000, max(values))
        ),
        text=values,
        textposition="outside"
    ))

    fig.update_layout(
        title="Steps Walked Each Day",
        title_font_color="white",
        plot_bgcolor="#050505",
        paper_bgcolor="#050505",
        font=dict(color="white"),
        yaxis=dict(
            title="Number of Steps",
            gridcolor="#333333",
            rangemode="tozero"
        ),
        xaxis=dict(title="Day"),
        showlegend=False,
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Daily Step Details")

    for d, value in zip(dates, values):
        st.write(f"**{d.strftime('%A, %d %B')}** — {value:,} steps")

    st.metric("Total Steps This Week", f"{sum(values):,}")

    st.metric(
        "Daily Average",
        f"{sum(values)//7:,} steps"
    )

