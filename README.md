# Conda Support Knowledge-Based System (CSKBS)

A small rule-based Knowledge Base System to assist with daily Conda workflow questions and simple diagnostic guidance. It extracts intent/keywords from natural language queries, applies inference rules, and shows actionable recommendations using Rich formatting.

## Features
- NLP entity and intent extraction (spaCy + keyword fallback)
- Rule-based inference (environment setup, export, install, cleanup, dependency issues)
- Fallback general advice lookup when no rule fires
- Rich terminal UI (panels, markdown rendering)
- Portable domain knowledge (can be moved to JSON later)

## Project Structure
```
conda_kbs_gen.py      # Main KBS (rules, NLP, inference, UI loop)
README.md             # Documentation
data/knowledge_base.json (optional future externalization)
```

## Components
1. Domain Knowledge
   - KNOWLEDGE['advice'] (text guidance)
   - KNOWLEDGE['command'] (command templates)
2. RULES
   - Each rule: id, conditions[], conclusion
3. NLPProcessor
   - spaCy model for ROOT verb + noun chunk hints
   - Keyword fallback for domain entities
4. InferenceEngine
   - Evaluates rule conditions (eq, exists, in, contains)
5. KnowledgeBaseQuery
   - Supplies general advice when no conclusions triggered
6. Presenter
   - Renders entities, recommendations, and fallback advice

## Example Queries
- "I am starting a new project. What should I do?"
- "I need to install a package but I am still in base."
- "How do I export my environment cross platform?"
- "Dependency conflict during install."
- "Disk full. Need cleanup."

## Installation
```bash
git clone <repo>
cd knowledge-base-system
python -m venv .venv
source .venv/bin/activate
pip install spacy rich
python -m spacy download en_core_web_sm
```

## Run
```bash
python conda_kbs_gen.py
```

## Rule Logic (Sample)
| Rule ID | Fires When | Conclusion Purpose |
|---------|------------|--------------------|
| conda_new_project_sequence | new_project=True | Guide to create and name environment |
| conda_install_requires_activation | install_package=True + active_env_check=False | Remind to activate before install |
| conda_install_specific_env | install_package=True + target_specific_env=True | Show scoped install pattern |
| conda_export_portable | export_env=True + cross_platform=True | Advise history-based export |
| conda_export_detailed | export_env=True + full_detail=True | Produce explicit export command |
| conda_dependency_error | dependency_error=True | Suggest revision listing |
| conda_system_cleanup | cleanup_needed=True | Show cleanup command |

## Adding a Rule
Edit RULES list:
```python
RULES.append({
  "id": "conda_update_base",
  "conditions": [{"attribute": "update_base", "op": "eq", "value": True}],
  "conclusion": "Update base environment: `conda update --name base conda`"
})
```

## Extending
- Externalize KNOWLEDGE and RULES to JSON for portable edits
- Add working memory (session-based dynamic facts)
- Add confidence scoring per rule
- Implement spaCy Matcher patterns for more precise entities
- Add environment-specific diagnostics (PATH, versions)

## Limitations
- No persistent state across sessions
- Intent = ROOT lemma is simplistic
- Entities rely on substring lists
- Not all Conda error scenarios covered yet

## Troubleshooting
- Markdown in conclusions must use `Markdown()` (Rich) not `Text.from_markup`
- If spaCy model load fails, system falls back to blank English (reduced parsing)
- Ensure terminal supports ANSI colors for Rich output

## License
Internal / educational use.
