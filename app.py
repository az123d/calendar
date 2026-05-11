import streamlit as st
import pandas as pd
import datetime

# --- Page Setup ---
st.set_page_config(page_title="Chronicle of Tragedy", page_icon="🌑", layout="centered")

# Custom CSS for a mission-focused dark theme
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('tragedies.csv')
        return df
    except Exception:
        return pd.DataFrame(columns=['Month', 'Day', 'Year', 'Event'])

df = load_data()

# --- Header ---
st.title("🌑 Historical Tragedy Calendar")
st.markdown("---")
st.write("Select a date from the calendar to reveal a significant historical tragedy or disaster that occurred on that day.")

# --- Interactive Sidebar/Input ---
selected_date = st.date_input("Investigation Date:", datetime.date.today())

# [...](asc_slot://start-slot-3)--- Logic ---
month = selected_date.month
day = selected_date.day
match = df[(df['Month'] == month) & (df['Day'] == day)]
st.divider()

# --- Display Results ---
if not match.empty:
    st.subheader(f"Incidents on {selected_date.strftime('%B %d')}")
    for _, row in match.iterrows():
        with st.container():
            st.error(f"### {row['Year']}: {row['Event']}")
else:
    st.info(f"No major tragedies currently indexed for {selected_date.strftime('%B %d')}. The database is updated periodically.")

st.markdown("---")
st.caption("Data provided for historical research and mission awareness purposes.")
