import streamlit as st
import pandas as pd
import feedparser
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
import os
from datetime import datetime

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Auto News Command", layout="wide", page_icon="🚙")

# Custom CSS to replicate the "Card" look
# FIXED: Added 'color: #333333' to force dark text on white cards
st.markdown("""
<style>
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #333333; 
    }
    .source-tag {
        background-color: #f0f2f6;
        color: #333333;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .time-tag {
        float: right;
        color: #888;
        font-size: 0.8rem;
    }
    .news-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 10px;
        color: #1f1f1f;
        text-decoration: none;
    }
    .news-summary {
        font-size: 0.9rem;
        color: #555555;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .read-btn {
        display: block;
        margin-top: 15px;
        color: #0068c9;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
    }
    /* Social Card Specifics */
    .social-card {
        background: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #eee;
        color: #333333; /* Forces black text */
    }
    .social-card a {
        color: #0068c9;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA HANDLING FUNCTIONS ---

def load_sources():
    if not os.path.exists("sources.csv"):
        # Create default if missing
        df = pd.DataFrame(columns=["Category", "Name", "URL"])
        df.to_csv("sources.csv", index=False)
    return pd.read_csv("sources.csv")

def save_source(category, name, url):
    df = load_sources()
    new_row = pd.DataFrame({"Category": [category], "Name": [name], "URL": [url]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("sources.csv", index=False)

def clean_summary(html_text):
    if not html_text: return ""
    soup = BeautifulSoup(html_text, "lxml")
    return soup.get_text()[:150] + "..."

def get_time(entry):
    # Tries to find published date, otherwise uses current time
    if hasattr(entry, 'published'):
        return entry.published[:16] # Truncate to keep it short (e.g., "Tue, 15 Jan 2026")
    elif hasattr(entry, 'updated'):
        return entry.updated[:16]
    else:
        return "Just Now"

def fetch_feed_data(sources_df):
    news_items = []
    for _, row in sources_df.iterrows():
        try:
            feed = feedparser.parse(row["URL"])
            for entry in feed.entries[:4]: # Top 4 per source
                summary = entry.summary if 'summary' in entry else ""
                news_items.append({
                    "Source": row["Name"],
                    "Title": entry.title,
                    "Link": entry.link,
                    "Summary": clean_summary(summary),
                    "Time": get_time(entry)
                })
        except:
            continue
    return news_items

# --- 3. MAIN UI LAYOUT ---

st.title("🚙 Auto News Command")
st.caption("Real-time Automotive Intelligence System")

# Tabs
tab_india, tab_global, tab_social, tab_trends = st.tabs([
    "🇮🇳 Indian News", "🌍 Global News", "📱 Social Wall", "📈 Market Intelligence"
])

df_sources = load_sources()

# --- TAB 1: INDIAN NEWS ---
with tab_india:
    if st.button("🔄 Refresh India News"):
        indian_sources = df_sources[df_sources["Category"] == "Indian News"]
        news_data = fetch_feed_data(indian_sources)
        
        cols = st.columns(3)
        for i, item in enumerate(news_data):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <span class="source-tag">{item['Source']}</span>
                    <span class="time-tag">🕒 {item['Time']}</span>
                    <div class="news-title"><a href="{item['Link']}" target="_blank" style="text-decoration:none; color:#1f1f1f;">{item['Title']}</a></div>
                    <div class="news-summary">{item['Summary']}</div>
                    <a href="{item['Link']}" target="_blank" class="read-btn">Read Article ↗</a>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 2: GLOBAL NEWS ---
with tab_global:
    if st.button("🔄 Refresh Global News"):
        global_sources = df_sources[df_sources["Category"] == "Global News"]
        news_data = fetch_feed_data(global_sources)
        
        cols = st.columns(3)
        for i, item in enumerate(news_data):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <span class="source-tag">{item['Source']}</span>
                    <span class="time-tag">🕒 {item['Time']}</span>
                    <div class="news-title"><a href="{item['Link']}" target="_blank" style="text-decoration:none; color:#1f1f1f;">{item['Title']}</a></div>
                    <div class="news-summary">{item['Summary']}</div>
                    <a href="{item['Link']}" target="_blank" class="read-btn">Read Article ↗</a>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 3: SOCIAL WALL ---
with tab_social:
    st.info("Tip: Use RSS Bridge links for Twitter and Instagram sources.")
    col1, col2, col3, col4 = st.columns(4)
    
    def render_social_col(column, category_name, icon):
        with column:
            st.markdown(f"### {icon} {category_name}")
            sources = df_sources[df_sources["Category"] == f"Social-{category_name}"]
            if not sources.empty:
                for _, row in sources.iterrows():
                    try:
                        feed = feedparser.parse(row["URL"])
                        for entry in feed.entries[:3]:
                            timestamp = get_time(entry)
                            # FIXED: Using 'social-card' class to ensure black text
                            st.markdown(f"""
                            <div class="social-card">
                                <small style="color:#666;"><b>{row['Name']}</b> • {timestamp}</small><br>
                                <div style="margin-top:5px; font-weight:500;">{entry.title}</div>
                                <div style="margin-top:8px;"><a href="{entry.link}" target="_blank">View Post ↗</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    except:
                        st.error(f"Error loading {row['Name']}")
            else:
                st.caption(f"No {category_name} sources added.")

    render_social_col(col1, "X", "🐦")
    render_social_col(col2, "Insta", "📸")
    render_social_col(col3, "Facebook", "📘")
    render_social_col(col4, "Threads", "🧵")

# --- TAB 4: MARKET INTELLIGENCE (TRENDS) ---
with tab_trends:
    st.write("### Google Search Interest (Last 7 Days)")
    if st.button("📊 Scan Trends"):
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            kw_list = ["Car", "EV", "SUV"]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**🇮🇳 India**")
                pytrends.build_payload(kw_list, cat=47, timeframe='now 7-d', geo='IN')
                st.line_chart(pytrends.interest_over_time()[kw_list])
            with c2:
                st.write("**🇺🇸 USA**")
                pytrends.build_payload(kw_list, cat=47, timeframe='now 7-d', geo='US')
                st.line_chart(pytrends.interest_over_time()[kw_list])
            with c3:
                st.write("**🇬🇧 UK**")
                pytrends.build_payload(kw_list, cat=47, timeframe='now 7-d', geo='GB')
                st.line_chart(pytrends.interest_over_time()[kw_list])

        except Exception as e:
            st.warning("Google Trends is busy. Try again in 10 minutes.")

# --- SIDEBAR: MANAGE FEEDS ---
with st.sidebar:
    st.header("⚙️ Manage Feeds")
    with st.expander("➕ Add New Source"):
        with st.form("add_source_form"):
            s_name = st.text_input("Source Name (e.g. Autocar)")
            s_cat = st.selectbox("Category", ["Indian News", "Global News", "Social-X", "Social-Insta", "Social-Facebook", "Social-Threads"])
            s_url = st.text_input("RSS URL")
            submitted = st.form_submit_button("Add Source")
            
            if submitted and s_name and s_url:
                save_source(s_cat, s_name, s_url)
                st.success("Added! Refresh app.")
    
    st.write("---")
    st.write("**Current Sources:**")
    st.dataframe(df_sources, hide_index=True)
