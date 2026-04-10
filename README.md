# 🤖 Google Form Auto-Filler — Indian Persona Mode

Automatically fills Google Forms using realistic Indian identities.
Built with **Playwright** for reliable, modern web automation.

---

## ⚙️ Setup (One-Time)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (Chromium)
python -m playwright install chromium
```

---

## 🚀 Usage

```bash
# Fill form once (browser visible)
python form_filler.py --url "https://forms.gle/YOUR_FORM_ID"

# Fill 5 times
python form_filler.py --url "https://forms.gle/YOUR_FORM_ID" --count 5

# Run silently (no browser window)
python form_filler.py --url "https://forms.gle/YOUR_FORM_ID" --count 10 --headless

# Slow down typing (more human-like)
python form_filler.py --url "https://forms.gle/YOUR_FORM_ID" --count 3 --delay 1.5

# Custom gap between submissions
python form_filler.py --url "https://forms.gle/YOUR_FORM_ID" --count 5 --gap 5
```

---

## 🎛️ All Options

| Flag        | Default | Description                                  |
|-------------|---------|----------------------------------------------|
| `--url`     | —       | Google Form URL (required)                   |
| `--count`   | 1       | Number of submissions                        |
| `--headless`| False   | Hide the browser window                      |
| `--delay`   | 0.5     | Typing speed multiplier (higher = slower)    |
| `--gap`     | 3.0     | Seconds between submissions                  |

---

## 🧠 Smart Field Detection

The bot detects question labels and fills contextually appropriate answers:

| Question contains   | Fills with                          |
|---------------------|-------------------------------------|
| name                | Random Indian full name             |
| email               | Realistic Indian email              |
| phone / mobile      | Valid Indian mobile (6–9 prefix)    |
| city / location     | Indian city                         |
| state               | Indian state                        |
| age                 | Random integer 18–45                |
| college / university| IIT / NIT / VIT etc.                |
| company             | TCS / Infosys / Flipkart etc.       |
| feedback / comment  | Natural-sounding paragraph          |
| rating / score      | Biased toward 7–10 (positive)       |
| date                | Random valid date                   |
| gender              | Matched to generated persona        |

Radio, checkbox, dropdown, scale, date, and text fields are all handled automatically.

---

## 📝 Notes

- Works best with standard Google Forms
- Multi-page forms are supported (Next button is clicked automatically)
- Each submission uses a fresh, unique Indian persona
- Typing is randomized to mimic human behavior

---

*For educational and fun purposes only.*
