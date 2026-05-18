import streamlit as st
import pandas as pd
import datetime
import requests

# --- Page Setup ---
st.set_page_config(page_title="Chronicle of Tragedy", page_icon="🌑", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- Dynamic API Fetcher ---
@st.cache_data
def fetch_tragedy_for_day(month, day):
    """Calls Wikipedia API dynamically for the selected date."""
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    headers = {'User-Agent': 'HistoricalCalendarApp/1.0 (Mission Support Research)'}
    keywords = ['disaster', 'earthquake', 'fire', 'crash', 'explosion', 
                'killed', 'assassination', 'massacre', 'tsunami', 'hurricane', 
                'sinking', 'tornado', 'flood', 'bombing', 'terrorist']
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            events = response.json().get('events', [])
            
            # Find all tragedies matching keywords
            matches = []
            for event in events:
                text = event.get('text', '')
                if any(word in text.lower() for word in keywords):
                    matches.append({
                        "Year": event.get('year', 'Unknown'),
                        "Event": text
                    })
            
            if matches:
                # Return the list of tragedies found for that day
                return pd.DataFrame(matches)
                
    except Exception as e:
        st.error(f"Network error: Unable to reach historical database.")
    
    return pd.DataFrame()

# --- Application UI ---
st.title("🌑 Historical Tragedy Calendar")
st.markdown("---")

st.write("Select any date. The system will query the historical archives in real-time.")
selected_date = st.date_input("Investigation Date:", datetime.date.today())

# Trigger the dynamic fetch
with st.spinner(f"Querying archives for {selected_date.strftime('%B %d')}..."):
    results_df = fetch_tragedy_for_day(selected_date.month, selected_date.day)

st.divider()

# --- Display Results ---
if not results_df.empty:
    st.subheader(f"Historical Records: {selected_date.strftime('%B %d')}")
    for _, row in results_df.iterrows():
        st.error(f"### {row['Year']}: {row['Event']}")
else:
    st.info(f"No major tragedies found in the primary archive for {selected_date.strftime('%B %d')}. This date may have been historically quiet or requires further deep research.")

st.markdown("---")
st.caption("Real-time data provided via Wikipedia REST API.")
