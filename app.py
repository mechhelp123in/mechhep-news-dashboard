import streamlit as st
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time

# --- 1. CONFIGURATION & PAGE SETUP ---
st.set_page_config(page_title="Auto News Command", layout="wide", page_icon="🏎️")

# Initialize Session State
if 'indian_news' not in st.session_state: st.session_state['indian_news'] = []
if 'global_news' not in st.session_state: st.session_state['global_news'] = []
if 'last_updated' not in st.session_state: st.session_state['last_updated'] = "Waiting for Refresh..."

# --- 2. PREMIUM CSS DESIGN (FIXED FOR DARK MODE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Force main app background to dark if desired, but let's focus on cards */
    .stApp {
       /* background-color: #0e1117; */ /* Optional: force dark bg */
    }

    /* CRITICAL FIX: Force text inside white cards to be DARK */
    .news-card, .trend-card, .social-card {
        color: #333333 !important; /* Dark Charcoal Text */
    }
    /* Force headers and links inside cards to be dark too */
    .news-card h1, .news-card h2, .news-card h3, .news-card div, .news-card span, .news-card a:not(.read-button) {
        color: #333333 !important;
    }
    
    /* CARD DESIGN Styles */
    .news-card {
        background-color: #ffffff !important; /* Force white background */
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        height: 100%;
    }
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        border-color: #e0e0e0;
    }

    /* TREND BLOCKS */
    .trend-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    /* Fix visibility for trend text objects */
    .trend-flag { font-size: 3rem; margin-bottom: 10px; display: block; }
    .trend-title { font-size: 1.2rem; font-weight: 800; color: #333333 !important; margin-bottom: 5px; }
    .trend-desc { font-size: 0.9rem; color: #666666 !important; margin-bottom: 20px; }

    /* TAGS & BUTTONS */
    .source-badge {
        background-color: #e3f2fd;
        color: #1565c0 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .time-badge { float: right; color: #757575 !important; font-size: 0.8rem; font-weight: 500; }
    
    .read-button {
        display: inline-block;
        background-color: #111;
        color: #fff !important; /* White text on black button */
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none;
        transition: background 0.2s;
    }
    .read-button:hover { background-color: #333; color: #fff !important;}

    /* SOCIAL COLORS */
    .social-card-x { border-left: 4px solid #000; }
    .social-card-insta { border-left: 4px solid #E1306C; }
    .social-card-fb { border-left: 4px solid #1877F2; }
    .social-card-threads { border-left: 4px solid #333; }
    
    /* Sidebar adjustments for dark mode */
    [data-testid="stSidebar"] {
       /* background-color: #1e1e1e; */
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & FUNCTIONS ---

def load_sources():
    if not os.path.exists("sources.csv"):
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

# --- 4. MAIN DASHBOARD UI ---

c1, c2 = st.columns([3, 1])
with c1:
    st.title("🏎️ Auto News Command")
    st.markdown("**Real-time Intelligence System** | MechHelp.in")
with c2:
    st.metric(label="System Status", value="Online 🟢", delta=st.session_state['last_updated'])

st.write("---")

tab1, tab2, tab3, tab4 = st.tabs(["🇮🇳 Indian News", "🌍 Global News", "📱 Social Wall", "📈 Trends (Live)"])

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
                    <div><span class="source-badge">{news['Source']}</span><span class="time-badge">{news['Time']}</span></div>
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
                    <div><span class="source-badge">{news['Source']}</span><span class="time-badge">{news['Time']}</span></div>
                    <div class="news-title">{news['Title']}</div>
                    <div class="news-summary">{news['Summary']}</div>
                    <a href="{news['Link']}" target="_blank" class="read-button">Read Article ↗</a>
                </div>
                """, unsafe_allow_html=True)

# TAB 3: SOCIAL
with tab3:
    st.caption("Using RSS-Bridge for Social Media")
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
                            <div class="news-card {css_class} social-card" style="padding: 15px; margin-bottom: 10px;">
                                <div style="font-size:0.8rem;" class="time-badge"><b>{row['Name']}</b> • {format_time(entry)}</div>
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

# --- TAB 4: TRENDS (DIRECT LINKS FIXED) ---
with tab4:
    st.subheader("🔥 Live Google Trends Dashboard")
    st.markdown("Direct access to the 'Trending Now' pages (Category: News/All).")
    
    # 3 BLOCKS LAYOUT
    t1, t2, t3 = st.columns(3)

    # Using the exact Category 1 links requested
    
    with t1:
        st.markdown("""
        <div class="trend-card">
            <span class="trend-flag">🇮🇳</span>
            <div class="trend-title">India Trends</div>
            <div class="trend-desc">Click to open Google Trends IN</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🚀 Open India Trends", "https://trends.google.com/trending?geo=IN&hl=en-US&hours=168&category=1", use_container_width=True)

    with t2:
        st.markdown("""
        <div class="trend-card">
            <span class="trend-flag">🇺🇸</span>
            <div class="trend-title">USA Trends</div>
            <div class="trend-desc">Click to open Google Trends US</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🚀 Open USA Trends", "https://trends.google.com/trending?geo=US&hl=en-US&hours=168&category=1", use_container_width=True)

    with t3:
        st.markdown("""
        <div class="trend-card">
            <span class="trend-flag">🇬🇧</span>
            <div class="trend-title">UK Trends</div>
            <div class="trend-desc">Click to open Google Trends UK</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🚀 Open UK Trends", "https://trends.google.com/trending?geo=GB&hl=en-US&hours=168&category=1", use_container_width=True)

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
