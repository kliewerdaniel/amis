"use client";

import { useState } from "react";
import { getArticleSummaries } from "@/lib/data";

export default function ArticlesPage() {
  const articles = getArticleSummaries();
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"title" | "evergreen" | "reading_time">("evergreen");

  const filtered = articles
    .filter((a) => !search || a.title.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === "title") return a.title.localeCompare(b.title);
      if (sortBy === "reading_time") return (b.reading_time_minutes || 0) - (a.reading_time_minutes || 0);
      return (b.scores.evergreen_score || 0) - (a.scores.evergreen_score || 0);
    });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Articles ({articles.length})</h1>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Search articles..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-3 py-1.5 border rounded-lg text-sm w-64"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1.5 border rounded-lg text-sm"
          >
            <option value="evergreen">Evergreen Score</option>
            <option value="title">Title A-Z</option>
            <option value="reading_time">Reading Time</option>
          </select>
        </div>
      </div>

      <div className="space-y-2">
        {filtered.map((a) => (
          <a
            key={a.id}
            href={`/articles/${a.slug}`}
            className="block bg-white rounded-lg border p-4 hover:shadow-sm transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h2 className="font-medium text-gray-900 truncate">{a.title}</h2>
                {a.description && (
                  <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{a.description}</p>
                )}
                <div className="flex gap-3 mt-2">
                  <span className="text-xs text-gray-400">
                    {a.reading_time_minutes || "?"} min · {a.word_count?.toLocaleString() || "?"} words
                  </span>
                  {a.publication_date && (
                    <span className="text-xs text-gray-400">{a.publication_date}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-2 ml-4 shrink-0">
                {a.scores.evergreen_score && (
                  <span className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium">
                    {a.scores.evergreen_score}
                  </span>
                )}
                {a.scores.trust_score && (
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                    Trust: {a.scores.trust_score}
                  </span>
                )}
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
