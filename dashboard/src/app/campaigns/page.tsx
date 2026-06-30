"use client";

import { getCampaigns, getStepsForCampaign, getArticleById } from "@/lib/data";

export default function CampaignsPage() {
  const campaigns = getCampaigns();

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Marketing Campaigns</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {campaigns.map((c) => {
          const steps = getStepsForCampaign(c.id);
          const platforms = c.platforms_json ? JSON.parse(c.platforms_json) : [];
          const schedule = c.publishing_schedule_json ? JSON.parse(c.publishing_schedule_json) : [];
          const metrics = c.success_metrics_json ? JSON.parse(c.success_metrics_json) : [];

          return (
            <a
              key={c.id}
              href={`/campaigns/${c.id}/`}
              className="block bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h2 className="font-semibold text-gray-900">{c.name}</h2>
                  <p className="text-sm text-gray-500 mt-0.5">{c.goal}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  c.status === "draft" ? "bg-yellow-50 text-yellow-700" : "bg-green-50 text-green-700"
                }`}>
                  {c.status}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                {platforms.map((p: string) => (
                  <span key={p} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                    {p}
                  </span>
                ))}
              </div>

              <div className="flex gap-4 text-xs text-gray-500">
                <span>{c.estimated_duration_days || "?"} days</span>
                <span>Reach: {c.estimated_reach?.toLocaleString() || "?"}</span>
                {c.estimated_conversion_rate && (
                  <span>Conv: {(c.estimated_conversion_rate * 100).toFixed(0)}%</span>
                )}
                <span>{steps.length} steps</span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
