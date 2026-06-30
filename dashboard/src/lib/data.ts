import articleSummaries from "../../data/article_summaries.json";
import platformSummaries from "../../data/platform_summaries.json";
import audienceSummaries from "../../data/audience_summaries.json";
import stats from "../../data/stats.json";
import campaignsData from "../../data/campaigns.json";
import campaignSteps from "../../data/campaign_steps.json";
import knowledgeGraph from "../../data/knowledge_graph.json";
import topics from "../../data/topics.json";
import entities from "../../data/entities.json";
import articles from "../../data/articles.json";

export type ArticleSummary = {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  publication_date: string | null;
  word_count: number | null;
  reading_time_minutes: number | null;
  scores: Record<string, number>;
  platforms: {
    platform: string;
    suitability_score: number | null;
    optimal_format: string | null;
    posting_frequency: string | null;
    reason: string | null;
  }[];
  audiences: {
    audience_type: string;
    relevance_score: number | null;
    reasoning: string | null;
  }[];
  topics: { name: string; relevance_score: number | null; is_primary: boolean | null }[];
  entities: { name: string; entity_type: string }[];
  repurposing: {
    target_format: string;
    suitability_score: number | null;
    transformation_notes: string | null;
    estimated_effort: string | null;
  }[];
};

export type Campaign = {
  id: number;
  name: string;
  goal: string;
  audience: string | null;
  platforms_json: string | null;
  publishing_schedule_json: string | null;
  success_metrics_json: string | null;
  status: string;
  estimated_duration_days: number | null;
  estimated_reach: number | null;
  estimated_conversion_rate: number | null;
};

export type CampaignStep = {
  id: number;
  campaign_id: number;
  step_order: number;
  step_type: string;
  platform: string | null;
  article_id: number | null;
  content_plan: string | null;
  scheduled_date: string | null;
  status: string | null;
};

export type GraphNode = { id: string; label: string; type: string };
export type GraphLink = { source: string; target: string; type: string; weight: number | null };

export function getArticleSummaries(): ArticleSummary[] {
  return articleSummaries as unknown as ArticleSummary[];
}

export function getArticleBySlug(slug: string): ArticleSummary | undefined {
  return (articleSummaries as unknown as ArticleSummary[]).find((a) => a.slug === slug);
}

export function getArticleById(id: number): ArticleSummary | undefined {
  return (articleSummaries as unknown as ArticleSummary[]).find((a) => a.id === id);
}

export function getPlatformSummaries() {
  return platformSummaries as unknown as Record<string, any>;
}

export function getPlatformNames(): string[] {
  return Object.keys(platformSummaries as unknown as Record<string, any>).sort();
}

export function getAudienceSummaries() {
  return audienceSummaries as unknown as Record<string, any>;
}

export function getStats() {
  return stats as unknown as any;
}

export function getCampaigns(): Campaign[] {
  return campaignsData as unknown as Campaign[];
}

export function getCampaignById(id: number): Campaign | undefined {
  return (campaignsData as unknown as Campaign[]).find((c) => c.id === id);
}

export function getStepsForCampaign(campaignId: number): CampaignStep[] {
  return (campaignSteps as unknown as CampaignStep[])
    .filter((s) => s.campaign_id === campaignId)
    .sort((a, b) => a.step_order - b.step_order);
}

export function getKnowledgeGraph() {
  return knowledgeGraph as unknown as { nodes: GraphNode[]; links: GraphLink[] };
}

export function getTopics() {
  return topics as unknown as any[];
}

export function getEntities() {
  return entities as unknown as any[];
}

export const PLATFORM_COLORS: Record<string, string> = {
  LinkedIn: "#0A66C2",
  X: "#1DA1F2",
  "Dev.to": "#0A0A0A",
  Hashnode: "#2962FF",
  Medium: "#000000",
  "Hacker News": "#FF6600",
  GitHub: "#181717",
  "Personal Blog": "#6B7280",
  "Email Newsletter": "#EA4335",
  YouTube: "#FF0000",
  "Conference CFP": "#8B5CF6",
  "Podcast Pitch": "#EC4899",
};
