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
                    
                    # Attempt to get an image and article link if available
                    img_url = None
                    article_url = None
                    pages = event.get('pages', [])
                    if pages:
                        article_url = pages[0].get('content_urls', {}).get('desktop', {}).get('page')
                        thumbnail = pages[0].get('thumbnail')
                        if thumbnail:
                            img_url = thumbnail.get('source')

                    # Clean up the year to ensure it's treated as an integer for sorting
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
                # Sort by year (Most recent first)
                df = pd.DataFrame(matches)
                df = df.sort_values(by="SortYear", ascending=False).drop(columns=["SortYear"])
                return df
                
    except Exception as e:
        st.error("Network error: Unable to reach historical database.")
    
    return pd.DataFrame()

# --- Application UI ---
st.title("🌑 Historical Tragedy Calendar")
st.write("Select a date to query the archives. The system will retrieve historical disasters, images, and research links.")

# Add a sidebar for extra controls
with st.sidebar:
    st.header("Control Panel")
    selected_date = st.date_input("Investigation Date:", datetime.date.today())
    st.caption("Change the date here to trigger a new search.")

# Trigger the dynamic fetch
with st.spinner(f"Querying archives for {selected_date.strftime('%B %d')}..."):
    results_df = fetch_tragedy_for_day(selected_date.month, selected_date.day)

st.divider()

# --- Display Results ---
if not results_df.empty:
    st.subheader(f"Historical Records: {selected_date.strftime('%B %d')}")
    st.write(f"Found **{len(results_df)}** significant incidents.")
    
    for _, row in results_df.iterrows():
        # Use Streamlit expanders for a cleaner, modern look
        with st.expander(f"🚩 {row['Year']}: {row['Event'][:60]}..."):
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(row['Image']):
                    st.image(row['Image'], use_column_width=True)
                else:
                    st.write("*(No image on file)*")
                    
            with col2:
                st.write(f"**Detailed Summary:** {row['Event']}")
                if pd.notna(row['Link']):
                    st.markdown(f"[➡️ Read full declassified report (Wikipedia)]({row['Link']})")

    # Add Export Capability
    st.divider()
    csv = results_df[['Year', 'Event', 'Link']].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Daily Report (CSV)",
        data=csv,
        file_name=f"Tragedy_Report_{selected_date.strftime('%b_%d')}.csv",
        mime="text/csv",
    )
    
else:
    st.info(f"No major tragedies found in the primary archive for {selected_date.strftime('%B %d')}.")

st.markdown("---")
st.caption("Real-time data provided via Wikipedia REST API.")
