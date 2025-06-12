# main.py

import re
import streamlit as st
import openai
from streamlit_lottie import st_lottie
from data import events
from overlay import render_camera_overlay, render_sample_overlay
import requests

# 1) Page config (MUST be first)
st.set_page_config(page_title="AR Violence Tour", layout="wide")

# 2) Together.ai (Mistral) setup
openai.api_key = "9c035ced6c9f77a29672dc9eb7857f13526f410c30c63d10641739648132ce81"
openai.api_base = "https://api.together.xyz"

# 3) --- Sidebar: styling controls ---
st.sidebar.markdown("## 🎨 Theme & Style")

# 3a) Theme picker
themes = {
    "Dark Purple": "background: linear-gradient(to right, #1f1c2c, #928dab);",
    "Sunset":
    "background: linear-gradient(to right, #ff8177, #ff867a, #ff8c7f, #f99185, #cf556c, #b12a5b);",
    "Neon Blue": "background: linear-gradient(to right, #000046, #1cb5e0);",
}
theme_choice = st.sidebar.selectbox("Background Theme", list(themes.keys()))

# 3b) Scan-ring color picker
ring_color = st.sidebar.color_picker("🔆 Scan-Ring Color", "#00fff0")

# 3c) Info-panel opacity
panel_opacity = st.sidebar.slider("📐 Panel Opacity", 0.2, 1.0, 0.8, 0.05)

# 3d) Scan-ring speed
scan_speed = st.sidebar.slider("⏱ Scan-Ring Speed (s)", 2.0, 10.0, 6.0, 0.5)

# 4) Inject dynamic CSS overrides
st.markdown(f"""
<style>
  .reportview-container {{
    {themes[theme_choice]}
    color: #f0f0f0;
  }}
  .scan-ring {{
    border-color: {ring_color} !important;
    animation-duration: {scan_speed}s !important;
  }}
  .ar-overlay {{
    background: rgba(0,0,0,{panel_opacity}) !important;
    box-shadow: 0 0 20px {ring_color} !important;
  }}
</style>
""",
            unsafe_allow_html=True)


# 5) Lottie animation at top
def load_lottie(url):
  r = requests.get(url)
  if r.status_code == 200:
    return r.json()
  return None


lottie_anim = load_lottie(
    "https://assets7.lottiefiles.com/packages/lf20_tll0j4bb.json")
if lottie_anim:
  st_lottie(lottie_anim, height=150)

# 6) Sidebar: choose mode & event
st.sidebar.markdown("---")
st.sidebar.title("AR Modes")
mode = st.sidebar.radio("View Mode", ["📷 Camera View", "🖼️ Sample Image"])
event_key = st.sidebar.selectbox("Event", list(events.keys()))
data = events[event_key]

# 7) Header & Tabs
st.title("📍 Histories of Violence – AR Tour")
tabs = st.tabs(["AR Overlay", "Event Details", "AI Q&A"])

# Extract year
year = re.search(r"\((\d{4})\)", event_key).group(1)

with tabs[0]:
  c1, c2 = st.columns(2)
  c1.metric("📅 Year", year)
  c2.metric("📍 Location", data["location"])
  st.subheader(f"🔍 {data['title']}")
  if mode == "📷 Camera View":
    render_camera_overlay(data)
  else:
    render_sample_overlay(data)

with tabs[1]:
  st.header("📝 Event Details")
  st.markdown(f"**Description:** {data['description']}")
  st.markdown(f"**Quote:** *{data['quote']}*")
  with st.expander("🕵️ Additional Facts"):
    for fact in data.get("facts", []):
      st.write(f"- {fact}")

with tabs[2]:
  st.header("🤖 AI Q&A")
  question = st.text_input("Ask a question about this event")
  if question:
    with st.spinner("AI Analysis"):
      prompt = (
          f"Context is {data['title']}, answer the question in those terms.\n"
          f"Question: {question}")
      try:
        resp = openai.ChatCompletion.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
        )
        st.success(resp.choices[0].message.content.strip())
      except Exception as e:
        st.error(f"API error: {e}")
