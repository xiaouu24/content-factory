#!/usr/bin/env python3
"""
Initialize ChromaDB collections with sample data and knowledge base
Run this script to set up the vector store with initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_store import VectorStore
from embeddings import EmbeddingManager
from datetime import datetime
import json

def initialize_vector_store():
    """Initialize ChromaDB with collections and sample data"""
    print("Initializing ChromaDB vector store...")
    
    # Initialize vector store
    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    
    print(f"✓ Created collections: {list(vector_store.get_stats().keys())}")
    
    # Add sample knowledge base content
    print("\nAdding knowledge base content...")
    
    # Product documentation
    knowledge_items = [
        {
            "category": "product",
            "content": "Seedance 1.0 is a state-of-the-art text-to-video API that generates high-quality videos from text prompts. It supports multiple aspect ratios, frame rates, and durations up to 10 seconds. The API uses advanced diffusion models for photorealistic output.",
            "metadata": {"source": "product_docs", "version": "1.0"}
        },
        {
            "category": "technical",
            "content": "API Endpoints: POST /v1/videos/generations for text-to-video, POST /v1/videos/edits for video editing. Authentication via Bearer token. Rate limits: 100 requests/minute for standard tier, 1000 requests/minute for enterprise.",
            "metadata": {"source": "api_reference", "endpoint": "/v1/videos"}
        },
        {
            "category": "enterprise",
            "content": "Enterprise features include: SSO/SAML integration, dedicated support with SLA, VPC peering for secure connections, custom model fine-tuning, volume discounts, and compliance certifications (SOC 2, GDPR).",
            "metadata": {"source": "enterprise_guide", "tier": "enterprise"}
        },
        {
            "category": "pricing",
            "content": "Pricing tiers: Free tier includes 100 credits/month. Pro tier at $99/month includes 10,000 credits. Enterprise tier with custom pricing, unlimited credits, and priority support.",
            "metadata": {"source": "pricing_page", "updated": "2024-01"}
        },
        {
            "category": "style",
            "content": "Brand voice guidelines: Use clear, technical language for developers. Avoid hype and unsubstantiated claims. Focus on concrete benefits and real use cases. Maintain professional tone with enterprise clients.",
            "metadata": {"source": "style_guide", "audience": "all"}
        },
        {
            "category": "brand",
            "content": "Visual brand guidelines: Primary colors #101418 (dark), #1C64F2 (blue), #22C55E (green). Use clean, modern imagery with soft gradients. Avoid cluttered designs. Logo placement in top-right with 12px safe area.",
            "metadata": {"source": "brand_guide", "type": "visual"}
        }
    ]
    
    for item in knowledge_items:
        doc_id = vector_store.add_knowledge(
            category=item["category"],
            content=item["content"],
            metadata=item["metadata"]
        )
        print(f"  Added {item['category']} knowledge: {doc_id[:20]}...")
    
    # Add sample high-performing content as style examples
    print("\nAdding style examples...")
    
    style_examples = [
        {
            "content_type": "blog",
            "content": "# Revolutionizing Video Creation with Seedance API\n\nIn today's content-driven world, the ability to generate high-quality videos programmatically is becoming essential. Seedance 1.0 introduces a breakthrough in text-to-video generation...",
            "performance_score": 0.92,
            "metadata": {"views": 15000, "engagement_rate": 0.08}
        },
        {
            "content_type": "x_developer",
            "content": "🚀 Just shipped Seedance 1.0 - text-to-video API that actually works!\n\n✨ 10-second videos\n🎬 Multiple aspect ratios\n⚡ <30s generation time\n\nDocs: seedance.ai/docs\n\n#AI #VideoGeneration #API",
            "performance_score": 0.85,
            "metadata": {"likes": 234, "retweets": 89}
        },
        {
            "content_type": "x_creator",
            "content": "Turn your ideas into videos with just text 🎥\n\nNo editing skills needed → seedance.ai",
            "performance_score": 0.88,
            "metadata": {"likes": 567, "comments": 45}
        },
        {
            "content_type": "linkedin",
            "content": "Excited to announce Seedance 1.0 - our enterprise-ready text-to-video API.\n\nKey features for businesses:\n• SOC 2 compliant\n• SSO/SAML integration\n• Dedicated support with SLA\n• Custom model fine-tuning\n\nPerfect for scaling content creation while maintaining brand consistency.\n\n#EnterpriseAI #VideoTechnology #ContentAutomation",
            "performance_score": 0.83,
            "metadata": {"views": 8900, "clicks": 234}
        }
    ]
    
    for example in style_examples:
        doc_id = vector_store.add_style_example(
            content_type=example["content_type"],
            content=example["content"],
            performance_score=example["performance_score"],
            metadata=example["metadata"]
        )
        print(f"  Added {example['content_type']} example: {doc_id[:20]}...")
    
    # Add sample content history
    print("\nAdding sample content history...")
    
    content_history = [
        {
            "content_type": "brief",
            "content": json.dumps({
                "product_name": "Seedance 1.0",
                "objective": "Launch announcement",
                "target_segments": ["developers", "creators"],
                "key_points": ["Easy integration", "High quality", "Fast generation"]
            }),
            "metadata": {"campaign": "launch", "date": "2024-01-15"}
        },
        {
            "content_type": "blog",
            "content": "# Getting Started with Seedance API\n\nThis tutorial will walk you through your first text-to-video generation...",
            "metadata": {"word_count": 1523, "read_time": "6 min"}
        }
    ]
    
    for content in content_history:
        doc_id = vector_store.add_content(
            content_type=content["content_type"],
            content=content["content"],
            metadata=content["metadata"]
        )
        print(f"  Added {content['content_type']} to history: {doc_id[:20]}...")
    
    # Display final statistics
    print("\n" + "="*50)
    print("ChromaDB Initialization Complete!")
    print("="*50)
    
    stats = vector_store.get_stats()
    print("\nCollection Statistics:")
    for collection, count in stats.items():
        print(f"  {collection}: {count} documents")
    
    print("\n✅ Vector store is ready for use!")
    print("You can now run the Content Factory with ChromaDB integration enabled.")

def reset_vector_store():
    """Reset all collections (use with caution)"""
    response = input("⚠️  This will delete all data in ChromaDB. Are you sure? (yes/no): ")
    if response.lower() == "yes":
        vector_store = VectorStore()
        for collection in ["content_history", "knowledge_base", "style_examples", "brand_assets", "performance_metrics"]:
            vector_store.clear_collection(collection)
        print("✓ All collections cleared")
    else:
        print("Reset cancelled")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize ChromaDB for Content Factory")
    parser.add_argument("--reset", action="store_true", help="Reset all collections before initializing")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_vector_store()
    
    initialize_vector_store()