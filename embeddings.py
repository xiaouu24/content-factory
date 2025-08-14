import openai
import os
from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime

class EmbeddingManager:
    """Manages embedding generation and caching for content"""
    
    def __init__(self):
        """Initialize OpenAI client for embeddings"""
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"
        self.cache = {}  # Simple in-memory cache
    
    def generate_embedding(self, text: str, cache: bool = True) -> List[float]:
        """Generate embedding for a text string"""
        # Check cache first
        text_hash = self._hash_text(text)
        if cache and text_hash in self.cache:
            return self.cache[text_hash]
        
        # Generate new embedding
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        
        embedding = response.data[0].embedding
        
        # Cache the result
        if cache:
            self.cache[text_hash] = embedding
        
        return embedding
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        # OpenAI supports batch embedding
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        
        return [data.embedding for data in response.data]
    
    def create_content_embedding(self, content: str, content_type: str) -> Dict[str, Any]:
        """Create embedding with metadata for content"""
        embedding = self.generate_embedding(content)
        
        return {
            "embedding": embedding,
            "content": content,
            "content_type": content_type,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "hash": self._hash_text(content)
        }
    
    def create_knowledge_embedding(self, content: str, category: str, source: str) -> Dict[str, Any]:
        """Create embedding for knowledge base content"""
        embedding = self.generate_embedding(content)
        
        return {
            "embedding": embedding,
            "content": content,
            "category": category,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def create_multimodal_embedding(self, text: str, image_description: Optional[str] = None) -> Dict[str, Any]:
        """Create embedding for multimodal content (text + image description)"""
        combined_text = text
        if image_description:
            combined_text = f"{text}\n\nImage: {image_description}"
        
        embedding = self.generate_embedding(combined_text)
        
        return {
            "embedding": embedding,
            "text": text,
            "image_description": image_description,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        import numpy as np
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def find_similar_content(self, query_embedding: List[float], embeddings: List[List[float]], threshold: float = 0.7) -> List[int]:
        """Find indices of similar content based on embedding similarity"""
        similar_indices = []
        
        for i, embedding in enumerate(embeddings):
            similarity = self.compute_similarity(query_embedding, embedding)
            if similarity >= threshold:
                similar_indices.append((i, similarity))
        
        # Sort by similarity (descending)
        similar_indices.sort(key=lambda x: x[1], reverse=True)
        
        return [idx for idx, _ in similar_indices]
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text (for caching)"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached embeddings"""
        return len(self.cache)
    
    def create_content_summary_embedding(self, brief: Dict[str, Any], blog: str, social_posts: List[str]) -> Dict[str, Any]:
        """Create a comprehensive embedding for an entire content package"""
        # Combine all content into a summary
        summary_parts = [
            f"Product: {brief.get('product_name', '')}",
            f"Category: {brief.get('product_category', '')}",
            f"Objective: {brief.get('objective', '')}",
            f"Blog excerpt: {blog[:500]}",  # First 500 chars of blog
        ]
        
        # Add social post samples
        for i, post in enumerate(social_posts[:3]):  # First 3 posts
            summary_parts.append(f"Social post {i+1}: {post}")
        
        summary = "\n".join(summary_parts)
        embedding = self.generate_embedding(summary)
        
        return {
            "embedding": embedding,
            "summary": summary,
            "brief": brief,
            "content_types": ["blog", "social"],
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def create_style_embedding(self, content: str, style_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Create embedding for style examples with attributes"""
        # Enhance content with style attributes for better retrieval
        style_text = f"{content}\n\nStyle attributes: "
        for key, value in style_attributes.items():
            style_text += f"{key}: {value}, "
        
        embedding = self.generate_embedding(style_text)
        
        return {
            "embedding": embedding,
            "content": content,
            "style_attributes": style_attributes,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }