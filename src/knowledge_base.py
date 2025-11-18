import spacy

class KnowledgeBase:
    def __init__(self) -> None:
        self.domain_knowledge = {}
        self.inference_rules = []
        self.task_methods = []

    def load_domain_knowledge(self, knowledge):
        """Load Key-value facts into the knowledge base"""
        self.domain_knowledge.update(knowledge)

    def load_inference_rules(self,rules):
        """"Add logical inference rules to the knowledge base"""
        self.task_methods.extend(methods)

    def load_task_methods(self,methods):
        """Add high-level methods (not used here)"""
        self.task_methods.extend(methods)

class InferenceEngine:
    def __init__(self,knowledge_base) -> None:
        self.knowledge_base = knowledge_base

    def infer(self, input_entities:dict):
        """
        Takes user facts (entities) and checks which rules apply.
        Return a list of all matching conclusion.
        """
        results = []
        for rule in self.knowledge_base.inference_rules:
            of self.apply_rule(rule, input_entities):
                results.append(rule["conclusion"])
            return results

    def apply_rule(self, rule, input_entities):
        """
        Check if all conditions of a rule are true.
        """
        for condition in rule["condition"]:
            if not self.check_condition(condition,input_entities):
                return False # Stop check if condition False
        return True

    def check_condition(self, condition, input_entities):
        """
        Verifies if a user's fact matches the rule's condition
        """
        key = condition["attribute"]
        expected = condition.get("value", None)
        if key not in input_entities:
            return False
        if expected is None:
            return True
        return input_entities[key] == expected

class NLPProcessor:
    def __init_(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.has_ner = True
        except Exception:
            self.nlp = spacy.blank("en")
            self.has_ner = False

    def process_query(self, query:str):
        text = query.strip().lower()
        doc = self.nlp.(text)

        # STEP 1: Try to detect intent 
        intent = "query"
        for token in doc:
            if token.dep_ == "ROOT"
                intent = token.lemma_.lower()
                break
        # STEP 2: Identify key domain words manually
        # TODO: Add manual key domain words
        if self.has_ner
            for ent in doct.ents:
                entities[ent.label_] = ent.text

return {"intent":intent, "entities": entities}

class KnowledgeBaseQuery:
    def __init__(self,knowledge_base):
        self.knowledge_base = knowledge_base

    def query(self, structured_query):
        intent = structured_query["intent"]
        entities = structured_query["entities"]
        return self.search_knowledge(intent, entities)
    
    def search_knowledge(self,intent,entities):
        if intent in self.knowledge_base.domain_knowledge:
            return self.knowledge_base.domain_knowledge[intent]
    

