print("RAG Service: Module loading...")
import json
import os
import httpx
import chromadb
# Simple imports to avoid version conflicts
try:
    from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
except ImportError:
    # Fallback for older versions
    Documents = list
    Embeddings = list
    EmbeddingFunction = object

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="llama3.2", url=None):
        self.model_name = os.getenv("LLM_MODEL_NAME", model_name)
        self.url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        # Using synchronous call for ChromaDB compatibility
        with httpx.Client() as client:
            for text in input:
                try:
                    response = client.post(
                        f"{self.url}/api/embeddings",
                        json={"model": self.model_name, "prompt": text},
                        timeout=300.0
                    )
                    response.raise_for_status()
                    embeddings.append(response.json()["embedding"])
                except Exception as e:
                    print(f"Embedding error: {e}")
                    # Zero fallback (3072 for llama3.2)
                    embeddings.append([0.0] * 3072)
        return embeddings

class RAGService:
    def __init__(self, data_path="data/policies"):
        print("RAGService: Initializing...")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_fn = OllamaEmbeddingFunction()
        self.data_path = data_path
        self.collection = None

    async def initialize(self):
        try:
            print("RAGService: Resetting collection for fresh start...")
            try:
                self.client.delete_collection("climate_policies")
            except:
                pass
            
            self.collection = self.client.create_collection(
                name="climate_policies",
                embedding_function=self.embedding_fn
            )
            print("RAGService: Collection created. Starting ingestion...")
            await self._ingest_policies()
            print("RAGService: Background initialization complete.")
        except Exception as e:
            print(f"RAGService CRITICAL ERROR: {e}")

    async def _ingest_policies(self):
        for filename in os.listdir(self.data_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_path, filename), "r") as f:
                    policy_data = json.load(f)
                    country = policy_data["country"]
                    
                    documents = []
                    metadatas = []
                    ids = []
                    
                    for i, pos in enumerate(policy_data["key_positions"]):
                        documents.append(pos)
                        metadatas.append({"country": country, "type": "key_position"})
                        ids.append(f"{country}_kp_{i}")
                    
                    for i, line in enumerate(policy_data["red_lines"]):
                        documents.append(line)
                        metadatas.append({"country": country, "type": "red_line"})
                        ids.append(f"{country}_rl_{i}")
                    
                    print(f"RAGService: Ingesting {len(documents)} points for {country}...")
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )

    def retrieve(self, query, country, n_results=3):
        if not self.collection:
            print("RAGService: Retrieve failed - collection not ready.")
            return []
        try:
            results = self.collection.query(
                query_texts=[query],
                where={"country": country},
                n_results=n_results
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []

_rag_service = None

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
