"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  getStats, getArticleSummaries, getPlatformSummaries, getAudienceSummaries, getCampaigns,
} from "@/lib/data";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"];

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <div className="text-gray-500 text-xs font-medium uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mt-1">{value.toLocaleString()}</div>
    </div>
  );
}

export default function DashboardPage() {
  const stats = getStats();
  const articles = getArticleSummaries();
  const platforms = getPlatformSummaries();
  const audiences = getAudienceSummaries();
  const campaigns = getCampaigns();

  const platformData = Object.values(platforms).map((p: any) => ({
    name: p.platform,
    avg: Math.round(p.avg_suitability * 10) / 10,
    count: p.total_articles,
  })).sort((a, b) => b.avg - a.avg);

  const audienceData = Object.values(audiences).map((a: any) => ({
    name: a.audience_type,
    avg: Math.round(a.avg_relevance * 10) / 10,
    count: a.total_articles,
  })).sort((a, b) => b.avg - a.avg);

  const metricData = Object.entries(stats.metrics_stats)
    .map(([name, m]: any) => ({ name, avg: Math.round(m.avg * 10) / 10 }))
    .sort((a, b) => b.avg - a.avg);

  const topArticles = articles
    .filter((a) => a.scores.evergreen_score)
    .sort((a, b) => (b.scores.evergreen_score || 0) - (a.scores.evergreen_score || 0))
    .slice(0, 10);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Marketing Intelligence Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-8">
        <StatCard label="Articles" value={stats.total_articles} />
        <StatCard label="Platform Recs" value={stats.total_platform_recs} />
        <StatCard label="Audiences" value={stats.total_audiences} />
        <StatCard label="Topics" value={stats.total_topics} />
        <StatCard label="Entities" value={stats.total_entities} />
        <StatCard label="Relationships" value={stats.total_relationships} />
        <StatCard label="Campaigns" value={stats.total_campaigns} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Platform Suitability (avg)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={platformData} layout="vertical" margin={{ left: 80 }}>
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
              <Tooltip />
              <Bar dataKey="avg" fill="#3B82F6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Top Marketing Metrics</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={metricData} margin={{ left: 20, bottom: 60 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={60} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="avg" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Platform Recommendations by Count</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={platformData}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ name, percent }: any) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
              >
                {platformData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Top 10 Articles (Evergreen Score)</h2>
          <div className="space-y-1.5">
            {topArticles.map((a, i) => (
              <a
                key={a.id}
                href={`/articles/${a.slug}`}
                className="flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-50 text-sm"
              >
                <span className="truncate text-gray-800 flex-1">
                  <span className="text-gray-400 mr-2">#{i + 1}</span>
                  {a.title}
                </span>
                <span className="text-blue-600 font-mono text-xs ml-2">{a.scores.evergreen_score}</span>
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Campaigns</h2>
          <div className="space-y-2">
            {campaigns.map((c) => (
              <a
                key={c.id}
                href={`/campaigns/${c.id}`}
                className="block px-3 py-2 rounded-lg border hover:bg-gray-50"
              >
                <div className="font-medium text-sm text-gray-900">{c.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{c.goal}</div>
              </a>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Top Topics</h2>
          <div className="flex flex-wrap gap-1.5">
            {stats.top_topics.slice(0, 40).map((t: any) => (
              <span
                key={t.name}
                className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs"
              >
                {t.name} ({t.count})
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
