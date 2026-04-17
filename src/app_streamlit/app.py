import os
import streamlit as st
import sys
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import random

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)
from src.core.pipeline import AutomatedPipeline

def log_prediction(source_type, source_content, prediction, confidence, reasoning):
    db_path = os.path.join(project_root, "src", "app_flask", "predictions.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_type TEXT,
                source_content TEXT,
                prediction TEXT,
                confidence REAL,
                reasoning TEXT
            )
        ''')
        conn.execute('''
            INSERT INTO predictions (source_type, source_content, prediction, confidence, reasoning)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_type, source_content, prediction, confidence, reasoning))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save to DB: {e}")

# IMPORTANT: Setup page layout
st.set_page_config(page_title="Fake News Detection System", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the Futuristic Theme
st.markdown("""
<style>
/* Hide standard elements securely */
header[data-testid="stHeader"] {display:none;}
footer {display: none;}
[data-testid="collapsedControl"] {display: none;}
section[data-testid="stSidebar"] {display: none !important;}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;600;800&display=swap');

div.stApp {
    background-color: #030712 !important;
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.15), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(59, 130, 246, 0.15), transparent 25%),
        radial-gradient(circle at 50% 80%, rgba(236, 72, 153, 0.1), transparent 25%) !important;
    background-attachment: fixed !important;
    font-family: 'Inter', sans-serif !important;
    color: #f8fafc !important;
}

/* Master Bounded Software App Window */
.block-container {
    padding: 3rem 2.5rem !important;
    max-width: 1400px !important;
    margin-top: 5vh;
    margin-bottom: 5vh;
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Custom Containers */
.top-title {
    text-align: center; 
    font-family: 'Outfit', sans-serif;
    font-size: 2.5rem; 
    font-weight: 800; 
    background: linear-gradient(to right, #ffffff, #a5b4fc);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 30px; 
    letter-spacing: -1px;
    text-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

.glass-panel {
    background: rgba(17, 24, 39, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-panel:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
}

.panel-title { 
    font-family: 'Outfit', sans-serif;
    color: #f8fafc; 
    font-size: 1.2rem; 
    font-weight: 600; 
    margin-bottom: 20px; 
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 10px;
}

/* Sidebar simulation via column */
.sidebar-panel {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 30px 20px;
    height: 100%;
}
.brand-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 800; 
    font-size: 1.4rem; 
    border-bottom: 1px solid rgba(255,255,255,0.05); 
    padding-bottom: 20px; 
    margin-bottom: 20px; 
    text-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Overrides for Inputs/Buttons */
div[data-baseweb="input"] { 
    background-color: rgba(0,0,0,0.4) !important; 
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px;
}
div[data-baseweb="input"]:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
}
div[data-baseweb="select"] { 
    background-color: rgba(0,0,0,0.4) !important; 
    border-radius: 12px;
}

.stButton>button { 
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%); 
    color: white; 
    border: none; 
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
    border-radius: 12px;
    padding: 10px 20px;
    box-shadow: 0 10px 20px rgba(139, 92, 246, 0.2);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px rgba(139, 92, 246, 0.4);
    border: none;
    color: white;
}

.result-card-fake { 
    background: linear-gradient(180deg, rgba(239, 68, 68, 0.15), rgba(153, 27, 27, 0.3)); 
    border: 1px solid rgba(239,68,68,0.4); 
    border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(239,68,68,0.2), inset 0 1px 0 rgba(255,255,255,0.05); 
    text-align: center; 
    padding: 30px; 
    height: 180px; 
}
.result-card-real { 
    background: linear-gradient(180deg, rgba(16, 185, 129, 0.15), rgba(6, 95, 70, 0.3)); 
    border: 1px solid rgba(16,185,129,0.4); 
    border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(16,185,129,0.2), inset 0 1px 0 rgba(255,255,255,0.05); 
    text-align: center; 
    padding: 30px; 
    height: 180px; 
}
.sentiment-box { 
    background: linear-gradient(180deg, rgba(59, 130, 246, 0.15), rgba(30, 58, 138, 0.3)); 
    border: 1px solid rgba(59,130,246,0.4); 
    border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(59,130,246,0.2), inset 0 1px 0 rgba(255,255,255,0.05); 
    text-align: center; 
    padding: 30px; 
    height: 180px;
}

.stat-box { 
    background: rgba(255, 255, 255, 0.02); 
    border: 1px solid rgba(255,255,255,0.05); 
    border-radius: 16px; 
    padding: 20px; 
    height: 240px;
    transition: transform 0.3s ease;
}
.stat-box:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.03);
}
</style>
""", unsafe_allow_html=True)

# Application state
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyB8hzixiGLWiYBLkH4Pgh-sy8G-PlH3m6s")
if "current_view" not in st.session_state:
    st.session_state.current_view = "Fetch News"

# Main Container using actual Streamlit Columns
st.markdown("<div class='top-title'>— Fake News Detection System —</div>", unsafe_allow_html=True)


layout_col_left, layout_col_right = st.columns([1, 4])

with layout_col_left:
    st.markdown("""
        <div class="sidebar-panel" style="padding-bottom: 0;">
            <div class="brand-title">👁️ Fake News System</div>
    """, unsafe_allow_html=True)
    
    # CSS hack to style these specific columns buttons to look like nav links
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-of-type(1) .stButton>button {
        background: transparent; justify-content: flex-start; box-shadow: none; border: none; color: #94a3b8; font-size: 1rem; font-weight: 500; padding: 15px; margin-bottom: 5px; border-radius: 8px;
    }
    div[data-testid="column"]:nth-of-type(1) .stButton>button:hover { background: rgba(255,255,255,0.05); color: white; }
    </style>
    """, unsafe_allow_html=True)

    if st.button("🏠 Home", use_container_width=True): st.session_state.current_view = "Home"
    
    # Highlight logic purely visual indication
    f_lbl = "📄 Fetch News" if st.session_state.current_view != "Fetch News" else "📄 Fetch News  ›"
    if st.button(f_lbl, use_container_width=True): st.session_state.current_view = "Fetch News"
    
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.current_view = "Dashboard"
    
    h_lbl = "🕰️ History" if st.session_state.current_view != "History" else "🕰️ History  ›"
    if st.button(h_lbl, use_container_width=True): st.session_state.current_view = "History"
        
        
    st.markdown("</div>", unsafe_allow_html=True)

with layout_col_right:
    
    if st.session_state.current_view == "History":
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>🕰️ Scan History</div>", unsafe_allow_html=True)
        try:
            db_path = os.path.join(project_root, "src", "app_flask", "predictions.db")
            conn = sqlite3.connect(db_path)
            history_df = pd.read_sql_query("SELECT timestamp, source_content, prediction, confidence FROM predictions ORDER BY timestamp DESC LIMIT 50", conn)
            conn.close()
            
            if not history_df.empty:
                # Format for display
                history_df['confidence'] = (history_df['confidence'] * 100).round(1).astype(str) + '%'
                history_df.rename(columns={'timestamp': 'Date & Time', 'source_content': 'Analyzed Content', 'prediction': 'Result', 'confidence': 'AI Confidence'}, inplace=True)
                
                # Use st.dataframe with custom styling logic if possible, or just raw
                st.dataframe(history_df, use_container_width=True, hide_index=True)
            else:
                st.info("No system history recorded yet. Run a scan to see it here!")
        except Exception as e:
            st.error(f"Cannot load history database: {e}")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif st.session_state.current_view == "Fetch News":
        if "fetched_articles" not in st.session_state:
            st.session_state.fetched_articles = []
        if "analyze_target" not in st.session_state:
            st.session_state.analyze_target = ""

        # --- FETCH NEWS ROW ---
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Fetch Latest News</div>", unsafe_allow_html=True)
        r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1.5, 1.5, 2, 1])
        with r1_col1:
            category = st.selectbox("Category", ["General", "Technology", "Health", "Business", "Sports"], label_visibility="collapsed")
        with r1_col2:
            country_name = st.selectbox("Country", ["India", "USA", "UK", "Global"], label_visibility="collapsed")
            country_map = {"India": "in", "USA": "us", "UK": "gb", "Global": ""}
            country_code = country_map.get(country_name, "us")
        with r1_col3:
            date_range = st.text_input("Date range", "YYYY-MM-DD", label_visibility="collapsed", placeholder="e.g. 2024-04-01")
        with r1_col4:
            fetch_btn = st.button("Fetch News", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if fetch_btn:
            with st.spinner(f"Fetching {category} news..."):
                from src.core.news_api_fetcher import NewsAPIFetcher
                api_key = "14543106a2f2410c9b1bf2addd2e7cb8" # explicitly set new working key
                fetcher = NewsAPIFetcher(api_key=api_key)
                
                cat_lower = category.lower()
                c_code = country_code if country_code else None
                from_date = date_range if date_range and date_range != "YYYY-MM-DD" else None
                
                result = fetcher.fetch_news(category=cat_lower, country=c_code, from_date=from_date, page_size=5)
                
                if "error" in result:
                    st.error(f"Failed to fetch news: {result['error']}")
                else:
                    articles = result.get("articles", [])
                    st.session_state.fetched_articles = articles
                    if not articles:
                        st.warning("No articles found.")
                    else:
                        st.success(f"Fetched {len(articles)} articles!")

        if st.session_state.fetched_articles:
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-title'>Fetched Articles</div>", unsafe_allow_html=True)
            for i, article in enumerate(st.session_state.fetched_articles):
                with st.expander(f"{i+1}. {article['title']} - {article['source_name']}"):
                    st.write(f"**Published:** {article['published_at']}")
                    st.write(article.get('description', 'No description available.'))
                    if st.button(f"Analyze this Article", key=f"analyze_fetched_{i}"):
                        st.session_state.analyze_target = article.get('content') or article.get('description') or article['title']
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # --- ENTER ARTICLE ROW ---
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Enter News Article</div>", unsafe_allow_html=True)
        
        # Use session state to link the prefilled input
        user_input = st.text_input("Input", key="analyze_target", label_visibility="collapsed", placeholder="Paste article text here...")
        
        st.write("")
        btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 1])
        with btn_c2:
            check_btn = st.button("✔️ Check News", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- RESULT PANELS ---
        if check_btn and user_input:
            with st.spinner("Analyzing context..."):
                pipeline = AutomatedPipeline(api_key=st.session_state.api_key)
                
                is_url = user_input.startswith("http://") or user_input.startswith("https://")
                if is_url:
                    result_data = pipeline.run_url(user_input)
                    log_content = result_data.get("original_title", user_input)
                else:
                    result_data = pipeline.run_text(user_input)
                    log_content = user_input[:300]
                
                if "error" in result_data:
                    st.error(f"Error: {result_data['error']}")
                else:
                    result = result_data.get("result", "UNKNOWN")
                    confidence = float(result_data.get("confidence", 0.0))
                    reasoning = result_data.get("reasoning", "Analysis complete.")
                    
                    if result in ["REAL", "FAKE"]:
                        log_prediction("URL" if is_url else "TEXT", log_content, result, confidence, reasoning)

                    sentiment = "Negative" if result == "FAKE" else "Positive"
                    
                    res_c1, res_c2 = st.columns(2)
                    
                    with res_c1:
                        if result == "FAKE":
                            st.markdown(f"""
                            <div class='result-card-fake'>
                                <h2 style='margin:0; color:white;'>FAKE NEWS</h2>
                                <h4 style='color:white;'>Confidence: {confidence*100:.0f}%</h4>
                                <div style='background:rgba(0,0,0,0.3); height:10px; border-radius:5px; margin-top:20px; border: 1px solid rgba(255,255,255,0.1);'>
                                    <div style='background: linear-gradient(90deg, #ef4444, #ff7b7b); width:{confidence*100}%; height:100%; border-radius:5px; box-shadow: 0 0 10px #ef4444;'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                             st.markdown(f"""
                            <div class='result-card-real'>
                                <h2 style='margin:0; color:white;'>REAL NEWS</h2>
                                <h4 style='color:white;'>Confidence: {confidence*100:.0f}%</h4>
                                <div style='background:rgba(0,0,0,0.3); height:10px; border-radius:5px; margin-top:20px; border: 1px solid rgba(255,255,255,0.1);'>
                                    <div style='background: linear-gradient(90deg, #10b981, #34d399); width:{confidence*100}%; height:100%; border-radius:5px; box-shadow: 0 0 10px #10b981;'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                    with res_c2:
                        sent_color = "#fca5a5" if sentiment == "Negative" else "#6ee7b7"
                        st.markdown(f"""
                        <div class='sentiment-box'>
                            <h3 style='margin:0; color: #f8fafc;'>Sentiment Analysis</h3>
                            <hr style='border-color:rgba(255,255,255,0.1); margin:15px 0;'>
                            <h2 style='margin:0; color:{sent_color};'>{sentiment}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("")
                    bot_c1, bot_c2, bot_c3 = st.columns(3)
                    
                    with bot_c1:
                        st.markdown("<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ News Classification</div>", unsafe_allow_html=True)
                        fake_pct = int(confidence*100) if result == "FAKE" else 100 - int(confidence*100)
                        fig = go.Figure(data=[go.Pie(labels=['Fake News', 'Real News'], values=[fake_pct, 100-fake_pct], hole=0.4, marker=dict(colors=["#ef4444", "#3b82f6"]))])
                        fig.update_layout(height=160, margin=dict(t=10, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(font=dict(color="white")))
                        fig.update_traces(textinfo='none')
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with bot_c2:
                        st.markdown("<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ Fake News Trend</div>", unsafe_allow_html=True)
                        fig2 = go.Figure(data=go.Scatter(x=['May', 'June', 'Jul', 'Aug'], y=[10, 25, 18, 28], mode='lines+markers', line=dict(color='#ef4444', width=2)))
                        fig2.update_layout(height=160, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='white')), xaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', size=10)))
                        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with bot_c3:
                        st.markdown("<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ Source Credibility</div><br>", unsafe_allow_html=True)
                        words = [("Hoax", "#fca5a5", "18px"), ("Scandal", "#60a5fa", "15px"), ("Conspiracy", "#ef4444", "20px"), 
                                 ("Shocking", "#f87171", "18px"), ("Exposed", "#f8fafc", "16px"), ("bias", "#ef4444", "14px")]
                        wc_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; padding:10px; align-items:center; justify-content:center;'>"
                        for w, c, s in words:
                            wc_html += f"<span style='color:{c}; font-size:{s}; font-weight:bold;'>{w}</span>"
                        wc_html += "</div></div>"
                        st.markdown(wc_html, unsafe_allow_html=True)

        else:
            # Placeholders
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.markdown("<div class='result-card-fake' style='background:rgba(20,25,45,0.5); box-shadow:none; border: 1px dashed rgba(255,255,255,0.2)'><h2 style='color:#64748b;'>AWAITING</h2></div>", unsafe_allow_html=True)
            with res_c2:
                 st.markdown("<div class='sentiment-box' style='background:rgba(20,25,45,0.5); box-shadow:none; border: 1px dashed rgba(255,255,255,0.2)'><h3 style='color:#64748b;'>Sentiment Analysis</h3></div>", unsafe_allow_html=True)
            st.write("")
            bot_c1, bot_c2, bot_c3 = st.columns(3)
            for col, title in [(bot_c1, "News Classification"), (bot_c2, "Fake News Trend"), (bot_c3, "Source Credibility")]:
                with col:
                    st.markdown(f"<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ {title}</div></div>", unsafe_allow_html=True)
    
    elif st.session_state.current_view == "Dashboard":
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>📊 Analytics Dashboard (Admin)</div>", unsafe_allow_html=True)
        
        try:
            db_path = os.path.join(project_root, "src", "app_flask", "predictions.db")
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM predictions", conn)
            conn.close()
            
            if df.empty:
                st.info("No prediction data available yet!")
            else:
                # Top metrics row
                col1, col2, col3, col4 = st.columns(4)
                total_predictions = len(df)
                fake_count = len(df[df['prediction'] == 'FAKE'])
                real_count = len(df[df['prediction'] == 'REAL'])
                avg_conf = (df['confidence'].mean() * 100) if not df.empty else 0
                
                with col1:
                    st.markdown(f"<div class='stat-box' style='height: auto;'><div style='color:#94a3b8;'>Total Scans</div><h2 style='color:white; margin:0;'>{total_predictions}</h2></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='stat-box' style='height: auto;'><div style='color:#ef4444;'>Fake Detected</div><h2 style='color:white; margin:0;'>{fake_count}</h2></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='stat-box' style='height: auto;'><div style='color:#10b981;'>Real Verified</div><h2 style='color:white; margin:0;'>{real_count}</h2></div>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<div class='stat-box' style='height: auto;'><div style='color:#3b82f6;'>Avg Confidence</div><h2 style='color:white; margin:0;'>{avg_conf:.1f}%</h2></div>", unsafe_allow_html=True)
                
                st.write("")
                # Convert timestamps for charting
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.markdown("<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ Prediction Distribution</div>", unsafe_allow_html=True)
                    # Donut chart
                    fig = go.Figure(data=[go.Pie(labels=['Fake', 'Real'], values=[fake_count, real_count], hole=0.5, marker=dict(colors=["#ef4444", "#10b981"]))])
                    fig.update_layout(height=170, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with chart_col2:
                    st.markdown("<div class='stat-box'><div style='color:#94a3b8; font-weight:bold;'>▪ Scans over Time</div>", unsafe_allow_html=True)
                    # Time series chart
                    daily_counts = df.groupby('date').size().reset_index(name='counts')
                    fig2 = go.Figure(data=go.Scatter(x=daily_counts['date'], y=daily_counts['counts'], fill='tozeroy', line=dict(color='#3b82f6')))
                    fig2.update_layout(height=170, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
                    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Cannot load dashboard data: {e}")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif st.session_state.current_view == "Home":
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>🏠 Welcome to TruthSeeker PRO</div>", unsafe_allow_html=True)
        st.info("Select 'Fetch News' from the sidebar to analyze live data, or 'Dashboard' to view system metrics.")
        st.markdown("</div>", unsafe_allow_html=True)
