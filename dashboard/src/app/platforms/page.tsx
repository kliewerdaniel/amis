"use client";

import { getPlatformSummaries, getPlatformNames, PLATFORM_COLORS } from "@/lib/data";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function PlatformsPage() {
  const platforms = getPlatformSummaries();
  const names = getPlatformNames();

  const data = names.map((name) => ({
    name,
    avg: Math.round((platforms[name].avg_suitability || 0) * 10) / 10,
    count: platforms[name].total_articles || 0,
    color: PLATFORM_COLORS[name] || "#6B7280",
  })).sort((a, b) => b.avg - a.avg);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Platform Recommendations</h1>

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Average Suitability Score by Platform</h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data} layout="vertical" margin={{ left: 100 }}>
            <XAxis type="number" domain={[0, 100]} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
            <Tooltip />
            <Bar dataKey="avg" fill="#3B82F6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((p) => (
          <a
            key={p.name}
            href={`/platforms/${encodeURIComponent(p.name)}/`}
            className="block bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: p.color }}
              />
              <h3 className="font-medium text-gray-900">{p.name}</h3>
            </div>
            <div className="flex gap-4 text-sm text-gray-500">
              <span>Avg: <strong className="text-gray-800">{p.avg}</strong></span>
              <span>Articles: <strong className="text-gray-800">{p.count}</strong></span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
