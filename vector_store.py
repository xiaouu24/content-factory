import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class VectorStore:
    """ChromaDB vector store wrapper for content factory"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client with persistence"""
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Use OpenAI embeddings (requires OPENAI_API_KEY)
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize all required collections"""
        
        # Collection for all generated content
        self.content_history = self.client.get_or_create_collection(
            name="content_history",
            embedding_function=self.embedding_function,
            metadata={"description": "All generated content with metadata"}
        )
        
        # Collection for knowledge base (product docs, APIs, features)
        self.knowledge_base = self.client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_function,
            metadata={"description": "Product documentation and specifications"}
        )
        
        # Collection for high-performing content examples
        self.style_examples = self.client.get_or_create_collection(
            name="style_examples",
            embedding_function=self.embedding_function,
            metadata={"description": "High-performing content templates and examples"}
        )
        
        # Collection for visual assets and prompts
        self.brand_assets = self.client.get_or_create_collection(
            name="brand_assets",
            embedding_function=self.embedding_function,
            metadata={"description": "Visual prompts and successful image themes"}
        )
        
        # Collection for performance metrics
        self.performance_metrics = self.client.get_or_create_collection(
            name="performance_metrics",
            embedding_function=self.embedding_function,
            metadata={"description": "Content performance analytics and feedback"}
        )
    
    def add_content(self, content_type: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add generated content to the history"""
        doc_id = f"{content_type}_{datetime.now().isoformat()}"
        
        # Add timestamp and type to metadata
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["content_type"] = content_type
        
        self.content_history.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id
    
    def add_knowledge(self, category: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add product knowledge to the knowledge base"""
        doc_id = f"knowledge_{category}_{datetime.now().isoformat()}"
        
        metadata["category"] = category
        metadata["timestamp"] = datetime.now().isoformat()
        
        self.knowledge_base.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id
    
    def add_style_example(self, content_type: str, content: str, performance_score: float, metadata: Dict[str, Any]) -> str:
        """Add high-performing content as a style example"""
        doc_id = f"style_{content_type}_{datetime.now().isoformat()}"
        
        metadata["content_type"] = content_type
        metadata["performance_score"] = performance_score
        metadata["timestamp"] = datetime.now().isoformat()
        
        self.style_examples.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id
    
    def search_similar_content(self, query: str, content_type: Optional[str] = None, n_results: int = 5) -> Dict[str, Any]:
        """Search for similar content in history"""
        where_clause = {"content_type": content_type} if content_type else None
        
        results = self.content_history.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        return self._format_results(results)
    
    def search_knowledge(self, query: str, category: Optional[str] = None, n_results: int = 5) -> Dict[str, Any]:
        """Search the knowledge base"""
        where_clause = {"category": category} if category else None
        
        results = self.knowledge_base.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        return self._format_results(results)
    
    def get_style_examples(self, content_type: str, min_score: float = 0.7, n_results: int = 3) -> Dict[str, Any]:
        """Get high-performing style examples"""
        results = self.style_examples.query(
            query_texts=[f"high performing {content_type} content"],
            n_results=n_results,
            where={
                "$and": [
                    {"content_type": content_type},
                    {"performance_score": {"$gte": min_score}}
                ]
            }
        )
        
        return self._format_results(results)
    
    def check_duplicate(self, content: str, threshold: float = 0.95) -> bool:
        """Check if similar content already exists"""
        results = self.content_history.query(
            query_texts=[content],
            n_results=1
        )
        
        if results['distances'] and results['distances'][0]:
            # ChromaDB uses cosine distance, lower is more similar
            similarity = 1 - results['distances'][0][0]
            return similarity >= threshold
        return False
    
    def add_performance_metric(self, content_id: str, metrics: Dict[str, Any]) -> str:
        """Add performance metrics for content"""
        metric_id = f"metric_{content_id}_{datetime.now().isoformat()}"
        
        metrics["content_id"] = content_id
        metrics["timestamp"] = datetime.now().isoformat()
        
        self.performance_metrics.add(
            documents=[json.dumps(metrics)],
            metadatas=[metrics],
            ids=[metric_id]
        )
        return metric_id
    
    def get_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Get performance metrics for specific content"""
        results = self.performance_metrics.query(
            query_texts=[content_id],
            n_results=10,
            where={"content_id": content_id}
        )
        
        return self._format_results(results)
    
    def _format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format ChromaDB results for easier consumption"""
        formatted = {
            "documents": [],
            "metadatas": [],
            "distances": []
        }
        
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted["documents"].append(doc)
                formatted["metadatas"].append(results['metadatas'][0][i] if results['metadatas'] else {})
                formatted["distances"].append(results['distances'][0][i] if results['distances'] else 0)
        
        return formatted
    
    def clear_collection(self, collection_name: str):
        """Clear a specific collection (use with caution)"""
        if collection_name == "content_history":
            self.content_history.delete()
        elif collection_name == "knowledge_base":
            self.knowledge_base.delete()
        elif collection_name == "style_examples":
            self.style_examples.delete()
        elif collection_name == "brand_assets":
            self.brand_assets.delete()
        elif collection_name == "performance_metrics":
            self.performance_metrics.delete()
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored content"""
        return {
            "content_history": self.content_history.count(),
            "knowledge_base": self.knowledge_base.count(),
            "style_examples": self.style_examples.count(),
            "brand_assets": self.brand_assets.count(),
            "performance_metrics": self.performance_metrics.count()
        }