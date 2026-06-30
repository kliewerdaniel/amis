"use client";

import { useState } from "react";
import { getTopics, getStats } from "@/lib/data";

export default function TopicsPage() {
  const topics = getTopics();
  const stats = getStats();
  const [search, setSearch] = useState("");

  const topTopicNames = new Set(stats.top_topics.map((t: any) => t.name));
  const filtered = topics
    .filter((t: any) => !search || t.name.toLowerCase().includes(search.toLowerCase()))
    .filter((t: any) => topTopicNames.has(t.name) || search)
    .sort((a: any, b: any) => {
      const aCount = stats.top_topics.find((t: any) => t.name === a.name)?.count || 0;
      const bCount = stats.top_topics.find((t: any) => t.name === b.name)?.count || 0;
      return bCount - aCount;
    });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Topics ({stats.top_topics.length} active of {stats.total_topics} total)
        </h1>
        <input
          type="text"
          placeholder="Search topics..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 border rounded-lg text-sm w-64"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {filtered.map((t: any) => {
          const count = stats.top_topics.find((s: any) => s.name === t.name)?.count || 0;
          const size = Math.min(1 + count * 0.15, 3);
          return (
            <span
              key={t.id}
              className="inline-block px-3 py-1.5 rounded-full text-sm transition-colors hover:bg-blue-100"
              style={{
                fontSize: `${0.75 + size * 0.15}rem`,
                backgroundColor: count > 10 ? "#DBEAFE" : count > 5 ? "#F3F4F6" : "#F9FAFB",
                color: count > 10 ? "#1D4ED8" : count > 5 ? "#374151" : "#6B7280",
              }}
            >
              {t.name}
              <span className="ml-1.5 opacity-60">{count}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
