"use client";

import { getAudienceSummaries } from "@/lib/data";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function AudiencesPage() {
  const audiences = getAudienceSummaries();

  const data = Object.values(audiences)
    .map((a: any) => ({
      name: a.audience_type.replace(/_/g, " "),
      avg: Math.round((a.avg_relevance || 0) * 10) / 10,
      count: a.total_articles || 0,
    }))
    .sort((a, b) => b.avg - a.avg);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Audience Profiles</h1>

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Average Relevance by Audience Type</h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data} layout="vertical" margin={{ left: 130 }}>
            <XAxis type="number" domain={[0, 100]} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
            <Tooltip />
            <Bar dataKey="avg" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((a) => (
          <a
            key={a.name}
            href={`/audiences/${encodeURIComponent(a.name)}`}
            className="block bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-shadow"
          >
            <h3 className="font-medium text-gray-900 capitalize mb-1">{a.name}</h3>
            <div className="flex gap-4 text-sm text-gray-500">
              <span>Avg: <strong className="text-gray-800">{a.avg}</strong></span>
              <span>Articles: <strong className="text-gray-800">{a.count}</strong></span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
