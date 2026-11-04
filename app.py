import streamlit as st
import pandas as pd
import os
from datetime import date

profile_file = "data/profile.csv"
habits_file = "data/habits.csv"

def ensure_data_folder():
    os.makedirs("data", exist_ok=True)

goals = {
    "active_life": "Active Life",
    "healthy_growth": "Healthy Growth",
    "balance_life": "Balance Life",
    "fitness": "Fitness"
}

daily_targets = {
    "f_v": 5,
    "water": 8,
    "sleep_hours": 8,
    "exrcise": 30,
}

def load_profile():
    ensure_data_folder()

    if os.path.exists(profile_file):
        return pd.read_csv(profile_file)

    return pd.DataFrame(columns=["name", "age", "activity_level", "goal"])


def save_profile(name, age, activity_level, goal):
    df = load_profile()

    df = df[df["name"] != name]

    new_row = pd.DataFrame([{
        "name": name,
        "age": age,
        "activity_level": activity_level,
        "goal": goal
    }])

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(profile_file, index=False)


def load_habits():
    ensure_data_folder()

    columns = ["name", "date", "f_v", "water", "sleep_hours", "exercise", "points"]

    if os.path.exists(habits_file):
        return pd.read_csv(habits_file)

    return pd.DataFrame(columns=columns)


def save_habits(entry: dict):
    df = load_habits()

    df = df[~((df["name"] == entry["name"]) & (df["date"] == entry["date"]))]

    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)

    df.to_csv(habits_file, index=False)


def calculate_points(f_v, water, sleep_hours, exercise) -> int:
    points = 0

    points += min(f_v / daily_targets["f_v"], 1) * 25
    points += min(water / daily_targets["water"], 1) * 25
    points += min(sleep_hours / daily_targets["sleep_hours"], 1) * 25
    points += min(exercise / daily_targets["exrcise"], 1) * 25

    return round(points)


def get_badge(points: int) -> str:
    if points >= 100:
        return "🏆 Gold Badge"
    elif points >= 70:
        return "🥈 Silver Badge"
    elif points >= 50:
        return "🥉 Bronze Badge"
    elif points >= 30:
        return "🏅 Participation Badge"
    else:
        return "No Badge Yet"


def generate_tips(goal, f_v, water, sleep_hours, exercise) -> list:
    tips = []

    if goal == "active_life":
        if f_v < daily_targets["f_v"]:
            tips.append("Increase your intake of fruits and vegetables to meet your daily target.")
        if water < daily_targets["water"]:
            tips.append("Drink more water throughout the day to stay hydrated.")
        if sleep_hours < daily_targets["sleep_hours"]:
            tips.append("Ensure you get enough sleep for optimal health.")
        if exercise < daily_targets["exrcise"]:
            tips.append("Incorporate more physical activity into your routine.")

    elif goal == "healthy_growth":
        if f_v < daily_targets["f_v"]:
            tips.append("Focus on a balanced diet rich in fruits and vegetables.")
        if water < daily_targets["water"]:
            tips.append("Stay hydrated by drinking sufficient water.")
        if sleep_hours < daily_targets["sleep_hours"]:
            tips.append("Prioritize getting adequate sleep for growth and development.")
        if exercise < daily_targets["exrcise"]:
            tips.append("Engage in regular exercise to support healthy growth.")

    elif goal == "balance_life":
        if f_v < daily_targets["f_v"]:
            tips.append("Maintain a balanced diet with enough fruits and vegetables.")
        if water < daily_targets["water"]:
            tips.append("Keep yourself hydrated by drinking enough water.")
        if sleep_hours < daily_targets["sleep_hours"]:
            tips.append("Ensure you have a consistent sleep schedule for balance.")
        if exercise < daily_targets["exrcise"]:
            tips.append("Incorporate moderate exercise into your lifestyle.")

    elif goal == "fitness":
        if f_v < daily_targets["f_v"]:
            tips.append("Eat a variety of fruits and vegetables to fuel your fitness goals.")
        if water < daily_targets["water"]:
            tips.append("Hydrate well to support your fitness activities.")
        if sleep_hours < daily_targets["sleep_hours"]:
            tips.append("Get sufficient rest to aid in recovery and performance.")
        if exercise < daily_targets["exrcise"]:
            tips.append("Increase your physical activity to meet fitness targets.")

    return tips


st.title("Daily Health Tracker")

profiles = load_profile()

st.sidebar.title("New user?")

existing_names = profiles["name"].tolist() if not profiles.empty else []

choice = st.sidebar.radio(
    "Select an option:",
    ["New user", "Old user"] if existing_names else ["New user"]
)

if choice == "Old user":
    name = st.sidebar.selectbox("Choose your name:", existing_names)

    profile_row = profiles[profiles["name"] == name].iloc[0]

    goal = profile_row["goal"]

    st.sidebar.success(f"Welcome {name} again!")

else:
    name = st.sidebar.text_input("Enter your name:")

    age = st.sidebar.slider("Enter your age:", min_value=1, max_value=80, value=20)

    activity_level = st.sidebar.selectbox(
        "What is your activity level",
        ["Low", "Moderate", "High"]
    )

    goal_label = st.sidebar.selectbox("Select your goal:", list(goals.values()))

    goal = [k for k, v in goals.items() if v == goal_label][0]

    if name and st.sidebar.button("Save Profile"):
        save_profile(name, age, activity_level, goal)
        st.success(f"Profile saved for {name}!")

        st.rerun()

    if not name:
        st.info("Please enter your name")
        st.stop()

st.sidebar.markdown("---")
st.sidebar.write(f"Your goal: {goals[goal]}")

today = date.today().isoformat()

with st.form("habits_form"):
    col1, col2 = st.columns(2)

    with col1:
        f_v = st.slider("Fruits and vegetables", 0, 10, 0)
        water_cups = st.slider("Water cups", 0, 100, 0)

    with col2:
        sleep_hours = st.slider("Sleep hours", 0, 12, 0)
        exercise_minutes = st.slider("Exercise minutes", 0, 120, 0)

    submited = st.form_submit_button("Saved")

if submited:
    points = calculate_points(f_v, water_cups, sleep_hours, exercise_minutes)

    badge = get_badge(points)

    save_habits({
        "name": name,
        "date": today,
        "f_v": f_v,
        "water": water_cups,
        "sleep_hours": sleep_hours,
        "exercise": exercise_minutes,
        "points": points
    })

    st.success("Saved")
    st.metric("Your Points", f"{points} / 100")
    st.subheader(f"Your Badge: {badge}")
    st.balloons()

    st.markdown("---")

    tips = generate_tips(goal, f_v, water_cups, sleep_hours, exercise_minutes)

    for tip in tips:
        st.write(f"- {tip}")

st.markdown("---")

st.header("Your progress")

habits = load_habits()

user_data = habits[habits["name"] == name].copy()

if user_data.empty:
    st.info("Please store your habits")

else:
    user_data["date"] = pd.to_datetime(user_data["date"])
    user_data = user_data.sort_values("date")

    successful_days = (user_data["points"] >= 70).sum()
    total_day = len(user_data)

    success_rate = round((successful_days / total_day) * 100)

    st.metric("success_rate", f"{success_rate}%")

    last_days = user_data.tail(7)

    st.write("Points")
    st.bar_chart(last_days.set_index("date")[["points"]])

    st.markdown("---")

    st.caption("💚 مشروع تعليمي بسيط بلغة بايثون باستخدام Streamlit - CODEleader Academy")
