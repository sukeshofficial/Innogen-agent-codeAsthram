import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, Distance, VectorParams

from agent.qdrant.client import get_qdrant_client

# -------------------------
# Env setup
# -------------------------
load_dotenv()

COLLECTION_NAME = "block_grammar"

# Sentence-Transformers model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size

# -------------------------
# Load embedding model (ONCE)
# -------------------------
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# -------------------------
# Embedding helper (FREE & SAFE)
# -------------------------
def embed(text: str) -> list[float]:
    if not isinstance(text, str):
        raise ValueError(f"Embedding input must be string, got {type(text)}")

    text = text.strip()
    if not text:
        raise ValueError("Embedding input text is empty")

    vector = embedding_model.encode(
        text,
        normalize_embeddings=True  # cosine similarity friendly
    )

    return vector.tolist()

# -------------------------
# Block → Semantic Text
# -------------------------
def block_to_text(block: dict) -> str:
    fields = block.get("fields", [])
    value_inputs = block.get("value_inputs", [])
    statement_inputs = block.get("statement_inputs", [])

    return f"""
Block type: {block.get('type', 'unknown')}.
Category: {block.get('category', 'unknown')}.
Module: {block.get('module', 'unknown')}.
Kind: {block.get('kind', 'unknown')}.
Fields: {', '.join(fields) if fields else 'none'}.
Value inputs: {', '.join(value_inputs) if value_inputs else 'none'}.
Statement inputs: {', '.join(statement_inputs) if statement_inputs else 'none'}.
""".strip()

# -------------------------
# Main Ingestion
# -------------------------
def main():
    qdrant = get_qdrant_client()

    # Create collection (idempotent)
    try:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print("✅ Collection created")
    except Exception:
        print("ℹ️ Collection already exists")

    # Load normalized blocks
    BASE_DIR = Path(__file__).resolve().parents[2]
    BLOCKS_PATH = BASE_DIR / "agent" / "data" / "normalized_blocks.json"

    if not BLOCKS_PATH.exists():
        raise FileNotFoundError(f"Blocks file not found: {BLOCKS_PATH}")

    with open(BLOCKS_PATH, "r", encoding="utf-8") as f:
        blocks = json.load(f)

    points = []
    skipped = 0

    for block in blocks:
        try:
            text = block_to_text(block)
            vector = embed(text)

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=block,  # full grammar payload
                )
            )

        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipping block {block.get('type')} → {e}")

    if not points:
        raise RuntimeError("No valid blocks were embedded. Aborting upsert.")

    BATCH_SIZE = 100  # safe default

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i : i + BATCH_SIZE]
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )
        print(f"⬆️ Uploaded batch {i // BATCH_SIZE + 1}")


    print(f"✅ Uploaded {len(points)} blocks to Qdrant")
    if skipped:
        print(f"⚠️ Skipped {skipped} invalid blocks")

# -------------------------
# Entry
# -------------------------
if __name__ == "__main__":
    main()
