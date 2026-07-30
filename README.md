<div align="center">

# 🔬 Research Paper & Code Analysis Agent

**An AI-powered agent that reads, analyses, and cross-references your research papers with their implementation code — all from a single folder.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![AgentRouter](https://img.shields.io/badge/Powered%20by-AgentRouter-6c47ff)](https://agentrouter.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ What It Does

Point the agent at any folder containing a research paper and its code — it will:

1. **📄 Analyse the paper** — summary, key contributions, methodology, datasets, results & limitations
2. **💻 Analyse the code** — architecture, algorithm implementation, code quality, potential bugs
3. **🔗 Cross-analyse** — checks whether the code actually matches the paper's claims and gives a **Reproducibility Score**
4. **💬 Interactive Q&A** — ask follow-up questions about the paper or code in a chat interface
5. **📝 Save a report** — generates `research_analysis_report.md` inside your folder

---

## 🗂️ Supported File Types

| Category | Formats |
|---|---|
| Research Papers | `.pdf`, `.docx`, `.md`, `.txt` |
| Code | `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.go`, `.rs`, `.r` |
| Notebooks | `.ipynb` |
| Config / Scripts | `.yaml`, `.yml`, `.toml`, `.json`, `.sh` |

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/chandankumarcp/Agent.git
cd Agent
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
```

Open `.env` and set your [AgentRouter](https://agentrouter.org) API key:

```env
AGENTROUTER_API_KEY=your_api_key_here
AGENTROUTER_BASE_URL=https://agentrouter.org
AGENTROUTER_MODEL=gpt-5.6-sol
```

### 3. Run

```bash
# Analyse a folder
python agent.py /path/to/your/research/folder

# Pass the API key directly (no .env needed)
python agent.py /path/to/folder --api-key YOUR_KEY

# Pick a specific model
python agent.py /path/to/folder --model claude-3-5-sonnet

# Analysis + interactive Q&A chat afterwards
python agent.py /path/to/folder --interactive
```

---

## 📁 Expected Folder Structure

```
my_research/
├── paper.pdf          ← research paper
├── main.py            ← implementation
├── model.py
├── train.ipynb        ← Jupyter notebooks work too
├── utils.py
└── README.md
```

---

## 📊 Output Example

```
============================================================
  Research Analysis Agent
  Folder: /home/user/my_research
============================================================

Found 1 paper(s) and 4 code file(s).

[*] Analysing paper: paper.pdf
[*] Analysing 4 code file(s)...
[*] Running cross-analysis (paper ↔ code alignment)...

── PAPER ANALYSIS ──────────────────────────────────────────
1. Summary ...
2. Key Contributions ...
...

── CODE ANALYSIS ───────────────────────────────────────────
1. Architecture Overview ...
...

── CROSS-ANALYSIS ──────────────────────────────────────────
Reproducibility Score: 8/10
...

Report saved to: /home/user/my_research/research_analysis_report.md
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `AGENTROUTER_API_KEY` | Your AgentRouter API key | *(required)* |
| `AGENTROUTER_BASE_URL` | API base URL | `https://agentrouter.org` |
| `AGENTROUTER_MODEL` | Model to route to | `gpt-5.6-sol` |

---

## 🛠️ CLI Reference

```
usage: agent.py [-h] [--interactive] [--api-key API_KEY] [--model MODEL] folder

positional arguments:
  folder                Path to folder containing your research paper and code

options:
  -h, --help            Show this help message and exit
  --interactive, -i     Enter Q&A chat mode after analysis
  --api-key, -k KEY     AgentRouter API key (overrides .env)
  --model, -m MODEL     Model to use via AgentRouter
```

---

## 📦 Project Structure

```
Agent/
├── agent.py          ← Main agent (analysis + Q&A orchestration)
├── readers.py        ← File readers (PDF, DOCX, notebooks, code)
├── requirements.txt  ← Python dependencies
├── .env.example      ← Environment variable template
└── README.md
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

<div align="center">
Built with ❤️ using <a href="https://agentrouter.org">AgentRouter</a>
</div>
