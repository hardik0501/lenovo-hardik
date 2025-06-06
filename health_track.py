import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

# --- Utils ---
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        # Add contact and email columns for patient users
        return pd.DataFrame(columns=["username","name","age","gender","weight","height","disease","password","role","contact","email"])

def save_users(df):
    df.to_csv("users.csv", index=False)

def save_consult_requests(requests):
    with open("consult_requests.json", "w") as f:
        json.dump(requests, f, indent=2)

def load_consult_requests():
    if os.path.exists("consult_requests.json"):
        with open("consult_requests.json", "r") as f:
            return json.load(f)
    return []

def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 1)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def personalized_targets(category):
    if category == "Underweight":
        return {"steps": 8000, "water": 2.5, "sleep": 7}
    elif category == "Normal":
        return {"steps": 10000, "water": 3.0, "sleep": 7}
    elif category == "Overweight":
        return {"steps": 12000, "water": 3.5, "sleep": 7}
    else:
        return {"steps": 15000, "water": 4.0, "sleep": 7}

def ai_consultation_advice(user_info, daily_data):
    disease = user_info.get('disease', '').lower()
    bmi = calculate_bmi(user_info['weight'], user_info['height'])
    category = bmi_category(bmi)

    advice = ""

    if "diabetes" in disease:
        advice += "💉 Monitor blood sugar levels closely. Maintain low sugar diet.\n"
    if "hypertension" in disease:
        advice += "🧂 Avoid salty foods. Practice relaxation and yoga.\n"
    if "asthma" in disease:
        advice += "🌬️ Avoid triggers and keep inhaler handy.\n"

    if category == "Underweight":
        advice += "🍗 Recommend high-protein diet and strength training.\n"
    elif category == "Normal":
        advice += "🥗 Maintain balanced diet and regular exercise.\n"
    else:
        advice += "🥦 Consider low-calorie diet and cardio exercises.\n"

    avg_steps = daily_data['Steps'].mean() if not daily_data.empty else 0
    avg_water = daily_data['Water'].mean() if not daily_data.empty else 0
    avg_sleep = daily_data['Sleep'].mean() if not daily_data.empty else 0

    targets = personalized_targets(category)

    if avg_steps < targets['steps']:
        advice += "🚶 Increase daily steps to reach your target.\n"
    if avg_water < targets['water']:
        advice += "💧 Increase water intake to stay hydrated.\n"
    if avg_sleep < targets['sleep']:
        advice += "🛌 Aim for at least 7 hours of sleep.\n"

    if not advice:
        advice = "🎉 No specific advice. Keep up the good work!"

    return advice

# --- Streamlit Pages ---

def register_patient():
    st.header("📝 Patient Registration")
    with st.form("register_form_patient"):
        username = st.text_input("👤 Username", key="username_patient")
        name = st.text_input("📛 Full Name", key="name_patient")
        age = st.number_input("🎂 Age", min_value=1, max_value=120, key="age_patient")
        gender = st.radio("⚧️ Gender", ["Male", "Female", "Other"], key="gender_patient")
        weight = st.number_input("⚖️ Weight (kg)", min_value=1.0, max_value=300.0, format="%.1f", key="weight_patient")
        height = st.number_input("📏 Height (cm)", min_value=30.0, max_value=250.0, format="%.1f", key="height_patient")
        disease = st.text_input("💊 Disease / Suffering From (optional)", key="disease_patient")
        contact = st.text_input("📞 Contact Number", key="contact_patient")
        email = st.text_input("📧 Email Address", key="email_patient")
        password = st.text_input("🔒 Password", type="password", key="password_patient")
        confirm_password = st.text_input("🔁 Confirm Password", type="password", key="confirm_password_patient")

        submitted = st.form_submit_button("Register")
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            if not username or not name or not password:
                st.error("Please fill all required fields")
                return
            users = load_users()
            if username in users['username'].values:
                st.error("Username already taken")
                return
            new_user = {
                "username": username,
                "name": name,
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "disease": disease,
                "password": password,
                "role": "patient",
                "contact": contact,
                "email": email
            }
            users = users.append(new_user, ignore_index=True)
            save_users(users)
            st.success("Patient registration successful! Please login.")
            st.session_state.page = "login"
            st.experimental_rerun()

def register_doctor():
    st.header("📝 Doctor Registration")
    with st.form("register_form_doctor"):
        username = st.text_input("👤 Username", key="username_doctor")
        name = st.text_input("📛 Full Name", key="name_doctor")
        age = st.number_input("🎂 Age", min_value=25, max_value=100, key="age_doctor")
        gender = st.radio("⚧️ Gender", ["Male", "Female", "Other"], key="gender_doctor")
        specialization = st.text_input("🩺 Specialization", key="specialization_doctor")
        password = st.text_input("🔒 Password", type="password", key="password_doctor")
        confirm_password = st.text_input("🔁 Confirm Password", type="password", key="confirm_password_doctor")

        submitted = st.form_submit_button("Register")
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            if not username or not name or not password or not specialization:
                st.error("Please fill all required fields")
                return
            users = load_users()
            if username in users['username'].values:
                st.error("Username already taken")
                return
            # Doctor role has no weight, height, disease info
            new_user = {
                "username": username,
                "name": name,
                "age": age,
                "gender": gender,
                "weight": None,
                "height": None,
                "disease": None,
                "password": password,
                "role": "doctor",
                "specialization": specialization,
                "contact": None,
                "email": None
            }
            users = users.append(new_user, ignore_index=True)
            save_users(users)
            st.success("Doctor registration successful! Please login.")
            st.session_state.page = "login"
            st.experimental_rerun()

def patient_dashboard():
    st.header(f"🙋‍♂️ Welcome, {st.session_state.name} (Patient)")

    bmi = calculate_bmi(st.session_state.weight, st.session_state.height)
    category = bmi_category(bmi)
    st.write(f"📊 Your BMI is **{bmi}** which is considered **{category}**.")

    targets = personalized_targets(category)
    st.write(f"🎯 Your daily targets:")
    st.markdown(f"- 🚶 Steps: **{targets['steps']}** steps")
    st.markdown(f"- 💧 Water Intake: **{targets['water']}** liters")
    st.markdown(f"- 🛌 Sleep: **{targets['sleep']}** hours")

    days = st.slider("📆 Select number of days to track", 1, 7, 7)

    st.subheader("🗓️ Enter your daily data")

    daily_data = {
        "Date": [],
        "Steps": [],
        "Water": [],
        "Sleep": []
    }

    for i in range(days):
        date = (datetime.today() - pd.Timedelta(days=days-1 - i)).strftime("%Y-%m-%d")
        steps = st.number_input(f"🚶 Steps for {date}", min_value=0, max_value=50000, key=f"steps_{i}")
        water = st.number_input(f"💧 Water intake (liters) for {date}", min_value=0.0, max_value=10.0, step=0.1, key=f"water_{i}")
        sleep = st.number_input(f"🛌 Sleep hours for {date}", min_value=0.0, max_value=24.0, step=0.1, key=f"sleep_{i}")
        daily_data["Date"].append(date)
        daily_data["Steps"].append(steps)
        daily_data["Water"].append(water)
        daily_data["Sleep"].append(sleep)

    df_daily = pd.DataFrame(daily_data)

    st.subheader("📈 Your Health Data Trends")
    fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

    axs[0].plot(df_daily["Date"], df_daily["Steps"], marker='o', color='blue')
    axs[0].axhline(y=targets['steps'], color='green', linestyle='--', label='Target Steps')
    axs[0].set_ylabel('Steps')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(df_daily["Date"], df_daily["Water"], marker='o', color='cyan')
    axs[1].axhline(y=targets['water'], color='green', linestyle='--', label='Target Water (L)')
    axs[1].set_ylabel('Water (L)')
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(df_daily["Date"], df_daily["Sleep"], marker='o', color='purple')
    axs[2].axhline(y=targets['sleep'], color='green', linestyle='--', label='Target Sleep (Hrs)')
    axs[2].set_ylabel('Sleep (Hrs)')
    axs[2].set_xlabel('Date')
    axs[2].legend()
    axs[2].grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    if st.button("💾 Save Data and Request Consultation"):
        users = load_users()
        users.loc[users['username'] == st.session_state.username, ['weight','height']] = st.session_state.weight, st.session_state.height
        save_users(users)

        consult_requests = load_consult_requests()
        consult_requests = [r for r in consult_requests if r['username'] != st.session_state.username]

        user_info = users.loc[users['username'] == st.session_state.username].iloc[0].to_dict()

        new_request = {
            "username": st.session_state.username,
            "user_info": user_info,
            "daily_data": df_daily.to_dict(orient='records'),
            "timestamp": datetime.now().isoformat()
        }
        consult_requests.append(new_request)
        save_consult_requests(consult_requests)

        st.success("✅ Your data saved and consultation request sent!")

def doctor_dashboard():
    st.header("👨‍⚕️ Doctor Dashboard")

    consult_requests = load_consult_requests()
    if not consult_requests:
        st.info("No consultation requests available.")
        return

    usernames = [r['username'] for r in consult_requests]
    selected = st.selectbox("Select patient to view consultation request", usernames)
    request = next((r for r in consult_requests if r['username'] == selected), None)
    if not request:
        st.warning("Selected patient request not found.")
        return

    user_info = request['user_info']
    daily_data = pd.DataFrame(request['daily_data'])

    st.subheader(f"👤 Patient: {user_info['name']} (Age: {user_info['age']}, Gender: {user_info['gender']})")
    st.write(f"📞 Contact: {user_info.get('contact', 'N/A')}")
    st.write(f"📧 Email: {user_info.get('email', 'N/A')}")
    st.write(f"💊 Disease / Suffering From: **{user_info.get('disease','N/A')}**")

    st.subheader("📅 Recent Daily Data")
    st.dataframe(daily_data)

    st.subheader("🧠 AI Consultation Advice")
    advice = ai_consultation_advice(user_info, daily_data)
    st.text(advice)

    st.subheader("📝 Add Prescription / Notes")
    prescription = st.text_area("Enter prescription or notes here:")

    if st.button("💾 Submit & Complete Consultation"):
        # Save prescription to file
        os.makedirs("prescriptions", exist_ok=True)
        prescription_path = f"prescriptions/{selected}.txt"
        with open(prescription_path, "w") as f:
            f.write(prescription)

        # Save record to CSV
        record = {
            "username": selected,
            "name": user_info['name'],
            "age": user_info['age'],
            "gender": user_info['gender'],
            "contact": user_info.get('contact', ''),
            "email": user_info.get('email', ''),
            "disease": user_info.get('disease', ''),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "prescription": prescription,
            "advice": advice
        }
        completed_df = pd.DataFrame([record])
        if os.path.exists("completed_consultations.csv"):
            existing = pd.read_csv("completed_consultations.csv")
            completed_df = pd.concat([existing, completed_df], ignore_index=True)
        completed_df.to_csv("completed_consultations.csv", index=False)

        # Remove from current requests
        consult_requests = [r for r in consult_requests if r['username'] != selected]
        save_consult_requests(consult_requests)

        st.success(f"✅ Consultation completed and prescription saved for {user_info['name']}.")

# --- Login and routing ---
def login():
    st.header("🔐 Login")
    users = load_users()
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("➡️ Login"):
        user = users[(users['username'] == username) & (users['password'] == password)]
        if not user.empty:
            user = user.iloc[0]
            st.session_state.username = user['username']
            st.session_state.name = user['name']
            st.session_state.age = user['age']
            st.session_state.gender = user['gender']
            st.session_state.weight = user['weight']
            st.session_state.height = user['height']
            st.session_state.disease = user['disease']
            st.session_state.role = user['role']
            st.session_state.contact = user.get('contact', None)
            st.session_state.email = user.get('email', None)
            st.success(f"Welcome {user['name']}!")
            st.session_state.page = "patient_dashboard" if user['role'] == "patient" else "doctor_dashboard"
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    menu = {
        "🔐 Login": "login",
        "📝 Register Patient": "register_patient",
        "🩺 Register Doctor": "register_doctor",
        "📋 Patient Dashboard": "patient_dashboard",
        "👨‍⚕️ Doctor Dashboard": "doctor_dashboard"
    }

    choice = st.sidebar.selectbox("📂 Menu", list(menu.keys()))

    # Role based page access control
    if choice == "📋 Patient Dashboard" and (st.session_state.get("role") != "patient"):
        st.warning("Please login as patient to access this page.")
        st.session_state.page = "login"
    elif choice == "👨‍⚕️ Doctor Dashboard" and (st.session_state.get("role") != "doctor"):
        st.warning("Please login as doctor to access this page.")
        st.session_state.page = "login"
    else:
        st.session_state.page = menu[choice]

    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "register_patient":
        register_patient()
    elif st.session_state.page == "register_doctor":
        register_doctor()
    elif st.session_state.page == "patient_dashboard":
        patient_dashboard()
    elif st.session_state.page == "doctor_dashboard":
        doctor_dashboard()

if __name__ == "__main__":
    main()  