import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import wave
import base64
import random

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Happy Birthday Ayesha 🎂",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

PIN = "2002"
PAGE_ORDER = ["home", "wishes", "quotes", "prayers", "gift", "cake", "finale"]

# ------------------------------------------------------------------
# GLOBAL CSS — dark, premium, glowing theme. No sidebar is used anywhere.
# ------------------------------------------------------------------
def inject_global_css():
    st.markdown(
        """
        <style>
        #MainMenu, header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            visibility: hidden; display: none;
        }
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 50% 0%, #241b45 0%, #140e2b 45%, #0a0716 100%);
        }
        [data-testid="stAppViewContainer"] .main .block-container {
            animation: pageFadeSlide 0.6s ease;
            max-width: 560px;
            padding-top: 2rem;
        }
        @keyframes pageFadeSlide {
            0%   { opacity: 0; transform: translateY(22px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        h1, h2, h3, h4 { color: #ffd7ea !important; text-shadow: 0 0 18px rgba(255,111,174,0.35); }
        p, span, label, .stMarkdown { color: #ece4ff; }
        div.stButton > button {
            transition: transform 0.15s ease, box-shadow 0.25s ease;
            border-radius: 14px !important;
            border: 1px solid rgba(255,111,174,0.35) !important;
            box-shadow: 0 0 14px rgba(255,111,174,0.15);
            color: #f5e9ff !important;
        }
        div.stButton > button:hover {
            box-shadow: 0 0 22px rgba(255,111,174,0.45);
        }
        div.stButton > button:active { transform: scale(0.96); }
        .glow-card {
            padding: 24px; border-radius: 20px; text-align: center;
            background: linear-gradient(145deg, #1c1436, #241b45);
            border: 1px solid rgba(255,111,174,0.25);
            box-shadow: 0 0 30px rgba(255,111,174,0.18), inset 0 0 30px rgba(160,107,255,0.08);
        }
        @media (max-width: 640px) {
            .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_global_css()

# ------------------------------------------------------------------
# BEEP SOUND GENERATOR
# ------------------------------------------------------------------
def make_beep(freq=880, duration=0.25, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * t * 2 * np.pi)
    audio = (tone * volume * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return buf.getvalue()


def play_beep(freq=880, duration=0.25, volume=0.5):
    data = make_beep(freq, duration, volume)
    b64 = base64.b64encode(data).decode()
    components.html(
        f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
        height=0, width=0,
    )


def play_happy_chime():
    data1 = make_beep(659, 0.12, 0.4)
    data2 = make_beep(784, 0.12, 0.4)
    data3 = make_beep(988, 0.18, 0.4)
    combined = data1[44:] + data2[44:] + data3[44:]
    header = data1[:44]
    b64 = base64.b64encode(header + combined).decode()
    components.html(
        f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
        height=0, width=0,
    )


# ------------------------------------------------------------------
# BACKGROUND MUSIC — nasheed-style (voice-like hum + daf/frame-drum
# percussion, no melodic instruments), with an optional custom upload.
#
# NOTE: I can't embed a real, copyrighted nasheed recording or generate
# authentic sung vocals — so this is a synthesized approximation built
# only from a wordless vocal-style hum and hand-drum percussion, in the
# spirit of traditional nasheed (voice + daf, no instruments). If you
# have a royalty-free nasheed file of your own, upload it below and
# it'll be used instead.
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def make_nasheed_style_track():
    sample_rate = 22050
    # a simple, repeating vocal-style melodic phrase (monophonic, like a
    # chant) — no chords/instruments, just a single voice-like line
    phrase = [330, 370, 392, 440, 392, 370, 330, 294, 330, 392, 440, 392]
    note_dur = 0.55
    vocal = np.array([], dtype=np.float32)
    for freq in phrase:
        t = np.linspace(0, note_dur, int(sample_rate * note_dur), False)
        envelope = np.sin(np.pi * t / note_dur) ** 0.6
        # breathy, voice-like timbre: fundamental + soft overtones, slight vibrato
        vibrato = 1 + 0.006 * np.sin(2 * np.pi * 5 * t)
        tone = np.sin(freq * vibrato * t * 2 * np.pi)
        tone += 0.25 * np.sin(freq * 2 * vibrato * t * 2 * np.pi)
        tone += 0.12 * np.sin(freq * 3 * vibrato * t * 2 * np.pi)
        vocal = np.concatenate([vocal, tone * envelope])

    # daf / frame-drum style percussion hits under the vocal line
    total_len = len(vocal)
    drum = np.zeros(total_len, dtype=np.float32)
    beat_samples = int(sample_rate * note_dur)
    rng = np.random.default_rng(42)
    for i in range(0, total_len, beat_samples):
        hit_len = int(sample_rate * 0.09)
        end = min(i + hit_len, total_len)
        seg_len = end - i
        if seg_len <= 0:
            continue
        noise = rng.uniform(-1, 1, seg_len)
        env = np.exp(-np.linspace(0, 10, seg_len))
        drum[i:end] += noise * env * 0.35

    mixed = vocal * 0.55 + drum
    mixed = mixed / np.max(np.abs(mixed))
    pcm = (mixed * 0.3 * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return base64.b64encode(buf.getvalue()).decode()


def render_music_toggle():
    if "music_on" not in st.session_state:
        st.session_state.music_on = False
    if "custom_music_b64" not in st.session_state:
        st.session_state.custom_music_b64 = None
        st.session_state.custom_music_mime = None

    with st.expander("🎙️ Use your own nasheed file (optional)"):
        uploaded = st.file_uploader("Upload an mp3/wav", type=["mp3", "wav"], key="nasheed_upload")
        if uploaded is not None:
            st.session_state.custom_music_b64 = base64.b64encode(uploaded.getvalue()).decode()
            st.session_state.custom_music_mime = uploaded.type or "audio/mpeg"
            st.success("Your nasheed will play instead of the default track. 🎶")

    if st.session_state.custom_music_b64:
        b64 = st.session_state.custom_music_b64
        mime = st.session_state.custom_music_mime
    else:
        b64 = make_nasheed_style_track()
        mime = "audio/wav"

    label = "⏸️ Pause Music" if st.session_state.music_on else "🎵 Play Music"
    if st.button(label, key="music_toggle", use_container_width=True):
        st.session_state.music_on = not st.session_state.music_on
    if st.session_state.music_on:
        components.html(
            f"""
            <audio id="bgm" autoplay loop>
                <source src="data:{mime};base64,{b64}">
            </audio>
            <script>
                const bgm = document.getElementById('bgm');
                bgm.volume = 0.32;
                const saved = localStorage.getItem('bgm_time');
                if (saved) {{ try {{ bgm.currentTime = parseFloat(saved); }} catch(e) {{}} }}
                setInterval(() => {{
                    if (!bgm.paused) localStorage.setItem('bgm_time', bgm.currentTime);
                }}, 1000);
            </script>
            """,
            height=0, width=0,
        )


# ------------------------------------------------------------------
# TYPING TEXT ANIMATION
# ------------------------------------------------------------------
def typing_animation(text, speed_ms=80, size_px=30, height=90):
    safe_text = text.replace("'", "\\'")
    components.html(
        f"""
        <div style="text-align:center;font-family:'Trebuchet MS',sans-serif;
                    font-weight:800;font-size:{size_px}px;color:#ff9dc9;
                    text-shadow:0 0 18px rgba(255,111,174,0.55);
                    min-height:{size_px + 10}px;">
            <span id="typed"></span><span class="cursor">|</span>
        </div>
        <style>
            .cursor {{ animation: blink 0.8s infinite; }}
            @keyframes blink {{ 50% {{ opacity: 0; }} }}
        </style>
        <script>
            const txt = '{safe_text}';
            let i = 0;
            const el = document.getElementById('typed');
            function type() {{
                if (i < txt.length) {{
                    el.innerHTML += txt.charAt(i);
                    i++;
                    setTimeout(type, {speed_ms});
                }}
            }}
            type();
        </script>
        """,
        height=height,
    )


# ------------------------------------------------------------------
# STICKER / PETAL / MOON ANIMATIONS (dark-theme backdrops)
# ------------------------------------------------------------------
def animated_background(height=220, density="normal"):
    stickers = ["🎈", "🎉", "✨", "💖", "🎂", "🌸", "🎁", "🦋", "⭐", "💫", "🩷"]
    count = 18 if density == "normal" else 26
    items = ""
    for i in range(count):
        emoji = random.choice(stickers)
        left = random.randint(0, 96)
        delay = round(random.uniform(0, 6), 2)
        duration = round(random.uniform(6, 12), 2)
        size = random.randint(18, 34)
        items += f"""
        <div class="sticker" style="left:{left}%;font-size:{size}px;
            animation-delay:{delay}s;animation-duration:{duration}s;">{emoji}</div>
        """
    components.html(
        f"""
        <div class="sticker-field">{items}</div>
        <style>
            .sticker-field {{
                position: relative; width: 100%; height: {height}px;
                overflow: hidden; border-radius: 18px;
                background: radial-gradient(circle at 50% 100%, #2c2154 0%, #171029 70%);
            }}
            .sticker {{
                position: absolute; bottom: -50px;
                animation-name: floatUp; animation-timing-function: ease-in-out;
                animation-iteration-count: infinite; opacity: 0.9;
                filter: drop-shadow(0 0 6px rgba(255,111,174,0.4));
            }}
            @keyframes floatUp {{
                0%   {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
                10%  {{ opacity: 1; }}
                50%  {{ transform: translateY(-140px) rotate(15deg); }}
                100% {{ transform: translateY(-280px) rotate(-10deg); opacity: 0; }}
            }}
        </style>
        """,
        height=height + 10,
    )


def floating_petals(height=140):
    petals = ["🌹", "🥀", "🌸"]
    items = ""
    for i in range(16):
        emoji = random.choice(petals)
        left = random.randint(0, 96)
        delay = round(random.uniform(0, 6), 2)
        duration = round(random.uniform(7, 13), 2)
        size = random.randint(16, 30)
        items += f"""
        <div class="petal" style="left:{left}%;font-size:{size}px;
            animation-delay:{delay}s;animation-duration:{duration}s;">{emoji}</div>
        """
    components.html(
        f"""
        <div class="petal-field">{items}</div>
        <style>
            .petal-field {{
                position: relative; width: 100%; height: {height}px;
                overflow: hidden; border-radius: 18px;
                background: radial-gradient(circle at 50% 0%, #33203f 0%, #170e22 75%);
            }}
            .petal {{
                position: absolute; top: -40px;
                animation-name: petalFall; animation-timing-function: ease-in-out;
                animation-iteration-count: infinite; opacity: 0.9;
            }}
            @keyframes petalFall {{
                0%   {{ transform: translateY(0) translateX(0) rotate(0deg); opacity: 0; }}
                10%  {{ opacity: 1; }}
                50%  {{ transform: translateY({height*0.55}px) translateX(20px) rotate(120deg); }}
                100% {{ transform: translateY({height+40}px) translateX(-15px) rotate(260deg); opacity: 0; }}
            }}
        </style>
        """,
        height=height + 10,
    )


def moon_stars_scene(height=200):
    stars = ""
    for i in range(45):
        top = random.randint(0, 85)
        left = random.randint(0, 98)
        delay = round(random.uniform(0, 4), 2)
        size = random.choice([2, 3, 4])
        stars += f"""
        <div class="star" style="top:{top}%;left:{left}%;
            width:{size}px;height:{size}px;animation-delay:{delay}s;"></div>
        """
    components.html(
        f"""
        <div class="night-sky">{stars}<div class="moon"></div></div>
        <style>
            .night-sky {{
                position: relative; width: 100%; height: {height}px;
                overflow: hidden; border-radius: 18px;
                background: linear-gradient(180deg, #1a1233 0%, #2f1f4d 55%, #4a2b52 100%);
            }}
            .moon {{
                position: absolute; top: 22px; right: 30px;
                width: 60px; height: 60px; border-radius: 50%;
                background: #fff6d8;
                box-shadow: 0 0 35px 12px rgba(255, 246, 216, 0.55);
            }}
            .star {{
                position: absolute; background: #fff; border-radius: 50%;
                animation: twinkle 2.4s ease-in-out infinite;
            }}
            @keyframes twinkle {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
        </style>
        """,
        height=height + 10,
    )


def confetti_burst(height=200, duration_ms=4000):
    components.html(
        f"""
        <canvas id="confetti-canvas-{random.randint(0,999999)}" class="confetti-cv"
            style="width:100%;height:{height}px;display:block;"></canvas>
        <script>
        const canvases = document.getElementsByClassName('confetti-cv');
        const canvas = canvases[canvases.length - 1];
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = {height};
        const colors = ['#ff6b9d','#ffd93d','#6bd4ff','#a06bff','#6bffb0','#ff9f6b'];
        let pieces = [];
        for (let i=0;i<140;i++){{
            pieces.push({{
                x: Math.random()*canvas.width, y: Math.random()*-canvas.height,
                r: Math.random()*6+4, c: colors[Math.floor(Math.random()*colors.length)],
                spX: Math.random()*2-1, spY: Math.random()*3+2, rot: Math.random()*360
            }});
        }}
        let start = null;
        function draw(ts){{
            if(!start) start = ts;
            ctx.clearRect(0,0,canvas.width,canvas.height);
            pieces.forEach(p=>{{
                p.x += p.spX; p.y += p.spY; p.rot += 4;
                if(p.y>canvas.height){{ p.y = -10; p.x = Math.random()*canvas.width; }}
                ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot*Math.PI/180);
                ctx.fillStyle = p.c; ctx.fillRect(-p.r/2,-p.r/2,p.r,p.r*0.6); ctx.restore();
            }});
            if (ts - start < {duration_ms}) requestAnimationFrame(draw);
        }}
        requestAnimationFrame(draw);
        </script>
        """,
        height=height + 10,
    )


def fireworks_finale(height=300):
    components.html(
        f"""
        <canvas id="fw-canvas" style="width:100%;height:{height}px;display:block;
            background:linear-gradient(180deg,#1a1233 0%,#3a1f45 60%,#4a2b52 100%);
            border-radius:18px;"></canvas>
        <script>
        const canvas = document.getElementById('fw-canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = {height};
        const colors = ['#ff6b9d','#ffd93d','#6bd4ff','#c08bff','#6bffb0','#ff9f6b','#ffffff'];
        class Firework {{
            constructor() {{
                this.x = Math.random()*canvas.width; this.y = canvas.height;
                this.targetY = Math.random()*canvas.height*0.45 + 20;
                this.speed = 4 + Math.random()*2; this.exploded = false; this.particles = [];
                this.color = colors[Math.floor(Math.random()*colors.length)];
            }}
            update() {{
                if (!this.exploded) {{
                    this.y -= this.speed;
                    if (this.y <= this.targetY) {{
                        this.exploded = true;
                        for (let i=0;i<40;i++) {{
                            const angle = (Math.PI*2*i)/40;
                            const speed = Math.random()*3+1.5;
                            this.particles.push({{x:this.x, y:this.y,
                                vx:Math.cos(angle)*speed, vy:Math.sin(angle)*speed,
                                life:60, color: colors[Math.floor(Math.random()*colors.length)]}});
                        }}
                    }}
                }} else {{
                    this.particles.forEach(p=>{{ p.x += p.vx; p.y += p.vy; p.vy += 0.03; p.life -= 1; }});
                    this.particles = this.particles.filter(p=>p.life>0);
                }}
            }}
            draw() {{
                if (!this.exploded) {{
                    ctx.beginPath(); ctx.arc(this.x, this.y, 2.5, 0, Math.PI*2);
                    ctx.fillStyle = this.color; ctx.fill();
                }} else {{
                    this.particles.forEach(p=>{{
                        ctx.beginPath(); ctx.globalAlpha = Math.max(p.life/60, 0);
                        ctx.arc(p.x, p.y, 2, 0, Math.PI*2);
                        ctx.fillStyle = p.color; ctx.fill(); ctx.globalAlpha = 1;
                    }});
                }}
            }}
            isDone() {{ return this.exploded && this.particles.length === 0; }}
        }}
        let fireworks = []; let frame = 0;
        function loop() {{
            ctx.fillStyle = 'rgba(20,5,30,0.15)'; ctx.fillRect(0,0,canvas.width,canvas.height);
            if (frame % 35 === 0) fireworks.push(new Firework());
            fireworks.forEach(f=>{{ f.update(); f.draw(); }});
            fireworks = fireworks.filter(f=>!f.isDone());
            frame++; requestAnimationFrame(loop);
        }}
        loop();
        </script>
        """,
        height=height + 10,
    )


# ------------------------------------------------------------------
# CONTENT
# ------------------------------------------------------------------
QUOTES = [
    "A sister is a gift to the heart, a friend to the spirit, a golden thread to the meaning of life.",
    "Sisters share the scent and smells — the feelings of a common childhood.",
    "Having a sister means you'll always have a best friend, no matter what.",
    "Sisters are different flowers from the same garden.",
    "Life's better with a sister like you around.",
]

WISHES = [
    "Happy 24th Birthday to the best sister in the whole world! May this year bring you endless smiles.",
    "You've grown into someone so strong, kind, and full of light — I'm so proud to be your brother.",
    "May Allah bless you with health, happiness, and every success you dream of, Apa.",
    "Here's to another year of laughter, chai, and all our silly fights that end in hugs.",
    "No matter how far or busy life gets, you'll always be my favorite person.",
]

PRAYERS = [
    "Ya Allah, bless my sister with a life full of peace, good health, and happiness. Ameen.",
    "May Allah grant you success in everything you pursue and ease in every hardship. Ameen.",
    "May your Iman grow stronger every year, and may Allah keep you under His protection always. Ameen.",
    "May Allah accept your good deeds and grant you Jannah, Ameen. Happy Birthday, Apa.",
]

NO_BEEP_MESSAGES = [
    "Aray Apa nahi chalay ga! Ek chotay bhai ki mehnat ko dekhna to parega 😤🎈",
    "Nooo you can't skip this — click 'Yes' na, mera dil toot jaye ga 🥺💔",
    "Beep beep! This website has zero 'No' tolerance today, it's YOUR day 🎉",
    "Try again, Apa. The 'No' button is just decoration today 😏🎁",
]

BROTHER_LETTER = """
Dear Ayesha,

Twenty-four years of you being my sister, and I still don't have the words
to thank you properly — so I built you this instead.

Thank you for every time you looked out for me, believed in me, and made
our home feel warmer just by being in it. I pray this year brings you
everything you deserve: peace, success, good health, and joy that never
runs out.

I love you, Apa. Happy Birthday.
"""

SIGNATURE_HTML = """
<div style='text-align:center;margin-top:18px;'>
    <hr style='width:40%;margin:0 auto 10px auto;border:none;
        border-top:1px solid rgba(255,111,174,0.3);'>
    <p style='font-style:italic;font-size:16px;color:#ff9dc9;'>
        With love and prayers,<br>
        <span style='font-size:18px;font-weight:700;'>— Muhammad Abdullah ❤️</span>
    </p>
</div>
"""


def yes_no_section(key, question, on_yes):
    st.markdown(f"#### {question}")
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes", key=f"{key}_yes", use_container_width=True):
        play_happy_chime()
        on_yes()
    if c2.button("❌ No", key=f"{key}_no", use_container_width=True):
        play_beep(300, 0.3, 0.5)
        st.warning(random.choice(NO_BEEP_MESSAGES))


def next_button(label="Next ➜"):
    """The ONLY way to move forward — a single button at the bottom of
    every page. No sidebar, no jump-to-any-page navigation."""
    st.write("")
    st.write("")
    idx = PAGE_ORDER.index(st.session_state.page)
    cols = st.columns([1, 2, 1])
    with cols[1]:
        if st.button(label, key=f"next_{st.session_state.page}", use_container_width=True):
            if idx < len(PAGE_ORDER) - 1:
                st.session_state.page = PAGE_ORDER[idx + 1]
                st.rerun()


def progress_dots():
    """Passive progress indicator only — not clickable, not a navigation bar."""
    idx = PAGE_ORDER.index(st.session_state.page)
    dots = "".join(
        f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;"
        f"margin:0 4px;background:{'#ff6fae' if i <= idx else 'rgba(255,255,255,0.15)'};"
        f"box-shadow:{'0 0 8px rgba(255,111,174,0.8)' if i == idx else 'none'};'></span>"
        for i in range(len(PAGE_ORDER))
    )
    st.markdown(f"<div style='text-align:center;margin-bottom:10px;'>{dots}</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "pin_digits" not in st.session_state:
    st.session_state.pin_digits = ""
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False


# ------------------------------------------------------------------
# LOCK SCREEN — phone-style dial pad
# ------------------------------------------------------------------
def lock_screen():
    st.markdown(
        "<h2 style='text-align:center;'>🌙 A Secret Surprise Awaits</h2>"
        "<p style='text-align:center;color:#c9bfe8;'>Enter the code to unlock it</p>",
        unsafe_allow_html=True,
    )

    if "pin_error" not in st.session_state:
        st.session_state.pin_error = False
    if st.session_state.pin_error:
        st.error("Wrong code — try again 💫")
        st.session_state.pin_error = False

    dots = "".join(
        f"<span style='display:inline-block;width:16px;height:16px;border-radius:50%;"
        f"margin:0 8px;background:{'#ff6fae' if i < len(st.session_state.pin_digits) else 'transparent'};"
        f"border:2px solid #ff6fae;box-shadow:{'0 0 12px #ff6fae' if i < len(st.session_state.pin_digits) else 'none'};'></span>"
        for i in range(4)
    )
    st.markdown(f"<div style='text-align:center;margin:18px 0 22px 0;'>{dots}</div>", unsafe_allow_html=True)

    # Scoped CSS: only the dialpad container gets the light phone-keypad
    # look, with dark text so digits are always clearly visible.
    st.markdown(
        """
        <style>
        .st-key-dialpad {
            background: #e8e8ea; border-radius: 26px; padding: 18px 14px 22px 14px;
        }
        .st-key-dialpad div.stButton > button {
            background: #f6f6f7 !important;
            color: #1a1a1a !important;
            border: none !important;
            border-radius: 40px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
            height: 64px;
            font-size: 26px !important;
            font-weight: 500 !important;
        }
        .st-key-dialpad div.stButton > button:hover {
            background: #ececec !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
        }
        .st-key-dialpad div.stButton > button p { color: #1a1a1a !important; font-size: 26px !important; }
        .st-key-backspace div.stButton > button {
            background: transparent !important; border: none !important;
            box-shadow: none !important; color: #8a8a8a !important;
            font-size: 22px !important;
        }
        .st-key-unlockbtn div.stButton > button {
            background: #2e9e5b !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 40px !important;
            height: 58px;
            font-size: 19px !important;
            font-weight: 600 !important;
            box-shadow: 0 3px 10px rgba(46,158,91,0.5) !important;
        }
        .st-key-unlockbtn div.stButton > button p { color: #ffffff !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def press(digit):
        if len(st.session_state.pin_digits) < 4:
            st.session_state.pin_digits += digit
            if len(st.session_state.pin_digits) == 4:
                check_pin()
        st.rerun()

    def check_pin():
        if st.session_state.pin_digits == PIN:
            play_happy_chime()
            st.session_state.unlocked = True
        else:
            play_beep(220, 0.3, 0.5)
            st.session_state.pin_error = True
            st.session_state.pin_digits = ""

    with st.container(key="backspace"):
        bcols = st.columns([4, 1])
        with bcols[1]:
            if st.button("⌫", key="dial_back"):
                st.session_state.pin_digits = st.session_state.pin_digits[:-1]
                st.rerun()

    with st.container(key="dialpad"):
        grid = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", ""]]
        for r, row in enumerate(grid):
            cols = st.columns(3)
            for c, digit in zip(cols, row):
                with c:
                    if digit == "":
                        st.write("")
                    else:
                        if st.button(digit, key=f"dial_{digit}_{r}", use_container_width=True):
                            press(digit)

    st.write("")
    with st.container(key="unlockbtn"):
        if st.button("🔓  Unlock", key="dial_unlock", use_container_width=True):
            check_pin()
            st.rerun()


# ------------------------------------------------------------------
# PAGES — each ends with the single Next button, nothing else
# ------------------------------------------------------------------
def page_home():
    progress_dots()
    render_music_toggle()
    typing_animation("Happy Birthday Ayesha Sohail ❤️", speed_ms=75, size_px=28)
    st.markdown(
        "<p style='text-align:center;font-size:17px;color:#c9bfe8;'>10th August — your special day 💖</p>",
        unsafe_allow_html=True,
    )
    animated_background(height=220)
    st.write("")

    def show_intro():
        confetti_burst(height=140)
        st.success("Yayy! Get ready for a day full of love, Apa! 🥳")

    yes_no_section("intro", "Ready to see your birthday surprise? 🎁", show_intro)
    next_button()


def page_wishes():
    progress_dots()
    st.header("💌 Birthday Wishes for You")
    animated_background(height=140, density="light")

    def show_wishes():
        for w in WISHES:
            st.markdown(f"> {w}")
        st.balloons()

    yes_no_section("wishes", "Do you want to read your birthday wishes?", show_wishes)
    next_button()


def page_quotes():
    progress_dots()
    st.header("✨ Quotes About Sisters")
    animated_background(height=140, density="light")

    def show_quotes():
        for q in QUOTES:
            st.markdown(f"🌸 *{q}*")

    yes_no_section("quotes", "Want to see some quotes about sisters?", show_quotes)
    next_button()


def page_prayers():
    progress_dots()
    st.header("🤲 Duas & Prayers")
    floating_petals(height=140)

    def show_prayers():
        for p in PRAYERS:
            st.markdown(f"🕌 {p}")

    yes_no_section("prayers", "Would you like some heartfelt prayers?", show_prayers)
    next_button()


def page_gift():
    progress_dots()
    st.header("🎁 A Gift For You")
    animated_background(height=140, density="light")

    if "gift_opened" not in st.session_state:
        st.session_state.gift_opened = False
    if "letter_shown" not in st.session_state:
        st.session_state.letter_shown = False

    if not st.session_state.gift_opened:
        st.markdown(
            "<div style='text-align:center;font-size:90px;animation:giftShake 1.6s ease-in-out infinite;'>"
            "🎁</div>"
            "<style>@keyframes giftShake{0%,100%{transform:rotate(0deg);}"
            "20%{transform:rotate(-8deg);}40%{transform:rotate(8deg);}"
            "60%{transform:rotate(-5deg);}80%{transform:rotate(5deg);}}</style>",
            unsafe_allow_html=True,
        )
        if st.button("🎀 Open Your Gift", use_container_width=True):
            st.session_state.gift_opened = True
            play_happy_chime()
            st.rerun()
    else:
        confetti_burst(height=160)
        st.markdown(
            """
            <div class="glow-card" style="animation:giftGlow 2s ease-in-out infinite alternate;">
            <div style='font-size:56px;'>🎉🎁🎉</div>
            <h3>For Ayesha Sohail 💖</h3>
            <p style='font-size:16px;'>
            Inside this gift is all my love and gratitude for the sister you are.
            Here's to a year as beautiful, kind, and bright as you. Happy Birthday!
            </p>
            </div>
            <style>
            @keyframes giftGlow {
                from { box-shadow: 0 0 15px rgba(255,111,174,0.25); }
                to   { box-shadow: 0 0 35px rgba(255,111,174,0.6); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.letter_shown:
            if st.button("💌 Read a Message From Your Brother", use_container_width=True):
                st.session_state.letter_shown = True
                play_happy_chime()
                st.rerun()
        else:
            letter_paragraphs = "".join(
                f"<p style='margin:6px 0;'>{line}</p>"
                for line in BROTHER_LETTER.strip().split("\n\n")
            )
            st.markdown(
                f"""
                <div style='text-align:left;padding:22px;border-radius:14px;
                background:#1c1436;border:1px solid rgba(255,111,174,0.25);
                box-shadow:0 4px 22px rgba(0,0,0,0.35);
                font-family:Georgia,serif;font-style:italic;color:#ece4ff;
                animation:letterFade 0.8s ease;'>
                <h4 style='font-style:normal;color:#ff9dc9;margin-top:0;'>
                    ✨ A Message From Your Brother</h4>
                {letter_paragraphs}
                </div>
                <style>
                @keyframes letterFade {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to   {{ opacity: 1; transform: translateY(0); }}
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )

    next_button()


def page_cake():
    progress_dots()
    st.header("🎂 Blow Out the Candles")
    animated_background(height=140, density="light")

    if "candles_out" not in st.session_state:
        st.session_state.candles_out = False

    if not st.session_state.candles_out:
        st.markdown(
            """
            <div style='text-align:center;font-size:80px;line-height:1;'>
                <span style='display:inline-block;animation:flicker 0.6s infinite alternate;'>🕯️🕯️🕯️</span>
                <div>🎂</div>
            </div>
            <style>
            @keyframes flicker {
                from { opacity: 1; filter: drop-shadow(0 0 6px #ffd93d); }
                to   { opacity: 0.7; filter: drop-shadow(0 0 14px #ff9f6b); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.caption("The candles are lit — tap below to blow them out! 💨")
        if st.button("🎂 Blow Out the Candles", use_container_width=True):
            st.session_state.candles_out = True
            play_happy_chime()
            st.rerun()
    else:
        confetti_burst(height=160)
        st.markdown(
            "<div style='text-align:center;font-size:80px;'>🎂✨</div>"
            "<p style='text-align:center;font-size:17px;'>Make a wish, Ayesha! 🌟 "
            "May everything you wished for come true. 💕</p>",
            unsafe_allow_html=True,
        )
        st.balloons()

    next_button()


def page_finale():
    progress_dots()
    st.header("🌌 The Grand Finale")
    moon_stars_scene(height=180)

    def show_finale():
        st.markdown(SIGNATURE_HTML, unsafe_allow_html=True)
        st.write("")
        if st.button("🎆 Celebrate!", key="celebrate_btn", use_container_width=True):
            st.session_state.celebrated = True

        if st.session_state.celebrated:
            fireworks_finale(height=280)
            confetti_burst(height=140)
            st.markdown(
                """
                <div class="glow-card" style="animation:fireGlow 1.1s ease-in-out infinite alternate;
                    margin-top:14px;">
                <div style='font-size:52px;'>🎉🔥🎆🔥🎉</div>
                <h1 style='font-size:32px;margin:6px 0;'>Happy Birthday, Ayesha Sohail! ❤️</h1>
                <p style='font-size:17px;'>
                May Allah bless you with happiness, good health, success, barakah,
                and endless joy. Ameen.
                </p>
                </div>
                <style>
                @keyframes fireGlow {
                    from { box-shadow: 0 0 20px rgba(255,140,60,0.35), 0 0 40px rgba(255,111,174,0.25); }
                    to   { box-shadow: 0 0 45px rgba(255,140,60,0.75), 0 0 70px rgba(255,111,174,0.5); }
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.balloons()
            play_happy_chime()
        else:
            st.markdown(
                """
                <div class="glow-card" style="animation:finaleGlow 2.2s ease-in-out infinite alternate;">
                <div style='font-size:44px;'>🌙✨🎈✨🌙</div>
                <h2>Happy Birthday, Ayesha Sohail! ❤️</h2>
                <p style='font-size:17px;'>
                May Allah bless you with happiness, good health, success, barakah,
                and endless joy. Ameen.
                </p>
                </div>
                <style>
                @keyframes finaleGlow {
                    from { box-shadow: 0 0 15px rgba(255,111,174,0.2); }
                    to   { box-shadow: 0 0 40px rgba(255,111,174,0.55); }
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

    yes_no_section("finale", "Ready for your final birthday message? 🎁", show_finale)


PAGES = {
    "home": page_home,
    "wishes": page_wishes,
    "quotes": page_quotes,
    "prayers": page_prayers,
    "gift": page_gift,
    "cake": page_cake,
    "finale": page_finale,
}

# ------------------------------------------------------------------
# APP FLOW — no sidebar, no jump navigation. Lock screen, then a
# strictly linear sequence of pages connected only by "Next".
# ------------------------------------------------------------------
if not st.session_state.unlocked:
    lock_screen()
else:
    PAGES[st.session_state.page]()
