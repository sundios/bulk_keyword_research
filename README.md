# SEO Keyword Generator (OpenAI + KWRDS)

A Python tool that automates keyword research, traffic estimation, and content ideation using **OpenAI** and **KWRDS.ai** APIs.

Built by [@kburchardt](https://www.linkedin.com/in/konradburchardt/)

<video src="video.mov" width="640" autoplay loop controls muted></video>


---

## 💡 Overview

This tool helps content strategists, SEO teams, and marketers automatically generate topic ideas and estimate traffic potential — perfect for planning new landing pages or blog series.

> At Figma, this workflow helps research briefs for new landing pages by quantifying search volume, potential traffic, and estimated signups before production.

---

## 🧠 How it works

1. **Choose a topic** — e.g. “Netflix”.  
2. **OpenAI** generates up to 50 short-tail, related topic ideas (child pages).  
3. **KWRDS.ai** retrieves live keyword search volumes for each topic.  
4. The script merges everything into a single Excel workbook (`seo_keywords.xlsx`) with:
   - One **Index sheet** summarizing volumes and potential traffic.
   - One sheet per child topic with raw keyword data.

You can also manually add extra topics to include in the analysis.

If you prefer a no-code interface, the same logic is available via the **[KWRDS Topic Research tool](https://www.kwrds.ai/topic-research)**.

---

## 🚀 How to run it

### Requirements

- **Python 3.10+**
- **OpenAI API key** ([get one here](https://platform.openai.com))
- **KWRDS.ai API key** ([get one here](https://www.kwrds.ai/api))

### Installation

```bash
git clone https://github.com/your-org/seo-keyword-generator.git
cd seo-keyword-generator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Replace placeholder keys in the script with your own:

```python
client = OpenAI(api_key="##ADD-YOUR-KEY-HERE###")
```

and inside `get_keywords()`:

```python
url = "https://keywordresearch.api.kwrds.ai/keywords-with-volumes"
headers = { "X-API-KEY": "##ADD-YOUR-KEY-HERE###" }
```

---

### Run the script

```bash
python seo_keywords.py
```

You’ll be prompted for:
- Main topic (e.g. `Netflix`)
- Max number of child pages (1–50)
- Any additional pages to include (comma-separated)

Once complete, the script will:
- Fetch live keyword volumes from KWRDS.ai
- Estimate potential traffic (10%) and signups (4%)
- Save everything to `seo_keywords.xlsx`

---

## 📊 Example output

**Index Sheet Columns:**
- `Page type` — Page/topic name
- `Search volume` — Total keyword volume for that topic
- `Potential traffic (10%)`
- `Est signups (4%)`

**Per-topic Sheets:** contain raw keyword and volume data for each page.

---

## 🧩 Behind the scenes

```text
main() → gpt() → merge_pages() → progress_fetch_keywords(get_keywords)
   │          │               │                    └─► KWRDS.ai API
   │          └─► OpenAI      └─► Deduplicate + Cap
   └─► Build index + Export → Excel via XlsxWriter
```

- **Rich console UI** — Animated progress bars, tables, and summaries.
- **Excel export** — One file with all results, easy to share.

---

## 🔗 Related resources

- 🔑 Get your **KWRDS.ai API key:** [https://www.kwrds.ai/api](https://www.kwrds.ai/api)
- 💻 Try the **Live UI version:** [https://www.kwrds.ai/topic-research](https://www.kwrds.ai/topic-research)
- 🧰 OpenAI documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)


---

## 🧾 License

MIT — free to use, modify, and share.

