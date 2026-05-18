import streamlit as st
import pandas as pd
import datetime
import requests

# --- Page Setup ---
st.set_page_config(page_title="Things That Happened Today", page_icon="☠️", layout="centered")

# Custom CSS for dark mission theme
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- Dynamic API Fetcher ---
@st.cache_data
def fetch_tragedy_for_day(month, day):
    """Calls Wikipedia API and extracts events, links, and images."""
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    headers = {'User-Agent': 'HistoricalCalendarApp/2.0 (Mission Support Research)'}
    keywords = ['disaster', 'earthquake', 'fire', 'crash', 'explosion', 
                'killed', 'assassination', 'massacre', 'tsunami', 'hurricane', 
                'sinking', 'tornado', 'flood', 'bombing', 'terrorist']
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            events = response.json().get('events', [])
            
            matches = []
            for event in events:
                text = event.get('text', '')
                if any(word in text.lower() for word in keywords):
                    img_url = None
                    article_url = None
                    pages = event.get('pages', [])
                    if pages:
                        article_url = pages[0].get('content_urls', {}).get('desktop', {}).get('page')
                        thumbnail = pages[0].get('thumbnail')
                        if thumbnail:
                            img_url = thumbnail.get('source')

                    year_val = event.get('year')
                    try:
                        year_int = int(year_val)
                    except (ValueError, TypeError):
                        year_int = 0

                    matches.append({
                        "Year": year_val,
                        "SortYear": year_int,
                        "Event": text,
                        "Image": img_url,
                        "Link": article_url
                    })
            
            if matches:
                df = pd.DataFrame(matches)
                # Sort by year (Most recent first)
                df = df.sort_values(by="SortYear", ascending=False).reset_index(drop=True)
                return df
                
    except Exception:
        st.error("Network error: Unable to reach historical database.")
    
    return pd.DataFrame()

# --- Application UI ---
st.markdown("<h1 style='text-align: center;'>☠️ Fun Things Calendar ☠️</h1>", unsafe_allow_html=True)
st.write("Select a date to query the archives")

# Date picker in the center
selected_date = st.date_input("Investigation Date:", datetime.date.today())

# Trigger the dynamic fetch
with st.spinner(f"Querying archives for {selected_date.strftime('%B %d')}..."):
    results_df = fetch_tragedy_for_day(selected_date.month, selected_date.day)

st.divider()

# --- Display Results ---
if not results_df.empty:
    st.subheader(f"Historical Records: {selected_date.strftime('%B %d')}")
    
    # Loop through results and handle expansion
    for index, row in results_df.iterrows():
        # The first entry (index 0) is expanded by default
        is_expanded = (index == 0)
        
        with st.expander(f"🚩 {row['Year']}: {row['Event'][:60]}...", expanded=is_expanded):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(row['Image']):
                    st.image(row['Image'], use_column_width=True)
                else:
                    st.write("*(No image)*")
                    
            with col2:
                st.write(f"**Summary:** {row['Event']}")
                if pd.notna(row['Link']):
                    st.markdown(f"[➡️ Declassified Report]({row['Link']})")
    
else:
    st.info(f"No major tragedies found in the archive for {selected_date.strftime('%B %d')}.")

st.markdown("---")
st.caption("Real-time mission data provided via Wikipedia REST API.")
