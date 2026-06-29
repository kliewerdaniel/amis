SovereignSpec

Project: Agentic Marketing Intelligence System (AMIS)

Vision

Build an autonomous marketing intelligence platform that ingests a corpus of Markdown blog posts and transforms them into a continuously improving marketing knowledge graph capable of planning, ranking, recommending, and generating marketing campaigns for a technical book and related engineering work.

This is not a social media post generator.

This system is a reasoning engine that understands relationships between articles, products, repositories, audiences, and marketing channels.

⸻

Objectives

The system shall:

* Parse an arbitrary directory of Markdown documents.
* Build a searchable semantic database.
* Build a knowledge graph between all content.
* Score every document for multiple marketing dimensions.
* Recommend which articles should be promoted.
* Recommend where they should be promoted.
* Recommend how they should be promoted.
* Generate campaign plans.
* Persist all reasoning for future autonomous agents.
* Support future reinforcement from analytics.

⸻

Guiding Principles

* Local-first architecture.
* Markdown is the canonical source of truth.
* SQLite for structured persistence.
* ChromaDB for semantic retrieval.
* Graph relationships stored separately.
* Deterministic ingestion pipeline.
* LLM only used where reasoning is required.
* Every inference stored.
* Idempotent ingestion.

⸻

Directory Layout

content/
    posts/
        *.md
database/
    sqlite.db
chroma/
graph/
campaigns/
analytics/
generated/
configs/
logs/

⸻

Phase 1

Markdown Ingestion

Read every markdown file.

Extract

* filename
* slug
* title
* frontmatter
* publication date
* categories
* tags
* headings
* images
* links
* code blocks
* references
* word count
* reading time

Store normalized document.

⸻

Phase 2

Semantic Analysis

For every article determine

Summary

Core Thesis

Problem Solved

Primary Audience

Secondary Audience

Technical Difficulty

Business Difficulty

Book Relevance

GitHub Relevance

Consulting Relevance

Evergreen Score

Trend Score

Marketing Value

Educational Value

Originality

Practicality

Authority Score

Virality Potential

SEO Potential

Developer Appeal

Executive Appeal

Research Appeal

Startup Appeal

Enterprise Appeal

Confidence

Each metric

0-100

Persist all scores.

⸻

Phase 3

Topic Extraction

Extract

Topics

Subtopics

Concepts

Technologies

Frameworks

Languages

Industries

AI Concepts

Architectural Patterns

Enterprise Concerns

Cloud Providers

Security Topics

Optimization Topics

Store normalized taxonomy.

⸻

Phase 4

Entity Recognition

Detect

People

Companies

Books

Repositories

Products

Technologies

Protocols

Standards

Models

Programming Languages

Libraries

Frameworks

APIs

Cloud Services

Research Papers

Store relationships.

⸻

Phase 5

Knowledge Graph

Create graph nodes

Article

Book Chapter

Repository

Technology

Audience

Campaign

Platform

Topic

Entity

Product

Create edges

references

expands

contradicts

depends_on

introduces

explains

updates

duplicates

supports

markets

implements

mentions

recommended_after

recommended_before

related_to

derived_from

visualizes

Edge weights

0-1

Persist graph.

⸻

Phase 6

Duplicate Detection

Find

Duplicate articles

Near duplicate ideas

Outdated content

Articles superseded by newer work

Missing follow-up articles

Unfinished article series

Recommend consolidation.

⸻

Phase 7

Marketing Ranking

Compute

Marketing Score

Authority Score

Trust Score

Book Conversion Score

SEO Score

Evergreen Score

Shareability

Conference Potential

Podcast Potential

Newsletter Potential

Developer Community Potential

Enterprise Decision Maker Potential

Create overall ranking.

⸻

Phase 8

Audience Mapping

Determine

Beginner

Intermediate

Advanced

Developer

Architect

CTO

Engineering Manager

Founder

Consultant

Researcher

Student

Enterprise Buyer

Map every article.

⸻

Phase 9

Platform Recommendation

Supported Platforms

LinkedIn

X

Dev.to

Hashnode

Medium

Hacker News

GitHub

Personal Blog

Email Newsletter

YouTube

Conference CFP

Podcast Pitch

For every article produce

Suitability Score

Reason

Optimal Format

Posting Frequency

Ideal CTA

Audience Match

Competition Estimate

Expected ROI

⸻

Phase 10

Campaign Planner

Generate reusable campaigns.

Campaign object

Goal
Audience
Book Chapters
Supporting Articles
Repositories
Landing Page
Call To Action
Platforms
Publishing Schedule
Estimated Duration
Estimated Reach
Estimated Conversion
Dependencies
Success Metrics

Campaigns stored independently.

⸻

Phase 11

Content Repurposing

Identify

Articles that become

LinkedIn article

Technical thread

Newsletter

Conference talk

Workshop

Podcast pitch

Video script

GitHub README

Whitepaper

Book chapter

Create transformation recommendations.

⸻

Phase 12

Marketing Memory

Persist every recommendation.

Never regenerate identical reasoning.

Every recommendation receives

Timestamp

Reasoning

Confidence

Related content

Outcome

Future agents use prior reasoning.

⸻

Phase 13

Analytics Schema

Future support only.

Tables

Views

Clicks

Shares

Comments

CTR

Conversions

Book Sales

Email Signups

Repository Stars

Downloads

Time on Page

Bounce Rate

Campaign Effectiveness

Currently allow manual import.

⸻

Phase 14

Recommendation Engine

Queries

Best article to promote today

Best article for LinkedIn

Best article for executives

Best article to sell the book

Most evergreen article

Highest authority article

Most underutilized article

Best hidden gem

Best follow-up article

Article needing update

Highest ROI campaign

Generate ranked results.

⸻

Phase 15

Agent Interface

Expose structured tools.

Examples

find_best_articles()
generate_campaign(goal)
recommend_platform(article)
rank_articles()
find_hidden_gems()
find_duplicate_content()
find_missing_topics()
recommend_book_marketing()
recommend_consulting_content()
generate_monthly_plan()

Agents consume APIs.

No UI assumptions.

⸻

Phase 16

Future Autonomous Loop

Nightly

Ingest new markdown.

Recompute graph.

Detect changes.

Update scores.

Suggest campaigns.

Generate weekly report.

Recommend highest ROI actions.

Never overwrite historical reasoning.

Everything versioned.

⸻

SQLite Schema (Minimum)

Articles

Topics

Entities

Relationships

Campaigns

CampaignSteps

PlatformRecommendations

AudienceProfiles

Scores

Recommendations

Analytics

ReasoningHistory

BookMappings

RepositoryMappings

ArticleEmbeddings

⸻

Success Criteria

Given a directory of Markdown files, the system shall autonomously:

* Build a semantic understanding of the corpus.
* Construct a marketing knowledge graph.
* Rank every article by multiple marketing dimensions.
* Recommend optimal promotion strategies.
* Identify hidden opportunities.
* Generate reusable campaign plans.
* Persist all reasoning for future autonomous agents.
* Operate incrementally as new content is added.
* Serve as the intelligence layer for future agentic marketing workflows rather than as a simple content generator.