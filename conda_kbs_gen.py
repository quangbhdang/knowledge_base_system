import re
from typing import Dict, List, Any
import spacy
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

# -----------------------------
# 1. Domain knowledge (Facts and Advice)
# -----------------------------

# KNOWLEDGE stores both general advice/tips ('advice') and executable commands ('command').
# This structure defines the facts of the domain.
KNOWLEDGE: Dict[str, Any] = {
    "advice": {
        # Environment Management Advice (Derived from the conversation history)
        "new_project_start": "For any new project or workflow, it is **recommended to create a new environment** and name it descriptively .",
        "activation_sequence": "You must **activate an environment before installing packages** within it .",
        "environment_scoping": "Specifying the environment name (`--name ENVNAME`) **confines conda commands to that environment** .",
        "startup_status": "When starting a session, use `conda info --envs` to **list all environments**. Environments marked with an asterisk are active .",

        # Package and Dependency Advice
        "automatic_resolution": "Remember that **package dependencies and platform specifics are automatically resolved** when using conda.",

        # Export/Import Guidance
        "general_export": "Conda environment can be export so that other Conda user replicate you environment using the command, with the flags `--no-builds` to ensure compatibility across system (e.g, Window)(`conda env export --no-builds > environment.yml)",
        "export_cross_platform": "To create a **cross-platform compatible** export, use the history-based command (`conda export --from-history>ENV.yml`).",
        "export_naming_tip": "It is recommended to **name the export file 'environment'** as the original environment name will be preserved upon import.",
        "detailed_export": "For platform, package, and channel specifics, export explicitly to a `.txt` file (`conda list --explicit>ENV.txt`).",
        
        # Maintenance and Help Advice
        "general_help": "To get help for any command, use `conda COMMAND --help`.",
        "cleanup": "To remove all unused files (cache, tarballs), use `conda clean --all`."
    },

    "command": {
        # General Commands (Analogous to DNS flush policies [6, 7, 37, 38])
        "verify_install": "`conda info`",
        "update_conda": "`conda update --name base conda`",
        "clean_all": "`conda clean --all`",
        
        # Environment Management Commands
        "list_envs": "`conda info --envs`",
        "create_env_base": "`conda create --name ENVNAME`",
        "activate_env": "`conda activate ENVNAME`",
        "install_pkg_env": "`conda install --name ENVNAME PKGNAME1 PKGNAME2`",
        "delete_env": "`conda remove --name ENVNAME --all`",
        
        # Export/Import Commands
        "export_history_yml": "`conda export --from-history>ENV.yml`",
        "export_explicit_txt": "`conda list --explicit>ENV.txt`",
        "import_yml": "`conda env create --name ENVNAME --file ENV.yml`",
        
        # Revision Commands
        "list_revisions": "`conda list --name ENVNAME --revisions`",
    }
}

# -----------------------------
# 1. Domain knowledge (Rules/Logic)
# -----------------------------

# RULES define conditional logic applied by the InferenceEngine.
RULES: List[Dict[str, Any]] = [

    # R001: New Project Start (Requires Creation + Descriptive Naming)
    {"id": "conda_new_project_sequence",
     "conditions": [{"attribute": "new_project", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["new_project_start"] +
                   " To start, execute the command: " + 
                   KNOWLEDGE["command"]["create_env_base"]},

    # R002: Package Installation Pre-requisite (Must activate first)
    {"id": "conda_install_requires_activation",
     "conditions": [{"attribute": "install_package", "op": "eq", "value": True},
                    {"attribute": "active_env_check", "op": "eq", "value": False}],
     "conclusion": KNOWLEDGE["advice"]["activation_sequence"] +
                   " You must activate the environment first. Use command: " +
                   KNOWLEDGE["command"]["activate_env"]},

    # R003: Targeted Package Installation (Requires --name)
    {"id": "conda_install_specific_env",
     "conditions": [{"attribute": "install_package", "op": "eq", "value": True},
                    {"attribute": "target_specific_env", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["environment_scoping"] +
                   " Use the command: " +
                   KNOWLEDGE["command"]["install_pkg_env"]},

    # R004: Export for Cross-Platform Portability
    {"id": "conda_export_portable",
     "conditions": [{"attribute": "export_env", "op": "eq", "value": True},
                    {"attribute": "cross_platform", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["export_cross_platform"] + " "+ KNOWLEDGE["advice"]["export_naming_tip"] + " command: " + KNOWLEDGE["command"]["export_history_yml"]},
    # {"id": "conda_export_env",
    #     #  "conditions":[{"attribute": "export_env", "op": "eq", "value": True},
    #                {"attribute": "environment", "op": "eq", "value":True}],
    #  "conclusion": KNOWLEDGE["advice"]["environment"]
    # R005: Export for Maximum Detail (Channel specific)
    {"id": "conda_export_detailed",
     "conditions": [{"attribute": "export_env", "op": "eq", "value": True},
                    {"attribute": "full_detail", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["detailed_export"] + " command: " + KNOWLEDGE["command"]["export_explicit_txt"]},

    # R006: Troubleshooting Dependency Issues
    {"id": "conda_dependency_error",
     "conditions": [{"attribute": "dependency_error", "op": "eq", "value": True}],
     "conclusion": "You may have a dependency conflict. Remember that " +
                   KNOWLEDGE["advice"]["automatic_resolution"] +
                   " If resolution fails, try listing revisions using command: " +
                   KNOWLEDGE["command"]["list_revisions"]},

    # R007: Cleaning Up System Resources
    {"id": "conda_system_cleanup",
     "conditions": [{"attribute": "cleanup_needed", "op": "eq", "value": True}],
     "conclusion": "To free disk space by clearing cache and unused packages, use the advice: " +
                   KNOWLEDGE["advice"]["cleanup"] +
                   " command: " + KNOWLEDGE["command"]["clean_all"]}
]

# -----------------------------
# 2. Inference engine (Applies logic)
# -----------------------------

class InferenceEngine:
    """Applies conditional logic defined in RULES to extracted entities."""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    def infer(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Checks which rules apply given the current entities [19]."""
        results: List[Dict[str, Any]] = []
        for rule in self.rules:
            if self._rule_applies(rule, entities):
                results.append({"rule_id": rule["id"], "conclusion": rule["conclusion"]})
        return results

    def _rule_applies(self, rule: Dict[str, Any], entities: Dict[str, Any]) -> bool:
        """Checks all conditions for a single rule [19]."""
        for cond in rule.get("conditions", []):
            if not self._check(cond, entities):
                return False
        return True

    def _check(self, cond: Dict[str, Any], entities: Dict[str, Any]) -> bool:
        """Evaluates a single condition based on the operator [20]."""
        key = cond.get("attribute")
        op = cond.get("op", "eq")
        expect = cond.get("value", None)

        if op == "exists":
            return key in entities
        
        if key not in entities:
            return False

        value = entities[key]

        if op == "eq":
            return value == expect
        if op == "neq":
            return value != expect
        # Includes other operators defined in the source, if needed:
        if op == "in":
            return value in expect
        if op == "contains":
            if isinstance(value, str) and isinstance(expect, str):
                return expect in value
            if isinstance(value, list):
                return expect in value

        return False

# -----------------------------
# 3. NLP processor (Extracts intent and entities)
# -----------------------------

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = spacy.blank("en")

    def process_query(self, text: str):
        t = text.strip().lower()
        doc = self.nlp(t)
        entities: Dict[str, Any] = {}
        intent = "diagnose"

        # Use spaCy to find main verb (intent)
        for token in doc:
            if token.dep_ == "ROOT":
                intent = token.lemma_
                break

        # Use spaCy to extract entities based on noun chunks and keywords
        for chunk in doc.noun_chunks:
            if "environment" in chunk.text:
                entities["environment"] = True
            if "package" in chunk.text:
                entities["package"] = True

        # Use keyword matching as fallback (can be improved with spaCy matcher)
        if any(w in t for w in ["new project", "start workflow", "create environment"]):
            entities["new_project"] = True
        if any(w in t for w in ["install", "add package", "need package", "install library"]):
            entities["install_package"] = True
        if any(w in t for w in ["active environment", "current environment", "which environment"]):
            entities["active_env_check"] = False
        if any(w in t for w in ["specific environment", "target environment", "named environment"]):
            entities["target_specific_env"] = True
        if any(w in t for w in ["export", "save environment", "backup environment", "share environment"]):
            entities["export_env"] = True
        if any(w in t for w in ["cross platform", "portable", "different os", "multiple platforms"]):
            entities["cross_platform"] = True
        if any(w in t for w in ["detailed", "explicit", "full detail", "complete export"]):
            entities["full_detail"] = True
        if any(w in t for w in ["dependency error", "dependency conflict", "package conflict", "resolution failed"]):
            entities["dependency_error"] = True
        if any(w in t for w in ["cleanup", "clean up", "disk space", "cache", "free space", "storage"]):
            entities["cleanup_needed"] = True

        # Error code extraction (regex)
        m = re.search(r"(error\s+code\s*[:#]?\s*|code\s*[:#]?\s*)([a-z0-9\-x]+)", t)
        if m:
            entities["error_code"] = m.group(2)

        return {"intent": intent, "entities": entities}

# -----------------------------
# 4. Knowledge Base Query (Direct lookups/Fallback)
# -----------------------------

class KnowledgeBaseQuery:
    """Performs direct lookups for general advice when inference rules yield no conclusion [28]."""
    
    def __init__(self, advice: Dict[str, str]):
        self.advice = advice

    def lookup(self, entities: Dict[str, Any]) -> List[str]:
        """Looks up general advice based on detected entities [29]."""
        hits: List[str] = []
        
        # Priority list of Conda advice keys to check for general suggestions
        priority = [
            "new_project_start", "activation_sequence", "environment_scoping", 
            "automatic_resolution", "export_naming_tip", "cleanup", "general_help"
        ]

        for key in priority:
            # Check if the entity key matches a key in our advice dictionary
            if key in entities and key in self.advice:
                hits.append(self.advice[key])

        if not hits and "general_help" in self.advice:
            hits.append(self.advice["general_help"])

        return hits

# -----------------------------
# 5. Integration and Controller
# -----------------------------
def present_answer(structured, conclusions, advice):
    """Formats and prints the KBS response using rich library for better visualization"""
    console = Console()
    
    # Display structured entities in a panel
    entities_text = Text()
    if structured["entities"]:
        for key, value in structured["entities"].items():
            entities_text.append(f"{key}: {value}\n", style="cyan")
    else:
        entities_text.append("None detected", style="dim")
    
    console.print(Panel(entities_text, title="[bold blue]Detected Entities[/bold blue]", border_style="blue"))

    # Display conclusions if any rules were applied
    if conclusions:
        console.print("\n[bold green]Recommendations:[/bold green]")
        
        for i, c in enumerate(conclusions, 1):
            # Render markdown formatting in conclusions
            console.print(f"[dim]{i}.[/dim] ", end="")
            conclusion_text = Markdown(c['conclusion'])
            console.print(conclusion_text)
    else:
        console.print(Panel("[yellow]No specific rule applied.[/yellow]", border_style="yellow"))

    # Display general advice if available
    if advice:
        console.print("\n[bold cyan]General Advice:[/bold cyan]")
        for i, a in enumerate(advice, 1):
            # Render markdown formatting in advice
            advice_text = Text.from_markup(a)
            console.print(f"[dim]{i}.[/dim] ", end="")
            console.print(advice_text)

def handle_user_input():
    """Initializes components and runs the main loop, integrating all classes [30]."""
    console = Console()
    
    # Create a beautiful header with rich
    header_text = Text("Conda Support Knowledge-Based System (CSKBS)", style="bold magenta")
    console.print(Panel.fit(header_text, border_style="magenta"))
    
    # Create instructions with rich formatting
    instructions = Text()
    instructions.append("Type your ", style="white")
    instructions.append("Conda command question", style="bold cyan")
    instructions.append(".\n", style="white")
    instructions.append("Type '", style="white")
    instructions.append("help", style="bold yellow")
    instructions.append("' for examples. Type '", style="white")
    instructions.append("quit", style="bold red")
    instructions.append("' to exit.", style="white")
    
    console.print(Panel(instructions, title="[bold blue]Instructions[/bold blue]", border_style="blue"))

    # Initialize components
    nlp = NLPProcessor()
    engine = InferenceEngine(RULES)
    kbq = KnowledgeBaseQuery(KNOWLEDGE["advice"])

    EXAMPLES = [
        "I am starting a new project, how should I begin?",
        "I need to install a package but I am in the base environment.",
        "How do I install packages in a specific environment?",
        "I need to export my environment so it is cross platform compatible.",
        "I am getting dependency conflicts during installation.",
        "My disk is full, I need to clean up my conda cache.",
    ]

    while True:
        text = input("\n> ").strip()
        if not text:
            continue
        lo = text.lower()

        if lo in {"quit", "exit"}:
            console.print("[bold red]Goodbye.[/bold red]")
            break
        
        if lo in {"help", "examples"}:
            examples_text = Text()
            for i, e in enumerate(EXAMPLES, 1):
                examples_text.append(f"{i}. ", style="bold cyan")
                examples_text.append(f"{e}\n", style="white")
            
            console.print(Panel(examples_text, title="[bold green]Example Questions[/bold green]", border_style="green"))
            continue

        # 1. Extract intent and entities
        structured = nlp.process_query(text)
        entities = structured["entities"]
        
        # 2. Infer conclusions
        conclusions = engine.infer(entities)

        # 3. Perform fallback lookup if no rules were triggered
        extra_advice = []
        if not conclusions:
             # Only call lookup if the engine didn't find specific conclusions
            extra_advice = kbq.lookup(entities)

        # 4. Present answer
        present_answer(structured, conclusions, extra_advice)

if __name__ == "__main__":
    handle_user_input()