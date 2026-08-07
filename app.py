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
    page_title="Happy Birthday Apa 🎂",
    page_icon="🎉",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# GLOBAL CSS — page transitions + responsive tweaks
# (injected once; does not change existing colors/fonts/layout)
# ------------------------------------------------------------------
def inject_global_css():
    st.markdown(
        """
        <style>
        /* Smooth fade + slide whenever a page re-renders */
        [data-testid="stAppViewContainer"] .main .block-container {
            animation: pageFadeSlide 0.55s ease;
        }
        @keyframes pageFadeSlide {
            0%   { opacity: 0; transform: translateY(18px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        /* Buttons feel a touch springier without changing their look */
        div.stButton > button {
            transition: transform 0.15s ease;
        }
        div.stButton > button:active {
            transform: scale(0.96);
        }
        @media (max-width: 640px) {
            .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_global_css()

# ------------------------------------------------------------------
# BEEP SOUND GENERATOR (no external files needed)
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
        f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        height=0,
        width=0,
    )


def play_happy_chime():
    # a quick little rising chime for "yes" moments
    data1 = make_beep(659, 0.12, 0.4)
    data2 = make_beep(784, 0.12, 0.4)
    data3 = make_beep(988, 0.18, 0.4)
    combined = data1[44:] + data2[44:] + data3[44:]
    header = data1[:44]
    b64 = base64.b64encode(header + combined).decode()
    components.html(
        f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        height=0,
        width=0,
    )


# ------------------------------------------------------------------
# BACKGROUND MUSIC (soft, generated melody — no external file needed)
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def make_background_music():
    """A soft looping lullaby-like melody built from sine tones."""
    sample_rate = 22050
    # simple gentle chord progression (C major - A minor - F - G) melody notes
    melody = [523, 587, 659, 587, 523, 494, 440, 494,
              523, 659, 784, 659, 587, 523, 494, 440]
    note_dur = 0.45
    audio = np.array([], dtype=np.float32)
    for i, freq in enumerate(melody):
        t = np.linspace(0, note_dur, int(sample_rate * note_dur), False)
        # soft sine with gentle fade in/out (envelope) for a mellow tone
        envelope = np.sin(np.pi * t / note_dur)
        tone = np.sin(freq * t * 2 * np.pi) * envelope
        # add a soft harmonic for warmth
        tone += 0.3 * np.sin(freq * 2 * t * 2 * np.pi) * envelope
        audio = np.concatenate([audio, tone])
    audio = audio / np.max(np.abs(audio))
    pcm = (audio * 0.28 * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return base64.b64encode(buf.getvalue()).decode()


def render_background_music_player():
    """Play/Pause control. Music starts only after user presses Play
    (or right after unlocking, per the browser's autoplay rules)."""
    if "music_on" not in st.session_state:
        st.session_state.music_on = False

    b64 = make_background_music()
    label = "⏸️ Pause Music" if st.session_state.music_on else "🎵 Play Birthday Music"
    if st.button(label, key="music_toggle", use_container_width=True):
        st.session_state.music_on = not st.session_state.music_on

    if st.session_state.music_on:
        components.html(
            f"""
            <audio id="bgm" autoplay loop>
                <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            <script>
                const bgm = document.getElementById('bgm');
                bgm.volume = 0.35;
                const saved = localStorage.getItem('bgm_time');
                if (saved) {{ try {{ bgm.currentTime = parseFloat(saved); }} catch(e) {{}} }}
                setInterval(() => {{
                    if (!bgm.paused) localStorage.setItem('bgm_time', bgm.currentTime);
                }}, 1000);
            </script>
            """,
            height=0,
            width=0,
        )


# ------------------------------------------------------------------
# TYPING TEXT ANIMATION
# ------------------------------------------------------------------
def typing_animation(text, speed_ms=80, size_px=32, height=90):
    safe_text = text.replace("'", "\\'")
    components.html(
        f"""
        <div style="text-align:center;font-family:'Trebuchet MS',sans-serif;
                    font-weight:800;font-size:{size_px}px;color:#d6336c;
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
# STICKER / ANIMATION BACKGROUND (pure CSS, no external images)
# ------------------------------------------------------------------
def animated_background(height=260, density="normal"):
    stickers = ["🎈", "🎉", "✨", "💖", "🎂", "🌸", "🎁", "🦋", "⭐", "💫", "🩷"]
    count = 18 if density == "normal" else 28
    items = ""
    for i in range(count):
        emoji = random.choice(stickers)
        left = random.randint(0, 96)
        delay = round(random.uniform(0, 6), 2)
        duration = round(random.uniform(6, 12), 2)
        size = random.randint(20, 40)
        items += f"""
        <div class="sticker" style="
            left:{left}%;
            font-size:{size}px;
            animation-delay:{delay}s;
            animation-duration:{duration}s;
        ">{emoji}</div>
        """

    html = f"""
    <div class="sticker-field">
        {items}
    </div>
    <style>
        .sticker-field {{
            position: relative;
            width: 100%;
            height: {height}px;
            overflow: hidden;
            background: linear-gradient(180deg, #fff0f6 0%, #ffe3ec 100%);
            border-radius: 18px;
        }}
        .sticker {{
            position: absolute;
            bottom: -50px;
            animation-name: floatUp;
            animation-timing-function: ease-in-out;
            animation-iteration-count: infinite;
            opacity: 0.9;
        }}
        @keyframes floatUp {{
            0%   {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
            10%  {{ opacity: 1; }}
            50%  {{ transform: translateY(-140px) rotate(15deg); }}
            100% {{ transform: translateY(-280px) rotate(-10deg); opacity: 0; }}
        }}
    </style>
    """
    components.html(html, height=height + 10)


def confetti_burst(height=220, duration_ms=4000):
    components.html(
        f"""
        <canvas id="confetti-canvas" style="width:100%;height:{height}px;display:block;"></canvas>
        <script>
        const canvas = document.getElementById('confetti-canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = {height};
        const colors = ['#ff6b9d','#ffd93d','#6bcBff','#a06bff','#6bffb0','#ff9f6b'];
        let pieces = [];
        for (let i=0;i<140;i++){{
            pieces.push({{
                x: Math.random()*canvas.width,
                y: Math.random()*-canvas.height,
                r: Math.random()*6+4,
                c: colors[Math.floor(Math.random()*colors.length)],
                spX: Math.random()*2-1,
                spY: Math.random()*3+2,
                rot: Math.random()*360
            }});
        }}
        let start = null;
        function draw(ts){{
            if(!start) start = ts;
            ctx.clearRect(0,0,canvas.width,canvas.height);
            pieces.forEach(p=>{{
                p.x += p.spX; p.y += p.spY; p.rot += 4;
                if(p.y>canvas.height){{ p.y = -10; p.x = Math.random()*canvas.width; }}
                ctx.save();
                ctx.translate(p.x,p.y);
                ctx.rotate(p.rot*Math.PI/180);
                ctx.fillStyle = p.c;
                ctx.fillRect(-p.r/2,-p.r/2,p.r,p.r*0.6);
                ctx.restore();
            }});
            if (ts - start < {duration_ms}) requestAnimationFrame(draw);
        }}
        requestAnimationFrame(draw);
        </script>
        """,
        height=height + 10,
    )


def fireworks_finale(height=320):
    """Fireworks + rising balloons + glowing particles for the grand finale."""
    components.html(
        f"""
        <canvas id="fw-canvas" style="width:100%;height:{height}px;display:block;
            background:linear-gradient(180deg,#2b0a3d 0%,#5b1a52 60%,#ffe3ec 100%);
            border-radius:18px;"></canvas>
        <script>
        const canvas = document.getElementById('fw-canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = {height};
        const colors = ['#ff6b9d','#ffd93d','#6bd4ff','#c08bff','#6bffb0','#ff9f6b','#ffffff'];

        class Firework {{
            constructor() {{
                this.x = Math.random()*canvas.width;
                this.y = canvas.height;
                this.targetY = Math.random()*canvas.height*0.45 + 20;
                this.speed = 4 + Math.random()*2;
                this.exploded = false;
                this.particles = [];
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
                            this.particles.push({{
                                x:this.x, y:this.y,
                                vx:Math.cos(angle)*speed,
                                vy:Math.sin(angle)*speed,
                                life:60,
                                color: colors[Math.floor(Math.random()*colors.length)]
                            }});
                        }}
                    }}
                }} else {{
                    this.particles.forEach(p=>{{
                        p.x += p.vx; p.y += p.vy; p.vy += 0.03; p.life -= 1;
                    }});
                    this.particles = this.particles.filter(p=>p.life>0);
                }}
            }}
            draw() {{
                if (!this.exploded) {{
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, 2.5, 0, Math.PI*2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                }} else {{
                    this.particles.forEach(p=>{{
                        ctx.beginPath();
                        ctx.globalAlpha = Math.max(p.life/60, 0);
                        ctx.arc(p.x, p.y, 2, 0, Math.PI*2);
                        ctx.fillStyle = p.color;
                        ctx.fill();
                        ctx.globalAlpha = 1;
                    }});
                }}
            }}
            isDone() {{ return this.exploded && this.particles.length === 0; }}
        }}

        let fireworks = [];
        let frame = 0;
        function loop() {{
            ctx.fillStyle = 'rgba(20,5,30,0.15)';
            ctx.fillRect(0,0,canvas.width,canvas.height);
            if (frame % 35 === 0) fireworks.push(new Firework());
            fireworks.forEach(f=>{{ f.update(); f.draw(); }});
            fireworks = fireworks.filter(f=>!f.isDone());
            frame++;
            requestAnimationFrame(loop);
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
        border-top:1px solid rgba(214,51,108,0.35);'>
    <p style='font-style:italic;font-size:16px;color:#d6336c;'>
        With love and prayers,<br>
        <span style='font-size:18px;font-weight:700;'>— Muhammad Abdullah ❤️</span>
    </p>
</div>
"""


# ------------------------------------------------------------------
# ROSE PETALS (for the Duas & Prayers page)
# ------------------------------------------------------------------
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
        <div class="petal" style="
            left:{left}%;
            font-size:{size}px;
            animation-delay:{delay}s;
            animation-duration:{duration}s;
        ">{emoji}</div>
        """
    components.html(
        f"""
        <div class="petal-field">{items}</div>
        <style>
            .petal-field {{
                position: relative; width: 100%; height: {height}px;
                overflow: hidden;
                background: linear-gradient(180deg, #fff7e6 0%, #ffeede 100%);
                border-radius: 18px;
            }}
            .petal {{
                position: absolute; top: -40px;
                animation-name: petalFall;
                animation-timing-function: ease-in-out;
                animation-iteration-count: infinite;
                opacity: 0.9;
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


# ------------------------------------------------------------------
# MOON & STARS NIGHT SCENE (calm finale backdrop, before Celebrate)
# ------------------------------------------------------------------
def moon_stars_scene(height=220):
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
        <div class="night-sky">
            {stars}
            <div class="moon"></div>
        </div>
        <style>
            .night-sky {{
                position: relative; width: 100%; height: {height}px;
                overflow: hidden; border-radius: 18px;
                background: linear-gradient(180deg, #241b4e 0%, #4a2b6b 55%, #a35a8f 100%);
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
            @keyframes twinkle {{
                0%, 100% {{ opacity: 0.25; }}
                50% {{ opacity: 1; }}
            }}
        </style>
        """,
        height=height + 10,
    )


def yes_no_section(key, question, on_yes):
    st.markdown(f"#### {question}")
    c1, c2 = st.columns(2)
    yes_key = f"{key}_yes"
    no_key = f"{key}_no"
    if c1.button("✅ Yes", key=yes_key, use_container_width=True):
        play_happy_chime()
        on_yes()
    if c2.button("❌ No", key=no_key, use_container_width=True):
        play_beep(300, 0.3, 0.5)
        st.warning(random.choice(NO_BEEP_MESSAGES))


# ------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

PIN = "2002"

# ------------------------------------------------------------------
# LOCK SCREEN
# ------------------------------------------------------------------
def lock_screen():
    st.markdown(
        "<h1 style='text-align:center;'>🔒 A Secret Surprise Awaits...</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;'>Enter the 4-digit code to unlock your birthday surprise 🎂</p>",
        unsafe_allow_html=True,
    )
    animated_background(height=160)
    entered = st.text_input(
        "Enter PIN", type="password", max_chars=4, label_visibility="collapsed",
        placeholder="••••",
    )
    if st.button("Unlock 🔓", use_container_width=True):
        if entered == PIN:
            play_happy_chime()
            st.session_state.unlocked = True
            st.rerun()
        else:
            play_beep(220, 0.3, 0.5)
            st.error("Wrong code! Hint: think of a special year 😉")


# ------------------------------------------------------------------
# PAGES
# ------------------------------------------------------------------
def page_home():
    typing_animation("Happy Birthday Ayesha Sohail ❤️", speed_ms=75, size_px=30)
    st.markdown(
        "<p style='text-align:center;font-size:18px;'>10th August — your special day 💖</p>",
        unsafe_allow_html=True,
    )
    animated_background(height=240)
    st.write("")

    def show_intro():
        confetti_burst()
        st.success("Yayy! Get ready for a day full of love, Apa! 🥳")

    yes_no_section("intro", "Ready to see your birthday surprise? 🎁", show_intro)


def page_wishes():
    st.header("💌 Birthday Wishes for You")
    animated_background(height=140, density="light")

    def show_wishes():
        for w in WISHES:
            st.markdown(f"> {w}")
        st.balloons()

    yes_no_section("wishes", "Do you want to read your birthday wishes?", show_wishes)


def page_quotes():
    st.header("✨ Quotes About Sisters")
    animated_background(height=140, density="light")

    def show_quotes():
        for q in QUOTES:
            st.markdown(f"🌸 *{q}*")

    yes_no_section("quotes", "Want to see some quotes about sisters?", show_quotes)


def page_prayers():
    st.header("🤲 Duas & Prayers")
    floating_petals(height=140)

    def show_prayers():
        for p in PRAYERS:
            st.markdown(f"🕌 {p}")

    yes_no_section("prayers", "Would you like some heartfelt prayers?", show_prayers)


def page_gift_box():
    st.header("🎁 A Gift For You")
    animated_background(height=140, density="light")

    if "gift_opened" not in st.session_state:
        st.session_state.gift_opened = False

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
        confetti_burst(height=180)
        st.markdown(
            """
            <div style='text-align:center;padding:22px;border-radius:18px;
            background:linear-gradient(135deg,#fff0f6,#ffe3ec);
            box-shadow:0 0 25px rgba(255,105,180,0.55);
            animation:giftGlow 2s ease-in-out infinite alternate;'>
            <div style='font-size:60px;'>🎉🎁🎉</div>
            <h3>For Ayesha Sohail 💖</h3>
            <p style='font-size:16px;'>
            Inside this gift is all my love and gratitude for the sister you are.
            Here's to a year as beautiful, kind, and bright as you. Happy Birthday!
            </p>
            </div>
            <style>
            @keyframes giftGlow {
                from { box-shadow: 0 0 15px rgba(255,105,180,0.35); }
                to   { box-shadow: 0 0 35px rgba(255,105,180,0.75); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if "letter_shown" not in st.session_state:
            st.session_state.letter_shown = False

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
                background:#fffaf3;border:1px solid rgba(214,51,108,0.15);
                box-shadow:0 4px 18px rgba(0,0,0,0.08);
                font-family:Georgia,serif;font-style:italic;color:#5a3d3d;
                animation:letterFade 0.8s ease;'>
                <h4 style='font-style:normal;color:#d6336c;margin-top:0;'>
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

        if st.button("🔁 Wrap it up again", key="gift_reset"):
            st.session_state.gift_opened = False
            st.session_state.letter_shown = False
            st.rerun()


def page_cake():
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
        st.caption("The candles are lit — tap the cake below to blow them out! 💨")
        if st.button("🎂 Blow Out the Candles", use_container_width=True):
            st.session_state.candles_out = True
            play_happy_chime()
            st.rerun()
    else:
        confetti_burst(height=180)
        st.markdown(
            "<div style='text-align:center;font-size:80px;'>🎂✨</div>"
            "<p style='text-align:center;font-size:17px;'>Make a wish, Ayesha! 🌟 "
            "May everything you wished for come true. 💕</p>",
            unsafe_allow_html=True,
        )
        st.balloons()
        if st.button("🔁 Relight the candles", key="cake_reset"):
            st.session_state.candles_out = False
            st.rerun()


def page_finale():
    st.header("🌌 The Grand Finale")
    moon_stars_scene(height=200)

    def show_finale():
        st.markdown(
            """
            <div style='text-align:center;padding:24px;border-radius:18px;
            background:linear-gradient(135deg,#ffe3ec,#fff0f6);
            box-shadow:0 0 30px rgba(255,105,180,0.45);
            animation:finaleGlow 2.2s ease-in-out infinite alternate;'>
            <div style='font-size:46px;'>🌙✨🎈✨🌙</div>
            <h2>Happy Birthday, Ayesha Sohail! ❤️</h2>
            <p style='font-size:17px;'>
            May Allah bless you with happiness, good health, success, barakah,
            and endless joy. Ameen.
            </p>
            </div>
            <style>
            @keyframes finaleGlow {
                from { box-shadow: 0 0 15px rgba(255,105,180,0.3); }
                to   { box-shadow: 0 0 40px rgba(255,105,180,0.8); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(SIGNATURE_HTML, unsafe_allow_html=True)

        st.write("")
        if st.button("🎆 Celebrate!", key="celebrate_btn", use_container_width=True):
            st.session_state.celebrated = True

        if st.session_state.get("celebrated"):
            fireworks_finale(height=300)
            confetti_burst(height=160)
            st.balloons()
            play_happy_chime()

    yes_no_section("finale", "Ready for your final birthday message? 🎁", show_finale)


PAGES = {
    "🏠 Home": page_home,
    "💌 Wishes": page_wishes,
    "✨ Quotes": page_quotes,
    "🤲 Prayers": page_prayers,
    "🎁 Gift Box": page_gift_box,
    "🎂 Birthday Cake": page_cake,
    "🌌 Finale": page_finale,
}

# ------------------------------------------------------------------
# APP FLOW
# ------------------------------------------------------------------
if not st.session_state.unlocked:
    lock_screen()
else:
    st.sidebar.title("🎀 Navigate")
    render_background_music_player()
    st.sidebar.markdown("---")
    choice = st.sidebar.radio("Go to:", list(PAGES.keys()))
    PAGES[choice]()
    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 Lock again"):
        st.session_state.unlocked = False
        st.rerun()
