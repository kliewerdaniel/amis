"use client";

import { ArticleSummary, PLATFORM_COLORS } from "@/lib/data";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from "recharts";

export default function ArticleDetailClient({ article }: { article: ArticleSummary }) {
  return (
    <>
      {Object.keys(article.scores).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Marketing Scores</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(article.scores).map(([key, val]) => (
              <div key={key} className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">{val}</div>
                <div className="text-xs text-gray-500 capitalize">{key.replace(/_/g, " ")}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Platform Recommendations</h2>
          {article.platforms.length === 0 ? (
            <p className="text-sm text-gray-400">No platform recommendations</p>
          ) : (
            <div className="space-y-2">
              {article.platforms.slice(0, 8).map((p) => (
                <div key={p.platform} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{p.platform}</span>
                  <span
                    className="font-mono text-xs px-1.5 py-0.5 rounded"
                    style={{
                      backgroundColor: `${PLATFORM_COLORS[p.platform] || "#6B7280"}15`,
                      color: PLATFORM_COLORS[p.platform] || "#6B7280",
                    }}
                  >
                    {p.suitability_score}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Audiences</h2>
          {article.audiences.length === 0 ? (
            <p className="text-sm text-gray-400">No audiences mapped</p>
          ) : (
            <div className="space-y-2">
              {article.audiences.slice(0, 8).map((u) => (
                <div key={u.audience_type} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700 capitalize">{u.audience_type.replace(/_/g, " ")}</span>
                  <span className="font-mono text-xs text-blue-600">{u.relevance_score}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Topics ({article.topics.length})</h2>
          <div className="flex flex-wrap gap-1.5">
            {article.topics.slice(0, 20).map((t) => (
              <span
                key={t.name}
                className={`px-2 py-0.5 rounded-full text-xs ${
                  t.is_primary ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-700"
                }`}
              >
                {t.name}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Entities ({article.entities.length})</h2>
          <div className="flex flex-wrap gap-1.5">
            {article.entities.map((e) => (
              <span
                key={e.name}
                className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full text-xs"
              >
                {e.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {article.platforms.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Platform Details</h2>
          <ResponsiveContainer width="100%" height={Math.max(200, article.platforms.length * 28)}>
            <BarChart
              data={article.platforms.map((p) => ({ name: p.platform, score: p.suitability_score || 0 }))}
              layout="vertical"
              margin={{ left: 100 }}
            >
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
              <Tooltip />
              <Bar dataKey="score" fill="#3B82F6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {article.repurposing.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Content Repurposing</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {article.repurposing.slice(0, 10).map((r) => (
              <div key={r.target_format} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm text-gray-800">
                    {r.target_format.replace(/_/g, " ")}
                  </span>
                  <span className="text-xs font-mono text-green-600">{r.suitability_score}</span>
                </div>
                {r.transformation_notes && (
                  <p className="text-xs text-gray-500 line-clamp-2">{r.transformation_notes}</p>
                )}
                {r.estimated_effort && (
                  <span className="text-xs text-gray-400 mt-1 inline-block">
                    Effort: {r.estimated_effort}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
