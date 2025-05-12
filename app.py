import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from twilio.rest import Client
import secrets

st.set_page_config(page_title="Road Safety Analysis", layout="wide")
st.title("🚦 AI-Driven Road Accident Analysis & SMS Alert System")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("accident.csv")

df = load_data()

# --- 1. Reasons for Accidents ---
st.header("1. Reasons for Road Accidents")
reason_counts = df['Reason'].value_counts()
colors = plt.cm.Spectral(np.linspace(0, 1, len(reason_counts)))
fig1, ax1 = plt.subplots()
ax1.pie(reason_counts, labels=reason_counts.index, colors=colors, autopct='%1.1f%%', startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# --- 2. Accidents by State ---
st.header("2. Top 10 States by Number of Accidents")
state_accidents = df.groupby('State')['Accident_ID'].count().reset_index()
top_states = state_accidents.sort_values(by='Accident_ID', ascending=False).head(10)
fig2, ax2 = plt.subplots()
colors = plt.cm.Spectral(top_states['Accident_ID'] / float(max(top_states['Accident_ID'])))
ax2.barh(top_states['State'], top_states['Accident_ID'], color=colors)
ax2.set_xlabel("Number of Accidents")
st.pyplot(fig2)

# --- 3. Accidents by Weather ---
st.header("3. Accidents by Weather Conditions")
weather_stats = df.groupby('Weather_Conditions')['Accident_ID'].count().reset_index()
top_weather = weather_stats.sort_values(by='Accident_ID', ascending=False).head(10)
colors = plt.cm.Spectral_r(top_weather['Accident_ID'] / float(max(top_weather['Accident_ID'])))
fig3, ax3 = plt.subplots()
ax3.bar(top_weather['Weather_Conditions'], top_weather['Accident_ID'], color=colors)
ax3.set_ylabel("Number of Accidents")
ax3.set_xticklabels(top_weather['Weather_Conditions'], rotation=45)
st.pyplot(fig3)

# --- 4. Impact of Speed on Deaths ---
st.header("4. Impact of Speeding on Accident Severity")
speed_data = df[['Speed_Limit', 'Number_of_Deaths']].dropna()
speed_stats = speed_data.groupby('Speed_Limit')['Number_of_Deaths'].mean().reset_index()
fig4, ax4 = plt.subplots()
ax4.plot(speed_stats['Speed_Limit'], speed_stats['Number_of_Deaths'], marker='o')
ax4.set_xlabel("Speed Limit")
ax4.set_ylabel("Average Deaths")
st.pyplot(fig4)

# --- 5. Alcohol-related Accidents by State ---
st.header("5. Alcohol-Related Accidents by State")
alcohol_df = df[df['Alcohol_Involved'] == 'Yes']
alcohol_counts = alcohol_df['State'].value_counts()
fig5, ax5 = plt.subplots()
ax5.bar(alcohol_counts.index, alcohol_counts.values, color=plt.cm.Spectral(alcohol_counts.values / max(alcohol_counts.values)))
ax5.set_xticklabels(alcohol_counts.index, rotation=90, fontsize=8)
ax5.set_ylabel("Number of Alcohol-Involved Accidents")
st.pyplot(fig5)

# --- 6. Accidents: Rural vs. Urban ---
st.header("6. Accidents in Rural vs Urban Areas")
df['Location_Type'] = df['Road_Type'].apply(lambda x: 'Rural' if str(x).startswith('R') else 'Urban')
location_counts = df['Location_Type'].value_counts()
fig6, ax6 = plt.subplots()
ax6.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%', colors=['#ff7f0e', '#1f77b4'])
ax6.axis("equal")
st.pyplot(fig6)

# --- 7. Real-Time Safety Check and Alert ---
st.header("🚨 Real-Time Safety Check & SMS Alert")

with st.form("safety_form"):
    alcohol_input = st.radio("Have you consumed alcohol?", ("No", "Yes"))
    speed_input = st.number_input("Enter your current speed (km/h)", min_value=0, step=1)
    submitted = st.form_submit_button("Check and Send Alert")

    if submitted:
        alcohol_detected = (alcohol_input.lower() == "yes")
        speed_limit_exceeded = speed_input > 100

        try:
            client = Client(st.secrets["TWILIO_SID"], st.secrets["TWILIO_TOKEN"])
            from_number = st.secrets["FROM_NUMBER"]
            to_number = st.secrets["TO_NUMBER"]

            message_body = ""

            if alcohol_detected and speed_limit_exceeded:
                message_body = f"⚠️ ALERT: Driver is overspeeding ({speed_input} km/h) and has consumed alcohol."
            elif alcohol_detected:
                message_body = f"⚠️ ALERT: Driver has consumed alcohol."
            elif speed_limit_exceeded:
                message_body = f"⚠️ ALERT: Driver is overspeeding at {speed_input} km/h."

            if message_body:
                message = client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=to_number
                )
                st.success("🚨 Alert sent via SMS.")
                st.info(f"Message SID: {message.sid}")
            else:
                st.success("✅ You are driving safely. No alert needed.")
        except Exception as e:
            st.error(f"Error sending SMS: {e}")
