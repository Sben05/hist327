# overlay.py

from streamlit.components.v1 import html
from PIL import Image
import io, base64
import streamlit as st

# Shared CSS, animations, and toggle behavior
_CSS = '''
<style>
  .ar-wrapper {
    position: relative;
    max-width: 900px;
    margin: 24px auto;
  }
  .ar-wrapper img {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 12px;
    filter: brightness(0.85);
  }
  .scan-ring {
    position: absolute; top: 50%; left: 50%;
    width: 120px; height: 120px;
    margin: -60px 0 0 -60px;
    border: 2px solid rgba(0,255,255,0.6);
    border-radius: 50%;
    animation: spin 6s linear infinite, pulse 2s ease-in-out infinite alternate;
    z-index: 2;
  }
  .crossh { position: absolute; background: rgba(0,255,255,0.7); z-index:2; }
  .crossh.horiz { width:100%; height:2px; top:50%; left:0; transform:translateY(-50%); }
  .crossh.vert  { height:100%; width:2px; left:50%; top:0; transform:translateX(-50%); }

  /* Toggle button */
  .toggle-btn {
    position: absolute;
    bottom: 12%; right: 12%;
    width: 40px; height: 40px;
    background: rgba(0,0,0,0.6);
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    cursor: pointer;
    z-index: 3;
  }
  .toggle-btn:hover { background: rgba(0,0,0,0.8); }

  /* Overlay panel initially hidden */
  .ar-overlay {
    display: none;
    position: absolute;
    bottom: 5%; left: 50%;
    transform: translateX(-50%) perspective(600px) rotateX(15deg);
    background: rgba(0,0,0,0.8); color: #fff;
    padding: 18px; border-radius: 12px;
    width: 80%; box-shadow: 0 0 20px rgba(0,255,255,0.5);
    font-family: "Segoe UI", sans-serif;
    z-index: 2;
    animation: slideUp 0.8s ease-out forwards;
    opacity: 0;
  }
  .ar-overlay.show {
    display: block;
    opacity: 1;
  }
  .ar-overlay:before {
    content: "";
    position: absolute;
    top: -14px; left: 50%;
    transform: translateX(-50%);
    border-width: 0 14px 14px;
    border-style: solid;
    border-color: transparent transparent rgba(0,0,0,0.8);
  }
  .ar-overlay h3 { margin: 0 0 6px; font-size: 1.4rem; text-shadow: 0 0 10px #0ff; }
  .ar-overlay p { margin: 3px 0; font-size: 1rem; }
  .ar-overlay em { margin-top: 8px; font-size: 0.9rem; color: #ccc; }
  .ar-qa { margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.3); font-size: 0.9rem; }
  .ar-qa .question { color: #0ff; }
  .ar-qa .answer   { color: #afa; margin-top: 4px; }

  @keyframes spin   { 0% { transform: rotate(0); } 100% { transform: rotate(360deg); } }
  @keyframes pulse  { 0% { opacity: 0.4; } 100% { opacity: 1; } }
  @keyframes slideUp {
    from { transform: translateX(-50%) translateY(30px); opacity: 0; }
    to   { transform: translateX(-50%) translateY(0); opacity: 1; }
  }
</style>
'''


def render_camera_overlay(data, qa=None):
  img_file = st.camera_input("📸 Snap your camera to capture the scene")
  if not img_file:
    st.info("👈 Allow camera and capture a frame to see the AR overlay.")
    return
  img = Image.open(img_file)
  b64 = _pil_to_b64(img)
  _render_html(b64, data, qa, is_b64=True)


def render_sample_overlay(data, qa=None):
  st.write("### Sample site view with AR overlay")
  _render_html(data["sample_image_url"], data, qa, is_b64=False)


def _render_html(src, data, qa, is_b64):
  # Build image tag
  img_tag = (f'<img src="data:image/jpeg;base64,{src}" />'
             if is_b64 else f'<img src="{src}" />')

  # Optional QA block
  qa_html = ""
  if qa:
    qa_html = f'''
        <div class="ar-qa">
          <p class="question"><strong>Q:</strong> {qa['q']}</p>
          <p class="answer"><strong>A:</strong> {qa['a']}</p>
        </div>
        '''

  # Full HTML with toggle button and script
  html_code = _CSS + f'''
    <div class="ar-wrapper">
      {img_tag}
      <div class="scan-ring"></div>
      <div class="crossh horiz"></div>
      <div class="crossh vert"></div>
      <div id="toggle-btn" class="toggle-btn">ℹ️</div>
      <div id="overlay-panel" class="ar-overlay">
        <h3>{data['title']}</h3>
        <p><strong>Location:</strong> {data['location']}</p>
        <p>{data['description']}</p>
        <em>{data['quote']}</em>
        {qa_html}
      </div>
    </div>
    <script>
      const btn = document.getElementById('toggle-btn');
      const panel = document.getElementById('overlay-panel');
      btn.onclick = () => panel.classList.toggle('show');
    </script>
    '''
  # Render with adjusted height
  html(html_code, height=650)


def _pil_to_b64(img):
  buf = io.BytesIO()
  img.save(buf, format="JPEG")
  return base64.b64encode(buf.getvalue()).decode()
