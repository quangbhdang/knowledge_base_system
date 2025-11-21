#----------------------------------------------------------------------
# A submission for IDM course assignment 1: KBS 
# by Quang Ba Hai Dang, student ID: s3676330
#-----------------------------------------------------------------------

import spacy  # Natural Language Processing library
import re
import random
from rich.markdown import Markdown
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# -----------------------------
# KNOWLEDGE BASE
# -----------------------------
class KnowledgeBase:
    def __init__(self):
        # domain_knowledge: direct facts or advice about the domain
        # inference_rules: logical if-then rules
        # task_methods: optional advanced layer (not used in this simple demo)
        self.domain_knowledge = {}
        self.inference_rules = []
        self.task_methods = []

    def load_domain_knowledge(self, knowledge):
        """Load key-value facts into the knowledge base."""
        self.domain_knowledge.update(knowledge)

    def load_inference_rules(self, rules):
        """Add logical inference rules to the knowledge base."""
        self.inference_rules.extend(rules)

    def load_task_methods(self, methods):
        """Add high-level methods (not used here)."""
        self.task_methods.extend(methods)


# -----------------------------
# INFERENCE ENGINE
# -----------------------------
class InferenceEngine:
    def __init__(self, knowledge_base):
        # The inference engine connects to the knowledge base
        self.knowledge_base = knowledge_base

    def infer(self, input_entities: dict):
        """
        Takes user facts (entities + intent) and checks which rules apply.
        Returns a list of all matching conclusions.
        """
        results = []
        for rule in self.knowledge_base.inference_rules:
            if self.apply_rule(rule, input_entities):
                results.append(rule["conclusion"])
        return results

    def apply_rule(self, rule, input_entities):
        """Checks if all conditions of a rule are true."""
        for condition in rule["conditions"]:
            if not self.check_condition(condition, input_entities):
                return False  # Stop checking if one condition fails
        return True

    def check_condition(self, condition, input_entities):
        """
        Verifies if a user's fact matches the rule's condition.
        Supports an optional 'intent' guard on the condition.
        """
        # Check intent if specified in condition
        if "intent" in condition:
            expected_intent = condition["intent"]
            actual_intent = input_entities.get("intent")
            if actual_intent != expected_intent:
                return False

        # Check attribute condition
        key = condition["attribute"]
        expected = condition.get("value", None)
        if key not in input_entities:
            return False
        if expected is None:
            return True
        return input_entities[key] == expected


# -----------------------------
# NLP PROCESSOR
# -----------------------------
class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.has_ner = True
        except Exception:
            self.nlp = spacy.blank("en")
            self.has_ner = False

    def _make_token_sets(self, doc, raw_text: str):
        if self.has_ner and doc:
            lemmas = {t.lemma_.lower() for t in doc if t.lemma_}
            words = {t.text.lower() for t in doc}
        else:
            # Fallback simple split
            parts = [p for p in re.split(r"\W+", raw_text.lower()) if p]
            lemmas = set(parts)
            words = set(parts)
        return lemmas, words

    def _any(self, tokens: set, candidates):
        return any(c in tokens for c in candidates)

    def process_query(self, query: str):
        text = query.strip().lower()
        doc = self.nlp(text)
        lemmas, words = self._make_token_sets(doc, text)

        # Intent detection
        intent = "query"
        generic_roots = {"want", "need", "try", "wish", "help"}
        root = next((t for t in doc if t.dep_ == "ROOT"), None)
        action = None
        if root and root.lemma_:
            if root.lemma_.lower() in generic_roots:
                action = next(
                    (t for t in doc if t.dep_ in {"xcomp", "advcl"} and t.pos_ == "VERB"),
                    None,
                )
                chosen = action.lemma_ if (action and action.lemma_) else root.lemma_
                intent = chosen.lower()
            else:
                intent = root.lemma_.lower()

        # Synonym normalization (before fallback)
        synonym_map = {
            "share": "export",
            "export": "export",
            "distribute": "export",
            "collaborate": "export",
            "begin": "start",
            "turn on": "activate",
            "turn off": "deactivate",
            "switch": "activate"
        }
        if intent in synonym_map:
            intent = synonym_map[intent]

        # Fallback only if generic and no specific action found
        if (intent == "query" or intent in generic_roots) and not action:
            if self._any(lemmas, {"install", "add"}):
                intent = "install"
            elif self._any(lemmas, {"remove", "uninstall", "delete"}):
                intent = "remove"
            elif self._any(lemmas, {"create", "make"}):
                intent = "create"
            elif self._any(lemmas, {"update", "upgrade"}):
                intent = "update"
            elif self._any(lemmas, {"list", "show"}):
                intent = "list"
            elif self._any(lemmas, {"check", "info", "version"}):
                intent = "check"
            elif self._any(lemmas, {"share", "export", "collaborate", "distribute"}):
                intent = "export"
            elif self._any(lemmas, {"activate", "switch", "turn on"}):
                intent = "activate"
            elif self._any(lemmas, {"deactivate","turn off"}):
                intent = "deactivate"

        # Entities via token presence
        entities = {}
        if self._any(words, {"conda","miniconda","anaconda"}):
            entities["conda"] = True
        if self._any(words, {"env", "environment"}):
            entities["environment"] = True
        if self._any(words, {"package", "library", "pkg"}):
            entities["package"] = True
        if self._any(words, {"python"}):
            entities["python"] = True
        if self._any(words, {"channel", "conda-forge", "bioconda"}) or "-c " in text:
            entities["channel"] = True
        # version indicator
        if any(("==" in text, self._any(words, {"version"}), re.search(r"\b\d+\.\d+(\.\d+)?\b", text))):
            entities["version"] = True

        if self.has_ner:
            for ent in doc.ents:
                entities.setdefault(f"NER_{ent.label_}", set()).add(ent.text)

        return {"intent": intent, "entities": entities}


# -----------------------------
# KNOWLEDGE BASE QUERY
# -----------------------------
class KnowledgeBaseQuery:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def query(self, structured_query):
        intent = structured_query["intent"]
        entities = structured_query["entities"]
        return self.search_knowledge(intent, entities)

    def search_knowledge(self, intent, entities):
        # Try to match the user's intent first
        if intent in self.knowledge_base.domain_knowledge:
            return self.knowledge_base.domain_knowledge[intent]

        # If no direct match, check entity keys or values
        for key, val in entities.items():
            if key in self.knowledge_base.domain_knowledge:
                return self.knowledge_base.domain_knowledge[key]
            if isinstance(val, str) and val in self.knowledge_base.domain_knowledge:
                return self.knowledge_base.domain_knowledge[val]

        # Default fallback response
        return "Sorry, I don’t have information about that issue."


# -----------------------------
# BUILD THE KNOWLEDGE BASE
# -----------------------------
def build_kb():
    kb = KnowledgeBase()

    # STEP 1: Load domain knowledge (direct advice)
    kb.load_domain_knowledge({
        "conda": "Conda is a tool for managing packages, dependencies, and environments. Miniconda is a minimal installation of conda while Anaconda is a full installation packages with GUI.",
        "python": "Python is a programming language often installed with Conda.",
        "channel": "A Conda channel is a package source (e.g., conda-forge). Use to host and distribute packages for third-party developers.",
        "package": "Package is a library that can be install using `conda install PKGNAME` or `pip install PKGNAME`. It is recommend to use `conda install` for a better compatability management experience",
        "environment": "An environment is a virtual space which you can separate packages and dependencies for a project",
        "remove": "Remove a package: `conda remove <pkg>`; remove env: `conda env remove --name <env>`",
        "create": "Create env: `conda create --name <env> python=3.x`; activate: `conda activate <env>`",
    })

    # STEP 2: Load logical inference rules (intent + entity)
    kb.load_inference_rules([
        {
            "conditions":[{"intent": "export", "attribute": "environment", "value": True}],
            "conclusion": "To share you environment with other, you can export it by using `conda export --from-history>ENV.yml` for cross-platform sharing. It recommend to keep your export file as 'environment' for differentiation."
        },
        {
            "conditions":[{"intent": "start", "attribute": "conda", "value": True}],
            "conclusion": "To start conda, you first need to call `conda init`. If it does not work ensure you have conda install and add to PATH"
        },
        {
            "conditions":[{"intent": "install", "attribute": "conda", "value": True}],
            "conclusion": "To install conda you can either download Miniconda or Anaconda from https://docs.conda.io/projects/conda/en/stable/"
        },
        {
            "conditions": [{"intent": "install", "attribute": "package", "value": True}],
            "conclusion": "To install a package, use `conda install <package>`. It recommend to install you package in a separate environment from the default base."
        },
        {
            "conditions": [{"intent": "create", "attribute": "environment", "value": True}],
            "conclusion": "Create a new env: `conda create --name <env> python=3.x`; then `conda activate <env>`."
        },
        {
            "conditions": [{"intent": "update", "attribute": "conda", "value": True}],
            "conclusion": "Update conda: `conda update conda`; update all packages: `conda update --all`."
        },
        {
            "conditions": [{"intent": "list", "attribute": "package", "value": True}],
            "conclusion": "List installed packages: `conda list`; list environments: `conda env list`."
        },
        {
            "conditions": [{"intent": "remove", "attribute": "package", "value": True}],
            "conclusion": "Remove a package: `conda remove <package>`; remove an env: `conda env remove --name <env>`."
        },
        {
            "conditions": [
                {"intent": "install", "attribute": "package", "value": True},
                {"attribute": "channel", "value": True}
            ],
            "conclusion": "Install from a specific channel: `conda install -c <channel> <package>` (e.g., conda-forge)."
        },
        {
            "conditions":[{"intent": "activate", "attribute":"environment", "value": True}],
            "conclusion": "To activate a environment use `conda activate ENVNAME` where ENVNAME is the name of your environment. By default you are in Base environment at start."
        },
        {
            "conditions":[{"intent": "deactivate", "attribute":"environment", "value": True}],
            "conclusion": "To deactivate a environment use `conda deactivate`. If you do this multiple time you can end up deactivate base environment of conda so be careful."                
        },
        {
            "conditions": [{"intent": "clean", "attribute": "conda", "value": True}],
            "conclusion": "To clean up your conda cache use `conda clean --all`."
        }

    ])

    return kb


# -----------------------------
# HANDLE USER INPUT
# -----------------------------
def handle_user_input(kb, nlp_processor, text):
    # STEP 1: Process natural language input
    structured = nlp_processor.process_query(text)

    # STEP 2: Try logical reasoning (pass BOTH intent and entities)
    combined = {"intent": structured["intent"], **structured["entities"]}
    inference = InferenceEngine(kb).infer(combined)

    # STEP 3: If inference gives a result, return it
    if inference:
        return inference[0], structured, inference

    # STEP 4: Otherwise, fall back to simple lookup
    response = KnowledgeBaseQuery(kb).query(structured)
    return response, structured, inference


# -----------------------------
# SUPPORT FUNCTION
# -----------------------------

def random_goodbye():
    # Random goodbye phrases
    GOODBYE_PHRASES = [
        "Goodbye!",
        "See you later.",
        "Happy coding!",
        "May your environments stay clean.",
        "Farewell.",
        "Stay productive!",
        "Until next time.",
        "Au revoir!",
        "Cheers!"
    ]
    return random.choice(GOODBYE_PHRASES)

# -----------------------------
# MAIN PROGRAM LOOP
# -----------------------------
if __name__ == "__main__":
    console = Console()
    kb = build_kb()
    nlp = NLPProcessor()

    console.print("\nCONDA SUPPORT KNOWLEDGE-BASED SYSTEM\n", style="bold blue", justify="center")
    # Create instructions with rich formatting
    instructions = Text()
    instructions.append("Type your ", style="white")
    instructions.append("Conda/Miniconda/Anaconda related question", style="bold cyan")
    instructions.append(".\n", style="white")
    instructions.append("Type '", style="white")
    instructions.append("help", style="bold yellow")
    instructions.append("' for examples. Type '", style="white")
    instructions.append("quit", style="bold red")
    instructions.append("' to exit.", style="white")
    
    console.print(Panel(instructions, title="[bold blue]Instructions[/bold blue]", border_style="blue"))



    EXAMPLES = [
        "I am starting a new project, how should I begin?",
        "I need to install a package but I am in the base environment.",
        "How do I install packages in a specific environment?",
        "I need to export my environment so it is cross platform compatible.",
        "I am getting dependency conflicts during installation.",
        "My disk is full, I need to clean up my conda cache.",
    ]

    while True:
        user_text = input("\n> ").strip()
        if not user_text:
            continue
        lo = user_text.lower()

        if lo in {"quit", "exit"}:
            bye_phrase = random_goodbye()
            console.print(f"\n[bold red]{bye_phrase}[/bold red]\n")
            break
        
        if lo in {"help", "examples"}:
            examples_text = Text()
            for i, e in enumerate(EXAMPLES, 1):
                examples_text.append(f"{i}. ", style="bold cyan")
                examples_text.append(f"{e}\n", style="white")
            
            console.print(Panel(examples_text, title="[bold green]Example Questions[/bold green]", border_style="green"))
            continue

        answer, structured, inference = handle_user_input(kb, nlp, lo)
        console.print(f"Structured Query: {structured}", style="yellow")
        # console.print(f"Inference Results: {inference}\n", style="cyan")
        console.print(Markdown(f"\nAnswer: {answer}\n"))
