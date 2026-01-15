import streamlit as st
import pandas as pd
import feedparser
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import random

# --- 1. CONFIGURATION & PAGE SETUP ---
st.set_page_config(page_title="Auto News Command", layout="wide", page_icon="🏎️")

# Initialize Session State
if 'indian_news' not in st.session_state: st.session_state['indian_news'] = []
if 'global_news' not in st.session_state: st.session_state['global_news'] = []
if 'last_updated' not in st.session_state: st.session_state['last_updated'] = "Waiting for Refresh..."

# --- 2. PREMIUM CSS DESIGN ---
st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e1e1e;
    }

    /* CARD DESIGN */
    .news-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        border-color: #e0e0e0;
    }

    /* TAGS */
    .source-badge {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .time-badge {
        float: right;
        color: #757575;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* TYPOGRAPHY */
    .news-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #111;
        margin-top: 15px;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    
    .news-summary {
        font-size: 0.95rem;
        color: #555;
        line-height: 1.6;
        margin-bottom: 20px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* BUTTONS */
    .read-button {
        display: inline-block;
        background-color: #111;
        color: #fff !important;
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none;
        transition: background 0.2s;
    }
    
    .read-button:hover {
        background-color: #333;
        text-decoration: none;
    }

    /* SOCIAL CARDS COLOR CODING */
    .social-card-x { border-left: 4px solid #000; }
    .social-card-insta { border-left: 4px solid #E1306C; }
    .social-card-fb { border-left: 4px solid #1877F2; }
    .social-card-threads { border-left: 4px solid #333; }

</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & FUNCTIONS ---

def load_sources():
    if not os.path.exists("sources.csv"):
        # Default Data
        data = {
            "Category": ["Indian News", "Indian News", "Global News", "Global News"],
            "Name": ["Autocar India", "Team-BHP", "Motor1", "CarScoops"],
            "URL": [
                "https://www.autocarindia.com/RSS/News",
                "https://www.team-bhp.com/rss/news",
                "https://www.motor1.com/rss/news/all/",
                "https://www.carscoops.com/feed/"
            ]
        }
        pd.DataFrame(data).to_csv("sources.csv", index=False)
    return pd.read_csv("sources.csv")

def save_source(category, name, url):
    df = load_sources()
    new_row = pd.DataFrame({"Category": [category], "Name": [name], "URL": [url]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("sources.csv", index=False)

def format_time(entry):
    try:
        if hasattr(entry, 'published_parsed'):
            dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            return dt.strftime("%d %b, %I:%M %p")
        return entry.published[:16] if hasattr(entry, 'published') else "Just Now"
    except:
        return "Unknown"

def clean_summary(html_text):
    if not html_text: return "No summary available."
    try:
        return BeautifulSoup(html_text, "html.parser").get_text()[:200] + "..."
    except:
        return "Summary unavailable."

def fetch_feed_data(category_filter):
    df = load_sources()
    sources = df[df["Category"] == category_filter]
    items = []
    
    if sources.empty: return []
    
    # Progress Bar
    bar = st.progress(0)
    for i, (_, row) in enumerate(sources.iterrows()):
        try:
            feed = feedparser.parse(row["URL"])
            for entry in feed.entries[:5]:
                items.append({
                    "Source": row["Name"],
                    "Title": entry.title,
                    "Link": entry.link,
                    "Summary": clean_summary(entry.summary if 'summary' in entry else ""),
                    "Time": format_time(entry)
                })
        except: pass
        bar.progress((i + 1) / len(sources))
    bar.empty()
    return items

@st.cache_data(ttl=3600)
def get_trends(geo):
    try:
        time.sleep(random.uniform(1, 2))
        pytrends = TrendReq(hl='en-US', tz=360)
        kw = ['Car', 'SUV', 'EV']
        pytrends.build_payload(kw, cat=47, timeframe='now 7-d', geo=geo)
        related = pytrends.related_queries()
        for k in kw:
            if related and k in related and related[k]['rising'] is not None:
                return related[k]['rising'].head(5)
    except: return None

# --- 4. MAIN DASHBOARD UI ---

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🏎️ Auto News Command")
    st.markdown("**Real-time Intelligence System** | MechHelp.in")
with c2:
    st.metric(label="System Status", value="Online 🟢", delta=st.session_state['last_updated'])

st.write("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🇮🇳 Indian News", "🌍 Global News", "📱 Social Wall", "📈 Trends"])

# TAB 1: INDIA
with tab1:
    if st.button("🔄 Refresh Indian Feed", type="primary", use_container_width=True):
        st.session_state['indian_news'] = fetch_feed_data("Indian News")
        st.session_state['last_updated'] = datetime.now().strftime("%I:%M %p")
        st.rerun()

    if st.session_state['indian_news']:
        cols = st.columns(3)
        for i, news in enumerate(st.session_state['indian_news']):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <div>
                        <span class="source-badge">{news['Source']}</span>
                        <span class="time-badge">{news['Time']}</span>
                    </div>
                    <div class="news-title">{news['Title']}</div>
                    <div class="news-summary">{news['Summary']}</div>
                    <a href="{news['Link']}" target="_blank" class="read-button">Read Article ↗</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Feed is empty. Click Refresh above.")

# TAB 2: GLOBAL
with tab2:
    if st.button("🔄 Refresh Global Feed", use_container_width=True):
        st.session_state['global_news'] = fetch_feed_data("Global News")
        st.session_state['last_updated'] = datetime.now().strftime("%I:%M %p")
        st.rerun()
        
    if st.session_state['global_news']:
        cols = st.columns(3)
        for i, news in enumerate(st.session_state['global_news']):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <div>
                        <span class="source-badge">{news['Source']}</span>
                        <span class="time-badge">{news['Time']}</span>
                    </div>
                    <div class="news-title">{news['Title']}</div>
                    <div class="news-summary">{news['Summary']}</div>
                    <a href="{news['Link']}" target="_blank" class="read-button">Read Article ↗</a>
                </div>
                """, unsafe_allow_html=True)

# TAB 3: SOCIAL
with tab3:
    st.caption("Aggregating RSS feeds from RSS-Bridge")
    df = load_sources()
    c1, c2, c3, c4 = st.columns(4)

    def render_social_col(col, platform, css_class):
        with col:
            st.subheader(platform)
            subset = df[df["Category"] == f"Social-{platform}"]
            if not subset.empty:
                for _, row in subset.iterrows():
                    try:
                        feed = feedparser.parse(row["URL"])
                        for entry in feed.entries[:3]:
                            st.markdown(f"""
                            <div class="news-card {css_class}" style="padding: 15px; margin-bottom: 10px;">
                                <div style="font-size:0.8rem; color:#888;"><b>{row['Name']}</b> • {format_time(entry)}</div>
                                <div style="font-weight:600; margin-top:5px; margin-bottom:10px;">
                                    <a href="{entry.link}" target="_blank" style="text-decoration:none; color:#111;">{entry.title}</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    except: pass

    render_social_col(c1, "X", "social-card-x")
    render_social_col(c2, "Insta", "social-card-insta")
    render_social_col(c3, "Facebook", "social-card-fb")
    render_social_col(c4, "Threads", "social-card-threads")

# TAB 4: TRENDS
with tab4:
    st.subheader("🔥 Top Rising Search Queries")
    if st.button("📊 Scan Markets"):
        c1, c2, c3 = st.columns(3)
        
        def show_trend(col, country, code):
            with col:
                st.markdown(f"**{country}**")
                with st.spinner("Analyzing..."):
                    df_t = get_trends(code)
                    if df_t is not None:
                        st.dataframe(df_t, hide_index=True, use_container_width=True)
                    else:
                        st.warning("Rate Limit Hit 🛑")
                        st.markdown(f"[Open {country} Trends >](https://trends.google.com/trends/explore?geo={code}&q=Car)")

        show_trend(c1, "🇮🇳 India", "IN")
        show_trend(c2, "🇺🇸 USA", "US")
        show_trend(c3, "🇬🇧 UK", "GB")

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("➕ Add New Source", expanded=True):
        with st.form("src_form"):
            name = st.text_input("Source Name")
            cat = st.selectbox("Category", ["Indian News", "Global News", "Social-X", "Social-Insta", "Social-Facebook", "Social-Threads"])
            url = st.text_input("RSS URL")
            if st.form_submit_button("Save Source"):
                save_source(cat, name, url)
                st.success("Saved!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    st.write("**Database**")
    st.dataframe(load_sources(), hide_index=True)
