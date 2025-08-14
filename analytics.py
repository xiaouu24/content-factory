from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from vector_store import VectorStore
from embeddings import EmbeddingManager
import json

class PerformanceAnalytics:
    """Track and analyze content performance for continuous improvement"""
    
    def __init__(self):
        """Initialize analytics system"""
        self.vector_store = VectorStore()
        self.embedding_manager = EmbeddingManager()
    
    def track_content_performance(self, content_id: str, metrics: Dict[str, Any]) -> str:
        """Track performance metrics for generated content"""
        # Standard metrics structure
        performance_data = {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "engagement": metrics.get("engagement", {}),
            "reach": metrics.get("reach", 0),
            "conversions": metrics.get("conversions", 0),
            "sentiment": metrics.get("sentiment", "neutral"),
            "feedback": metrics.get("feedback", []),
            "performance_score": self._calculate_performance_score(metrics)
        }
        
        # Store in vector store
        metric_id = self.vector_store.add_performance_metric(content_id, performance_data)
        
        # If high-performing, add to style examples
        if performance_data["performance_score"] >= 0.8:
            self._promote_to_style_example(content_id, performance_data)
        
        return metric_id
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate normalized performance score (0-1)"""
        score = 0.0
        weights = {
            "engagement_rate": 0.3,
            "reach": 0.2,
            "conversions": 0.3,
            "sentiment": 0.2
        }
        
        # Engagement rate (likes + comments + shares / reach)
        if metrics.get("reach", 0) > 0:
            engagement = metrics.get("engagement", {})
            total_engagement = (
                engagement.get("likes", 0) +
                engagement.get("comments", 0) * 2 +  # Comments weighted higher
                engagement.get("shares", 0) * 3  # Shares weighted highest
            )
            engagement_rate = min(total_engagement / metrics["reach"], 1.0)
            score += engagement_rate * weights["engagement_rate"]
        
        # Reach (normalized, assuming 10k+ is excellent)
        reach_score = min(metrics.get("reach", 0) / 10000, 1.0)
        score += reach_score * weights["reach"]
        
        # Conversions (normalized, assuming 100+ is excellent)
        conversion_score = min(metrics.get("conversions", 0) / 100, 1.0)
        score += conversion_score * weights["conversions"]
        
        # Sentiment
        sentiment_scores = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
        sentiment_score = sentiment_scores.get(metrics.get("sentiment", "neutral"), 0.5)
        score += sentiment_score * weights["sentiment"]
        
        return round(score, 2)
    
    def _promote_to_style_example(self, content_id: str, performance_data: Dict[str, Any]):
        """Promote high-performing content to style examples"""
        # Retrieve the original content
        results = self.vector_store.content_history.get(ids=[content_id])
        
        if results and results.get("documents"):
            content = results["documents"][0]
            metadata = results["metadatas"][0] if results.get("metadatas") else {}
            
            # Add to style examples
            self.vector_store.add_style_example(
                content_type=metadata.get("content_type", "general"),
                content=content,
                performance_score=performance_data["performance_score"],
                metadata={
                    "original_id": content_id,
                    "metrics": performance_data,
                    "promoted_at": datetime.now().isoformat()
                }
            )
    
    def get_content_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for specific content"""
        performance_data = self.vector_store.get_content_performance(content_id)
        
        if not performance_data["documents"]:
            return {"content_id": content_id, "status": "no_data"}
        
        # Aggregate metrics over time
        metrics_over_time = []
        total_reach = 0
        total_conversions = 0
        
        for i, doc in enumerate(performance_data["documents"]):
            metric = json.loads(doc) if isinstance(doc, str) else doc
            metrics_over_time.append({
                "timestamp": metric.get("timestamp"),
                "performance_score": metric.get("performance_score"),
                "reach": metric.get("reach"),
                "conversions": metric.get("conversions")
            })
            total_reach += metric.get("reach", 0)
            total_conversions += metric.get("conversions", 0)
        
        return {
            "content_id": content_id,
            "metrics_count": len(metrics_over_time),
            "metrics_over_time": metrics_over_time,
            "total_reach": total_reach,
            "total_conversions": total_conversions,
            "average_performance": sum(m["performance_score"] for m in metrics_over_time) / len(metrics_over_time)
        }
    
    def get_top_performers(self, content_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content"""
        # Query style examples (which are high performers)
        results = self.vector_store.style_examples.get(
            where={"content_type": content_type} if content_type else None,
            limit=limit
        )
        
        top_performers = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results.get("metadatas") else {}
                top_performers.append({
                    "content": doc[:200] + "..." if len(doc) > 200 else doc,
                    "content_type": metadata.get("content_type"),
                    "performance_score": metadata.get("performance_score"),
                    "timestamp": metadata.get("timestamp")
                })
        
        # Sort by performance score
        top_performers.sort(key=lambda x: x.get("performance_score", 0), reverse=True)
        
        return top_performers[:limit]
    
    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze content performance trends over time"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get recent content
        results = self.vector_store.content_history.get(
            where={"timestamp": {"$gte": cutoff_date}},
            limit=1000
        )
        
        trends = {
            "period_days": days,
            "total_content_created": 0,
            "content_by_type": {},
            "average_performance_by_type": {},
            "trending_topics": []
        }
        
        if results and results.get("documents"):
            trends["total_content_created"] = len(results["documents"])
            
            # Analyze by content type
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results.get("metadatas") else {}
                content_type = metadata.get("content_type", "unknown")
                
                if content_type not in trends["content_by_type"]:
                    trends["content_by_type"][content_type] = 0
                trends["content_by_type"][content_type] += 1
            
            # TODO: Add topic extraction and trending analysis
            
        return trends
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights for continuous improvement"""
        insights = {
            "high_performing_patterns": [],
            "improvement_areas": [],
            "recommendations": []
        }
        
        # Analyze high performers
        top_performers = self.get_top_performers(limit=5)
        for performer in top_performers:
            insights["high_performing_patterns"].append({
                "pattern": f"{performer['content_type']} with score {performer['performance_score']}",
                "example": performer["content"][:100] + "..."
            })
        
        # Get overall statistics
        stats = self.vector_store.get_stats()
        
        # Generate recommendations
        if stats["style_examples"] < 10:
            insights["recommendations"].append(
                "Collect more performance data to build better style examples"
            )
        
        if stats["knowledge_base"] < 20:
            insights["recommendations"].append(
                "Expand knowledge base with more product documentation"
            )
        
        # Identify improvement areas
        low_performers = self._get_low_performers()
        if low_performers:
            insights["improvement_areas"] = [
                f"Content type '{lp['content_type']}' showing lower performance"
                for lp in low_performers[:3]
            ]
        
        return insights
    
    def _get_low_performers(self) -> List[Dict[str, Any]]:
        """Identify content with low performance"""
        # This would query performance metrics for low scores
        # For now, return empty list as placeholder
        return []
    
    def export_analytics_report(self) -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        return {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.vector_store.get_stats(),
            "trends": self.analyze_trends(),
            "top_performers": self.get_top_performers(),
            "insights": self.get_learning_insights()
        }


# Tool functions for tracking
def track_performance(content_id: str, metrics: Dict[str, Any]) -> str:
    """Tool function to track content performance"""
    analytics = PerformanceAnalytics()
    return analytics.track_content_performance(content_id, metrics)

def get_performance_insights() -> Dict[str, Any]:
    """Tool function to get performance insights"""
    analytics = PerformanceAnalytics()
    return analytics.get_learning_insights()

def get_top_content(content_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Tool function to get top performing content"""
    analytics = PerformanceAnalytics()
    return analytics.get_top_performers(content_type)