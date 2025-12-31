import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# -------------------------
# Paths & constants
# -------------------------
DATA_PATH = Path(__file__).parent.parent / "data" / "normalized_blocks.json"
COLLECTION_NAME = "block_grammar"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K_SEMANTIC = 8
TOP_K_KEYWORD = 20

KEYWORD_TO_MODULE = {
    "print": ["Text"],
    "display": ["Text"],
    "output": ["Text"],
    "number": ["Numbers"],
    "sum": ["Numbers"],
    "add": ["Numbers"],
    "loop": ["Loops"],
    "repeat": ["Loops"],
    "if": ["Conditionals"],
    "condition": ["Conditionals"],
}

class BlockKnowledgeBase:
    def __init__(self):
        self.blocks = self._load_blocks()
        self.by_type = {b["type"]: b for b in self.blocks}
        self.by_module = self._index_by_module()

        # 🔥 LOCAL EMBEDDINGS
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # 🔥 REMOTE QDRANT
        self.qdrant = QdrantClient(
            url="https://64ae9382-4720-40e0-92ef-b7ee2da511c7.us-east4-0.gcp.cloud.qdrant.io:6333",
            api_key=os.getenv("QDRANT_API_KEY", None),
        )

    def _load_blocks(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _index_by_module(self):
        index = {}
        for block in self.blocks:
            index.setdefault(block["module"], []).append(block)
        return index

    def _semantic_search(self, problem_text: str):
        query_vector = self.embedder.encode(
            problem_text,
            normalize_embeddings=True
        ).tolist()

        results = self.qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=TOP_K_SEMANTIC,
            with_payload=True,
        )

        return [r.payload for r in results]

    def _keyword_search(self, problem_text: str):
        problem_text = problem_text.lower()
        relevant_modules = set()

        for keyword, modules in KEYWORD_TO_MODULE.items():
            if keyword in problem_text:
                relevant_modules.update(modules)

        relevant_modules.update(["Text", "Numbers", "Logic & Booleans"])

        blocks = []
        for module in relevant_modules:
            blocks.extend(self.by_module.get(module, []))

        return blocks[:TOP_K_KEYWORD]

    def retrieve_relevant_blocks(self, problem_text: str):
        semantic_blocks = []
        try:
            semantic_blocks = self._semantic_search(problem_text)
        except Exception as e:
            print(f"[WARN] Semantic search failed ({e}), falling back to keyword only")

        keyword_blocks = self._keyword_search(problem_text)

        merged = {}
        for block in semantic_blocks + keyword_blocks:
            merged[block["type"]] = block

        return list(merged.values())

    def format_for_llm(self, blocks):
        formatted = []
        for b in blocks:
            formatted.append({
                "type": b.get("type"),
                "category": b.get("category"),
                "module": b.get("module"),
                "kind": b.get("kind"),
                "fields": list(b.get("fields", [])),
                "value_inputs": list(b.get("value_inputs", [])),
                "statement_inputs": list(b.get("statement_inputs", [])),
            })
        return formatted


# Debug run
if __name__ == "__main__":
    kb = BlockKnowledgeBase()
    problem = "Print Hello World using a loop"
    blocks = kb.retrieve_relevant_blocks(problem)
    print(json.dumps(kb.format_for_llm(blocks), indent=2))
