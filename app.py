from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
from controller import generate_package, publish_everything
from vector_store import VectorStore
from analytics import PerformanceAnalytics
from retrieval import RetrievalSystem
import os

app = FastAPI(title="Content Factory v2 with ChromaDB")

class GenerateRequest(BaseModel):
    product_input: str
    canonical_url: str | None = None
    schedule_iso: str | None = None

@app.post("/content-package")
async def content_package(req: GenerateRequest):
    try:
        pkg = await generate_package(req.product_input, req.canonical_url)
        result = {"package": pkg.model_dump()}
        if req.schedule_iso:
            result["publish"] = await publish_everything(pkg, req.schedule_iso)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Knowledge Base Management Endpoints

class KnowledgeRequest(BaseModel):
    category: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}

@app.post("/knowledge/add")
async def add_knowledge(req: KnowledgeRequest):
    """Add new knowledge to the knowledge base"""
    try:
        vector_store = VectorStore()
        doc_id = vector_store.add_knowledge(req.category, req.content, req.metadata)
        return {"status": "success", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    max_results: int = 5

@app.post("/knowledge/search")
async def search_knowledge(req: SearchRequest):
    """Search the knowledge base"""
    try:
        retrieval = RetrievalSystem()
        results = retrieval.retrieve_knowledge(req.query, req.category, req.max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Performance Analytics Endpoints

class PerformanceRequest(BaseModel):
    content_id: str
    metrics: Dict[str, Any]

@app.post("/analytics/track")
async def track_performance(req: PerformanceRequest):
    """Track performance metrics for content"""
    try:
        analytics = PerformanceAnalytics()
        metric_id = analytics.track_content_performance(req.content_id, req.metrics)
        return {"status": "success", "metric_id": metric_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/insights")
async def get_insights():
    """Get performance insights and recommendations"""
    try:
        analytics = PerformanceAnalytics()
        insights = analytics.get_learning_insights()
        return insights
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/top-content")
async def get_top_content(content_type: Optional[str] = None, limit: int = 10):
    """Get top performing content"""
    try:
        analytics = PerformanceAnalytics()
        top_content = analytics.get_top_performers(content_type, limit)
        return {"content_type": content_type, "top_performers": top_content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Vector Store Management Endpoints

@app.get("/vector-store/stats")
async def get_vector_stats():
    """Get statistics about the vector store"""
    try:
        vector_store = VectorStore()
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class DuplicateCheckRequest(BaseModel):
    content: str
    threshold: float = 0.95

@app.post("/vector-store/check-duplicate")
async def check_duplicate(req: DuplicateCheckRequest):
    """Check if content is duplicate"""
    try:
        retrieval = RetrievalSystem()
        result = retrieval.check_content_duplicate(req.content, req.threshold)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class StyleExampleRequest(BaseModel):
    content_type: str
    content: str
    performance_score: float
    metadata: Optional[Dict[str, Any]] = {}

@app.post("/vector-store/add-style-example")
async def add_style_example(req: StyleExampleRequest):
    """Add a high-performing content example"""
    try:
        vector_store = VectorStore()
        doc_id = vector_store.add_style_example(
            req.content_type, 
            req.content, 
            req.performance_score, 
            req.metadata
        )
        return {"status": "success", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "vector_store": "enabled", "version": "2.0"}
