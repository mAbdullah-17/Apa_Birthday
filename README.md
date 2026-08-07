# 🎂 Happy Birthday Website — for Ayesha Sohail

A private, animated Streamlit birthday website with:
- 🔒 4-digit PIN lock screen (code: `2002`)
- 🎵 Soft generated background music with a Play/Pause button (sidebar)
- ⌨️ Typing animation: "Happy Birthday Ayesha Sohail ❤️" on the Home page
- 🎈 Floating animated stickers — balloons, hearts, butterflies, sparkles
- 🌹 Floating rose petals on the Duas & Prayers page
- 🎉 Confetti bursts on Home, Gift Box, Cake, and Finale
- 🎆 Interactive finale — calm moon & stars scene, fireworks only after
  tapping "Celebrate!"
- 🎁 Interactive Gift Box — tap to open with a glowing reveal
- 💌 "A Message From Your Brother" — a heartfelt letter revealed after
  the gift opens
- 📜 Digital signature on the finale: "With love and prayers, —
  Muhammad Abdullah ❤️"
- 🎂 Interactive Cake — lit candles you can tap to blow out, then a
  balloon/confetti celebration
- 🔊 Beep/chime sounds generated on the fly (no audio files needed)
- ✅❌ "Yes / No" interactive choices on every section, with a playful
  scolding beep message if she clicks "No"
- 💌 Wishes, ✨ quotes, 🤲 prayers — plus smooth fade/slide page transitions
  throughout

---

## 1. Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL it prints (usually `http://localhost:8501`).

## 2. Push to GitHub

```bash
cd birthday_site
git init
git add .
git commit -m "Birthday website for Apa 🎂"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## 3. Deploy for free on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app**, pick your repo/branch, and set the main file to `app.py`.
3. Click **Deploy**. You'll get a shareable link — send it to her on August 10th!

## 4. Customize it further

- **Add real photos:** create an `images/` folder next to `app.py`, drop
  photos in it, and reference them with `st.image("images/filename.jpg")`
  inside `page_gallery()` — I used a placeholder uploader since I can't
  generate actual photos of the two of you.
- **Change the PIN:** edit the `PIN = "2002"` line in `app.py`.
- **Add more wishes/quotes/prayers:** just add more strings to the
  `WISHES`, `QUOTES`, and `PRAYERS` lists near the top of `app.py`.
- **Change colors:** search for `#ffe3ec` / `#fff0f6` in `app.py` and swap
  in her favorite colors.

## 5. A few honest technical notes

- **Background music:** Streamlit reruns the whole page on every button
  click, so browsers may briefly restart audio on interaction — the app
  saves playback position so it resumes almost seamlessly rather than
  starting from zero. Autoplay after unlocking may still be blocked by
  some browsers until she taps Play once (standard browser policy).
- **Page transitions:** every page fades/slides in smoothly on load.
- **Gallery photos:** the photo gallery was intentionally removed for
  privacy — no family photos are uploaded to a public server. If you
  want one back later, just ask and I'll re-add it as a private,
  password-gated section.

Happy Birthday to your sister! 🎉
