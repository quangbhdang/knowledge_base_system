# Conda Support Knowledge-Based System (CSKBS)

A small, rule-based Knowledge Base System that answers common Conda/Miniconda/Anaconda workflow questions. It extracts a simple intent and entities from natural language and applies inference rules to produce actionable guidance in the terminal using Rich formatting.

## Requirements

- Linux or macOS terminal (For Window please use WSL 2)
- Python 3.11+
- pip and virtualenv/venv
- Internet access (one-time) to download the spaCy English model

## Quick Start (Linux/macOS)

```bash
# 1) Clone the repo
git clone <repo>
cd knowledge-base-system

# 2) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
pip install -U pip wheel
pip install spacy rich

# 4) Download the spaCy English model (recommended)
python -m spacy download en_core_web_sm

# 5) Run the program
python 3676330_kbs.py
```

Notes:
- If the spaCy model is not available, the app falls back to a lightweight tokenizer (reduced NLP accuracy).
- To exit the app, type `quit` or `exit`. Type `help` or `examples` to see sample queries.

## Usage

Type a question about Conda, for example:
- "I am starting a new project, how should I begin?"
- "I need to install a package but I am in the base environment."
- "How do I install packages in a specific environment?"
- "I need to export my environment so it is cross platform compatible."
- "I am getting dependency conflicts during installation."
- "My disk is full, I need to clean up my conda cache."

The app will print a structured interpretation of your query and a recommended action or fallback advice.

## Project Structure

```
3676330_kbs.py   # Main KBS (rules, NLP, inference, UI loop)
README.md        # Documentation
```

## Dependencies

- spaCy (NLP parsing; intent/entity hints)
- Rich (terminal formatting)
- Standard library: re, random

Install with:
```bash
pip install spacy rich
python -m spacy download en_core_web_sm
```

## Components

- KnowledgeBase
  - Stores domain knowledge (fact strings) and rule list.
- InferenceEngine
  - Forward-chaining matcher over rules; returns matching conclusions.
- NLPProcessor
  - Extracts a simple intent (root verb + synonyms) and entity flags (e.g., environment, package, channel, version).
- KnowledgeBaseQuery
  - Fallback: returns general advice when no rule fires.
- CLI/Presenter
  - Rich-based terminal UI with examples and formatted answers.

## Rule Logic (Summary)

- Each rule has conditions (ANDed) and a conclusion (advice/command).
- A condition may include:
  - intent guard (e.g., intent = "install")
  - attribute equality (e.g., attribute "package" == True)
  - attribute presence (value omitted or None implies existence check)
- The engine collects all matching conclusions; the first is shown to the user.

## Troubleshooting

- If the terminal shows no colors/formatting, ensure ANSI colors are supported.
- If spaCy model download fails, re-run:
  ```bash
  python -m spacy download en_core_web_sm
  ```
- If you see import errors, verify the venv is active and dependencies are installed.

## License

Internal / educational use.
