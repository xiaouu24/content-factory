from typing import List, Dict, Any, Optional
from vector_store import VectorStore
from embeddings import EmbeddingManager
import json

class RetrievalSystem:
    """RAG system for agents to retrieve relevant context"""
    
    def __init__(self):
        """Initialize retrieval system with vector store and embedding manager"""
        self.vector_store = VectorStore()
        self.embedding_manager = EmbeddingManager()
    
    def retrieve_similar_content(self, query: str, content_type: Optional[str] = None, max_results: int = 3) -> Dict[str, Any]:
        """Retrieve similar content from history for context"""
        results = self.vector_store.search_similar_content(query, content_type, max_results)
        
        # Format for agent consumption
        context_items = []
        for i, doc in enumerate(results["documents"]):
            context_items.append({
                "content": doc,
                "metadata": results["metadatas"][i],
                "similarity": 1 - results["distances"][i]  # Convert distance to similarity
            })
        
        return {
            "query": query,
            "context_items": context_items,
            "count": len(context_items)
        }
    
    def retrieve_knowledge(self, query: str, category: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
        """Retrieve relevant knowledge from the knowledge base"""
        results = self.vector_store.search_knowledge(query, category, max_results)
        
        knowledge_items = []
        for i, doc in enumerate(results["documents"]):
            knowledge_items.append({
                "content": doc,
                "category": results["metadatas"][i].get("category", "general"),
                "source": results["metadatas"][i].get("source", "unknown"),
                "relevance": 1 - results["distances"][i]
            })
        
        return {
            "query": query,
            "knowledge_items": knowledge_items,
            "count": len(knowledge_items)
        }
    
    def retrieve_style_examples(self, content_type: str, min_performance: float = 0.7) -> Dict[str, Any]:
        """Retrieve high-performing style examples for agents"""
        results = self.vector_store.get_style_examples(content_type, min_performance)
        
        examples = []
        for i, doc in enumerate(results["documents"]):
            examples.append({
                "content": doc,
                "performance_score": results["metadatas"][i].get("performance_score", 0),
                "metadata": results["metadatas"][i]
            })
        
        return {
            "content_type": content_type,
            "examples": examples,
            "count": len(examples)
        }
    
    def check_content_duplicate(self, content: str, threshold: float = 0.95) -> Dict[str, Any]:
        """Check if content is too similar to existing content"""
        is_duplicate = self.vector_store.check_duplicate(content, threshold)
        
        if is_duplicate:
            # Get the similar content for reference
            similar = self.vector_store.search_similar_content(content, n_results=1)
            return {
                "is_duplicate": True,
                "similar_content": similar["documents"][0] if similar["documents"] else None,
                "metadata": similar["metadatas"][0] if similar["metadatas"] else None
            }
        
        return {"is_duplicate": False}
    
    def get_agent_context(self, agent_name: str, query: str) -> Dict[str, Any]:
        """Get comprehensive context for a specific agent"""
        context = {
            "agent": agent_name,
            "query": query,
            "retrieved_context": {}
        }
        
        # Agent-specific retrieval strategies
        if agent_name == "Planner":
            # Retrieve similar briefs and successful campaigns
            context["retrieved_context"]["similar_briefs"] = self.retrieve_similar_content(
                query, content_type="brief", max_results=2
            )
            context["retrieved_context"]["knowledge"] = self.retrieve_knowledge(
                query, category="product", max_results=3
            )
            
        elif agent_name == "Blog Writer":
            # Retrieve similar blog posts and technical documentation
            context["retrieved_context"]["similar_blogs"] = self.retrieve_similar_content(
                query, content_type="blog", max_results=2
            )
            context["retrieved_context"]["style_examples"] = self.retrieve_style_examples("blog")
            context["retrieved_context"]["technical_docs"] = self.retrieve_knowledge(
                query, category="technical", max_results=3
            )
            
        elif agent_name in ["X Dev Writer", "X Creator Writer"]:
            # Retrieve successful social posts
            persona = "developer" if "Dev" in agent_name else "creator"
            context["retrieved_context"]["successful_posts"] = self.retrieve_style_examples(f"x_{persona}")
            context["retrieved_context"]["recent_posts"] = self.retrieve_similar_content(
                query, content_type=f"x_{persona}", max_results=3
            )
            
        elif agent_name == "LinkedIn Writer":
            # Retrieve professional content examples
            context["retrieved_context"]["linkedin_examples"] = self.retrieve_style_examples("linkedin")
            context["retrieved_context"]["enterprise_info"] = self.retrieve_knowledge(
                query, category="enterprise", max_results=2
            )
            
        elif agent_name == "Art Director":
            # Retrieve successful visual themes
            context["retrieved_context"]["visual_themes"] = self.vector_store.search_similar_content(
                query, content_type="image_prompt", n_results=3
            )
            context["retrieved_context"]["brand_assets"] = self.retrieve_knowledge(
                "brand visual guidelines", category="brand", max_results=2
            )
            
        elif agent_name == "Editor":
            # Retrieve style guide and past corrections
            context["retrieved_context"]["style_guide"] = self.retrieve_knowledge(
                "style guide tone voice", category="style", max_results=3
            )
            context["retrieved_context"]["past_edits"] = self.retrieve_similar_content(
                query, content_type="edit", max_results=2
            )
        
        return context
    
    def build_rag_prompt(self, original_prompt: str, context: Dict[str, Any]) -> str:
        """Build an enhanced prompt with retrieved context"""
        enhanced_prompt = original_prompt + "\n\n### Retrieved Context:\n"
        
        # Add similar content context
        if "similar_content" in context:
            enhanced_prompt += "\n**Similar Previous Content:**\n"
            for item in context["similar_content"]["context_items"][:2]:
                enhanced_prompt += f"- {item['content'][:200]}... (similarity: {item['similarity']:.2f})\n"
        
        # Add knowledge context
        if "knowledge" in context:
            enhanced_prompt += "\n**Relevant Knowledge:**\n"
            for item in context["knowledge"]["knowledge_items"][:3]:
                enhanced_prompt += f"- {item['content'][:150]}... (source: {item['source']})\n"
        
        # Add style examples
        if "style_examples" in context:
            enhanced_prompt += "\n**High-Performing Examples:**\n"
            for item in context["style_examples"]["examples"][:2]:
                enhanced_prompt += f"- {item['content'][:150]}... (score: {item['performance_score']:.2f})\n"
        
        enhanced_prompt += "\n### Original Request:\n"
        
        return enhanced_prompt
    
    def store_agent_output(self, agent_name: str, output: str, metadata: Dict[str, Any]) -> str:
        """Store agent output in the appropriate collection"""
        # Determine content type based on agent
        content_type_map = {
            "Planner": "brief",
            "Blog Writer": "blog",
            "X Dev Writer": "x_developer",
            "X Creator Writer": "x_creator",
            "LinkedIn Writer": "linkedin",
            "Art Director": "image_prompt",
            "Image Maker": "image_asset",
            "Editor": "edit"
        }
        
        content_type = content_type_map.get(agent_name, "general")
        
        # Add agent name to metadata
        metadata["agent"] = agent_name
        
        # Store in content history
        doc_id = self.vector_store.add_content(content_type, output, metadata)
        
        return doc_id
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system"""
        stats = self.vector_store.get_stats()
        stats["embedding_cache_size"] = self.embedding_manager.get_cache_size()
        return stats


# Tool functions for agents
def retrieve_context(query: str, agent_name: str) -> Dict[str, Any]:
    """Tool function for agents to retrieve context"""
    retrieval = RetrievalSystem()
    return retrieval.get_agent_context(agent_name, query)

def check_duplicate(content: str) -> Dict[str, Any]:
    """Tool function to check for duplicate content"""
    retrieval = RetrievalSystem()
    return retrieval.check_content_duplicate(content)

def get_style_examples(content_type: str) -> Dict[str, Any]:
    """Tool function to get high-performing style examples"""
    retrieval = RetrievalSystem()
    return retrieval.retrieve_style_examples(content_type)

def search_knowledge(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Tool function to search the knowledge base"""
    retrieval = RetrievalSystem()
    return retrieval.retrieve_knowledge(query, category)