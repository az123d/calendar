import streamlit as st
import pandas as pd
import datetime
import requests
import time
import os

# --- Page Setup ---
st.set_page_config(page_title="Chronicle of Tragedy", page_icon="🌑", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- Database Generator Function ---
def generate_database():
    """Fetches 365 days of historical tragedies via Wikipedia API and saves to CSV."""
    data = []
    start_date = datetime.date(2024, 1, 1)
    keywords = ['disaster', 'earthquake', 'fire', 'crash', 'explosion', 
                'killed', 'assassination', 'massacre', 'tsunami', 'hurricane', 'sinking']
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(366):
        curr = start_date + datetime.timedelta(days=i)
        m, d = curr.month, curr.day
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{m}/{d}"
        headers = {'User-Agent': 'HistoricalCalendarApp/1.0 (Mission Support)'}
        
        year_found = "N/A"
        event_desc = "Historical record pending mission analysis"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                events = response.json().get('events', [])
                for event in events:
                    text = event.get('text', '')
                    if any(word in text.lower() for word in keywords):
                        year_found = event.get('year', 'Unknown')
                        event_desc = text
                        break
        except Exception:
            pass 
            
        data.append([m, d, year_found, event_desc])
        
        # Update UI Progress
        progress_bar.progress((i + 1) / 366)
        status_text.text(f"Extracting data for {curr.strftime('%B %d')}...")
        time.sleep(0.05) # Prevent API rate limiting

    df = pd.DataFrame(data, columns=['Month', 'Day', 'Year', 'Event'])
    df.to_csv('tragedies.csv', index=False)
    
    progress_bar.empty()
    status_text.empty()
    return df

# --- Data Loading ---
@st.cache_data
def load_data():
    if not os.path.exists('tragedies.csv'):
        return generate_database()
    return pd.read_csv('tragedies.csv')

# --- Header ---
st.title("🌑 Historical Tragedy Calendar")
st.markdown("---")

# Initial check & load
with st.spinner("Verifying historical database..."):
    df = load_data()

# Optional Manual Refresh Button in Sidebar
with st.sidebar:
    st.header("Database Controls")
    if st.button("Rebuild Database (Fetch Latest)"):
        st.cache_data.clear()
        if os.path.exists('tragedies.csv'):
            os.remove('tragedies.csv')
        st.rerun()

# --- Interactive UI ---
st.write("Select a date from the calendar to reveal a significant historical tragedy or disaster that occurred on that day.")
selected_date = st.date_input("Investigation Date:", datetime.date.today())

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
    st.info(f"No major tragedies currently indexed for {selected_date.strftime('%B %d')}.")

st.markdown("---")
st.caption("Data provided via Wikipedia API for historical research and mission awareness purposes.")
