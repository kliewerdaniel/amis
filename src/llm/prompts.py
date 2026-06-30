_JSON_ONLY = "\n\nRespond with ONLY valid JSON. Do not include any other text."
_JSON_FIRST = "Respond with ONLY valid JSON. Do not include any other text before or after the JSON.\n\n"

SEMANTIC_ANALYSIS_PROMPT = _JSON_FIRST + """You are a marketing intelligence analyst. Analyze the following blog article and provide scores for each dimension below.

Article Title: {title}
Author: {author}
Date: {publication_date}
Tags: {tags}

Article Content:
{content}

For each metric, provide:
1. A score from 0-100
2. A confidence value from 0-1
3. Brief reasoning (1-2 sentences)

Metrics to score: technical_difficulty, business_difficulty, book_relevance, github_relevance, consulting_relevance, evergreen_score, trend_score, marketing_value, educational_value, originality, practicality, authority_score, virality_potential, seo_potential, developer_appeal, executive_appeal, research_appeal, startup_appeal, enterprise_appeal

Respond in valid JSON format:
{{
  "summary": "...",
  "core_thesis": "...",
  "problem_solved": "...",
  "scores": {{
    "technical_difficulty": {{"score": 0, "confidence": 0.0, "reasoning": "..."}},
    ...
  }},
  "primary_audience": "...",
  "secondary_audience": "..."
}}"""

TOPIC_EXTRACTION_PROMPT = _JSON_FIRST + """Extract all topics and concepts from this blog article. Classify each into the appropriate category.

Article Title: {title}
Article Content:
{content}

Return ONLY valid JSON with these exact keys:
{{
  "topics": ["..."],
  "subtopics": ["..."],
  "concepts": ["..."],
  "technologies": ["..."],
  "frameworks": ["..."],
  "languages": ["..."],
  "industries": ["..."],
  "ai_concepts": ["..."],
  "architectural_patterns": ["..."],
  "enterprise_concerns": ["..."],
  "cloud_providers": ["..."],
  "security_topics": ["..."],
  "optimization_topics": ["..."]
}}"""

ENTITY_RECOGNITION_PROMPT = _JSON_FIRST + """Extract all named entities from this blog article. For each entity, provide its name, type, and a brief description.

Article Title: {title}
Article Content:
{content}

Entity types: person, company, book, repository, product, technology, protocol, standard, model, language, library, framework, api, cloud_service, research_paper

Return ONLY valid JSON with these exact keys:
{{
  "entities": [
    {{"name": "...", "type": "person", "description": "..."}}
  ]
}}"""

AUDIENCE_MAPPING_PROMPT = _JSON_FIRST + """Classify this blog article by target audience. For each audience type, provide a relevance score (0-100).

Article Title: {title}
Article Content Summary: {summary}

Return ONLY valid JSON with these exact keys:
{{
  "audiences": {{
    "beginner": {{"score": 45, "reasoning": "..."}},
    "intermediate": {{"score": 80, "reasoning": "..."}},
    "advanced": {{"score": 60, "reasoning": "..."}},
    "developer": {{"score": 90, "reasoning": "..."}},
    "architect": {{"score": 70, "reasoning": "..."}},
    "cto": {{"score": 30, "reasoning": "..."}},
    "engineering_manager": {{"score": 25, "reasoning": "..."}},
    "founder": {{"score": 50, "reasoning": "..."}},
    "consultant": {{"score": 40, "reasoning": "..."}},
    "researcher": {{"score": 35, "reasoning": "..."}},
    "student": {{"score": 55, "reasoning": "..."}},
    "enterprise_buyer": {{"score": 20, "reasoning": "..."}}
  }}
}}"""

PLATFORM_RECOMMENDATION_PROMPT = _JSON_FIRST + """Evaluate this blog article for promotion on {platform}.

Article: {title}
Summary: {summary}
Primary Audience: {primary_audience}
Technical Difficulty: {technical_difficulty}

Platform: {platform}

Return ONLY valid JSON with these exact keys:
{{
  "suitability_score": 0-100,
  "reason": "...",
  "optimal_format": "...",
  "posting_frequency": "...",
  "ideal_cta": "...",
  "audience_match": "...",
  "competition_estimate": "...",
  "expected_roi": "..."
}}"""

CAMPAIGN_GENERATION_PROMPT = _JSON_FIRST + """Based on the following articles and their marketing scores, generate a campaign plan to {goal}.

Top Articles:
{top_articles_json}

Target Audience: {audience}
Available Platforms: {platforms}

Return ONLY valid JSON with these exact keys:
{{
  "name": "...",
  "goal": "...",
  "audience": "...",
  "supporting_articles": [article_ids...],
  "platforms": ["..."],
  "publishing_schedule": [
    {{"day": 1, "platform": "...", "article_id": ..., "action": "..."}}
  ],
  "estimated_duration_days": 30,
  "estimated_reach": 10000,
  "estimated_conversion_rate": 0.02,
  "success_metrics": [
    {{"metric": "email_signups", "target": 500}}
  ],
  "steps": [
    {{"order": 1, "type": "publish", "platform": "...", "content_plan": "..."}}
  ]
}}"""

REPURPOSING_PROMPT = _JSON_FIRST + """Analyze this blog article and recommend content repurposing opportunities.

Article: {title}
Content Summary: {summary}

For each target format, provide suitability score (0-100), transformation notes, and estimated effort (low/medium/high).

Target formats: linkedin_article, technical_thread, newsletter, conference_talk, workshop, podcast_pitch, video_script, github_readme, whitepaper, book_chapter

Return ONLY valid JSON with these exact keys:
{{
  "repurposing": [
    {{"format": "linkedin_article", "suitability_score": 85, "transformation_notes": "...", "estimated_effort": "medium"}}
  ]
}}"""

WEEKLY_REPORT_PROMPT = """Generate a weekly marketing intelligence report based on the following data:

New Articles: {new_articles}
Top Performers: {top_performers}
Active Campaigns: {campaigns_active}
Pending Recommendations: {recommendations_pending}

Write a concise markdown report covering:
1. New content highlights
2. Top performing content
3. Campaign status
4. Action items
5. Recommendations for the upcoming week
"""
