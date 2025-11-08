import chromadb
from chromadb.config import Settings
import os

class VectorDatabase:
    def __init__(self, agent_name: str, persist_directory: str = None):
        """Initialize vector database for an agent
        Uses an absolute path to avoid issues with varying working directories.
        You can override the base directory with env var VECTOR_DB_DIR.
        """
        self.agent_name = agent_name

        # Determine a stable absolute base directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = (
            os.getenv("VECTOR_DB_DIR")
            or os.path.join(project_root, "vector_db")
        )
        if persist_directory:
            base_dir = persist_directory

        self.persist_directory = os.path.join(base_dir, agent_name)
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection for this agent
        self.collection = self.client.get_or_create_collection(
            name=f"{agent_name}_schedule",
            metadata={"description": f"Daily routine and schedule data for {agent_name}"}
        )
    
    def add_data(self, text: str, metadata: dict = None):
        """Add data to the vector database"""
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Add to collection
        self.collection.add(
            documents=[text],
            ids=[doc_id],
            metadatas=[metadata]
        )
        
        return doc_id
    
    def search(self, query: str, n_results: int = 5):
        """Search for similar data in the vector database"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    
    def get_all(self):
        """Get all data from the vector database"""
        return self.collection.get()
    
    def delete(self, doc_id: str):
        """Delete a document by ID"""
        self.collection.delete(ids=[doc_id])
    
    def update(self, doc_id: str, text: str, metadata: dict = None):
        """Update a document"""
        if metadata is None:
            metadata = {}
        
        self.collection.update(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
    
    def delete_all(self):
        """Delete all documents from the collection"""
        all_data = self.get_all()
        if all_data['ids']:
            self.collection.delete(ids=all_data['ids'])
            return len(all_data['ids'])
        return 0

