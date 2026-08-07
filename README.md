# 🌙 Happy Birthday Website — for Ayesha Sohail

A private, dark-themed, single-flow birthday website. No sidebar, no
jump-around navigation — just a phone-style lock screen followed by one
page leading directly into the next.

## What's inside

- 📱 **Phone-style dial pad lock screen** — tap digits like unlocking a
  phone, code: `2002`
- ➡️ **Linear flow only** — every page ends in one "Next ➜" button that
  takes her straight to the next moment. A small row of glowing dots at
  the top shows progress (not clickable — just a visual cue, not a nav bar)
- 🌌 **Dark, glowing theme** throughout — deep navy/purple gradients,
  pink glow accents, glassmorphic cards (set via `.streamlit/config.toml`)
- 🎙️ **Nasheed-style background music** — a wordless vocal-style
  chant + daf/hand-drum percussion (no melodic instruments), Play/Pause
  toggle. You can also upload your own nasheed mp3/wav to use instead
  (see note below).
- ⌨️ Typing animation: "Happy Birthday Ayesha Sohail ❤️"
- 🎈 Floating balloons/hearts/sparkles, 🌹 rose petals on the Duas page
- 🎁 Interactive Gift Box → reveals a glowing message → "A Message From
  Your Brother" letter
- 🎂 Interactive Cake — lit candles, tap to blow out, confetti celebration
- 🌙 Moon & stars calm finale scene → tap **Celebrate!** to trigger fireworks
- 📜 Signature: *"With love and prayers, — Muhammad Abdullah ❤️"*
- ✅❌ Yes/No prompts on each page, with a playful beep if she taps "No"

## Flow (fixed order, no way to skip around)

Lock 🔒 → Home 🎉 → Wishes 💌 → Quotes ✨ → Duas 🤲 → Gift 🎁 →
Cake 🎂 → Finale 🌌

---

## 1. Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The `.streamlit/config.toml` file sets the dark theme automatically —
keep it in the same folder as `app.py`.

## 2. Push to GitHub

```bash
cd birthday_site
git init
git add .
git commit -m "Birthday website for Ayesha — dark themed, linear flow"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## 3. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. **New app** → pick your repo/branch → main file `app.py` → **Deploy**.
3. You'll get a shareable link — send it to her on August 10th!

## 4. Customize further

- **Change the PIN:** edit `PIN = "2002"` near the top of `app.py`.
- **Reorder or add a page:** edit the `PAGE_ORDER` list and the `PAGES`
  dict at the bottom of `app.py` — the flow follows that order automatically.
- **Tweak the dark palette:** colors mainly live in `inject_global_css()`
  and `.streamlit/config.toml`.
- **Add more wishes/quotes/prayers:** extend the `WISHES`, `QUOTES`, and
  `PRAYERS` lists.

## A few honest technical notes

- Streamlit reruns the whole script on every click, so background music
  may briefly restart on interaction — it resumes from its last saved
  position rather than from zero.
- Some browsers block audio autoplay until she's tapped something once
  on the page — that's a browser policy, not a bug.
- No gallery/photo upload is included, by design, since this will be
  hosted on a public link.
- **About the "nasheed" music:** I can't legally embed a real,
  copyrighted nasheed recording, and I can't generate authentic sung
  vocals — so the built-in track is a synthesized approximation (a
  wordless vocal-style chant plus daf/hand-drum percussion, deliberately
  with no melodic instruments, in the spirit of traditional nasheed). If
  you have a royalty-free nasheed file, use the "Use your own nasheed
  file" uploader on the Home page and it'll play instead automatically.

Happy Birthday to your sister! 🎉
