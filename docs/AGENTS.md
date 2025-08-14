# Agent Architecture & Detailed Capabilities

## Overview

The Content Factory uses 8 specialized agents working in orchestrated harmony. Each agent has distinct expertise and leverages ChromaDB for context-aware content generation.

## Agent Workflow

```
Product Input → Planner → Parallel Content Generation → Editor → Output Package
                   ↓
            [Context Retrieval from ChromaDB]
```

## Detailed Agent Descriptions

### 📋 Planner Agent
**Purpose**: Strategic content planning and brief creation

**Capabilities**:
- Analyzes product input to identify key messaging and target audiences
- Creates structured content brief for all downstream agents
- Determines content angles and calls-to-action
- Retrieves similar successful briefs from ChromaDB
- Searches knowledge base for product information

**Tools**: Web search, knowledge retrieval, context search, duplicate check  
**Output**: `ContentBrief` with product details, segments, and strategy

---

### ✍️ Blog Writer Agent
**Purpose**: Technical blog post generation

**Capabilities**:
- Generates comprehensive technical blogs (1500+ words)
- Structures content with SEO-optimized headings
- Includes code examples using the quickstart generator
- Adds latency/cost examples and quality metrics
- Retrieves high-performing blog examples for style guidance
- Searches technical documentation for accuracy

**Tools**: Code quickstart generator, style examples, knowledge search  
**Output**: `BlogArticle` with title, slug, meta description, and markdown body

---

### 💻 X Developer Writer Agent
**Purpose**: Developer-focused Twitter/X content

**Capabilities**:
- Creates up to 5 tweet variants under 280 characters
- Emphasizes technical benefits and features
- Includes documentation/demo links with UTM tracking
- Adds 1-2 relevant technical hashtags
- Checks for duplicate content to ensure originality
- Learns from high-engagement developer tweets

**Tools**: UTM builder, URL shortener, style examples, duplicate checker  
**Output**: `SocialPost` with developer-targeted variants

---

### 🎨 X Creator Writer Agent
**Purpose**: Creator-friendly social content (New in v2)

**Capabilities**:
- Generates hook-first posts for non-technical audiences
- Uses conversational tone with minimal emojis (≤1)
- Focuses on benefits over features
- Structures posts in 1-2 short lines for impact
- Avoids technical jargon
- Retrieves successful creator post examples

**Tools**: UTM builder, URL shortener, style examples, duplicate checker  
**Output**: `SocialPost` with creator-targeted variants

---

### 💼 LinkedIn Writer Agent
**Purpose**: Professional B2B content

**Capabilities**:
- Creates 1-2 LinkedIn post variants for decision makers
- Emphasizes enterprise features (SLA, SSO/SAML, data controls)
- Includes 3-5 strategic hashtags
- Suggests "link in comments" for better reach
- Balances technical depth with business value
- Searches knowledge base for enterprise features

**Tools**: UTM builder, URL shortener, style examples, knowledge search  
**Output**: `SocialPost` with professional variants

---

### 🎨 Art Director Agent
**Purpose**: Visual content strategy (New in v2)

**Capabilities**:
- Proposes 2-3 on-brand image concepts
- Creates detailed prompts for each platform (blog hero, X card, LinkedIn hero)
- Aligns with brand palette and style guidelines
- Specifies aspect ratios and dimensions
- Includes optional seeds for consistency
- Retrieves brand visual guidelines from knowledge base

**Tools**: Knowledge search, context retrieval  
**Output**: List of `ImageAsset` specifications

---

### 🖼️ Image Maker Agent
**Purpose**: Image generation and accessibility (New in v2)

**Capabilities**:
- Interfaces with text-to-image APIs
- Generates images based on Art Director specifications
- Creates accessibility-focused alt text
- Produces platform-specific visuals
- Handles multiple aspect ratios
- Returns complete image assets with URLs

**Tools**: Image generation API, alt text generator  
**Output**: List of `ImageAsset` with URLs and alt text

---

### 📝 Editor Agent
**Purpose**: Quality control and consistency

**Capabilities**:
- Reviews all content for clarity and tone
- Enforces developer vs creator content distinctions
- Flags unsubstantiated benchmark claims
- Removes marketing hype
- Suggests precise edits
- Validates against style guide
- Retrieves past editorial patterns

**Tools**: Knowledge search, context retrieval  
**Output**: Editorial feedback and final approval

## ChromaDB Integration

Each agent leverages ChromaDB for enhanced performance:

### Context Retrieval
- Agents retrieve relevant past content before generation
- Reduces redundancy and maintains consistency
- Provides examples of successful content

### Knowledge Grounding
- Access to product documentation and specifications
- Brand guidelines and style requirements
- Technical accuracy through RAG

### Performance Learning
- High-performing content promoted to style examples
- Agents learn from engagement metrics
- Continuous improvement through feedback loops

## Agent Orchestration

The `controller.py` manages agent execution:

1. **Sequential Steps**:
   - Planner creates brief
   - Content generation (parallel)
   - Visual generation
   - Editorial review
   - Guardrail validation

2. **Parallel Execution**:
   - Blog, X Dev, X Creator, and LinkedIn writers work simultaneously
   - Reduces total generation time

3. **Error Handling**:
   - Retry logic for transient failures
   - Guardrails prevent low-quality output
   - Fallback strategies for API failures

## Extending the System

To add a new agent:

1. Define agent in `agents_setup.py`
2. Create output contract in `content_contracts.py`
3. Add orchestration logic in `controller.py`
4. Configure retrieval strategy in `retrieval.py`
5. Update guardrails if needed

## Performance Metrics

Typical generation times:
- Brief creation: 3-5 seconds
- Parallel content: 10-15 seconds
- Visual generation: 5-10 seconds
- Total package: 20-30 seconds

With ChromaDB caching:
- 30% faster for similar requests
- 50% reduction in API calls for knowledge retrieval