import { notFound } from "next/navigation";
import { getCampaigns, getCampaignById, getStepsForCampaign, getArticleById } from "@/lib/data";

export function generateStaticParams() {
  return getCampaigns().map((c) => ({ id: String(c.id) }));
}

export default function CampaignDetailPage({ params }: { params: { id: string } }) {
  const id = parseInt(params.id);
  const campaign = getCampaignById(id);
  if (!campaign) notFound();

  const steps = getStepsForCampaign(id);
  const platforms = campaign.platforms_json ? JSON.parse(campaign.platforms_json) : [];
  const schedule = campaign.publishing_schedule_json ? JSON.parse(campaign.publishing_schedule_json) : [];
  const metrics = campaign.success_metrics_json ? JSON.parse(campaign.success_metrics_json) : [];
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <a href="/campaigns" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Campaigns
      </a>

      <div className="flex items-start justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
          <p className="text-gray-600 mt-1">{campaign.goal}</p>
        </div>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
          campaign.status === "draft" ? "bg-yellow-50 text-yellow-700" : "bg-green-50 text-green-700"
        }`}>
          {campaign.status}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border p-4 text-center">
          <div className="text-lg font-bold text-gray-900">{campaign.estimated_duration_days || "?"}</div>
          <div className="text-xs text-gray-500">Duration (days)</div>
        </div>
        <div className="bg-white rounded-xl border p-4 text-center">
          <div className="text-lg font-bold text-gray-900">
            {campaign.estimated_reach?.toLocaleString() || "?"}
          </div>
          <div className="text-xs text-gray-500">Estimated Reach</div>
        </div>
        <div className="bg-white rounded-xl border p-4 text-center">
          <div className="text-lg font-bold text-gray-900">
            {campaign.estimated_conversion_rate
              ? `${(campaign.estimated_conversion_rate * 100).toFixed(0)}%`
              : "?"}
          </div>
          <div className="text-xs text-gray-500">Conversion Rate</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Platforms</h2>
          <div className="flex flex-wrap gap-2">
            {platforms.map((p: string) => (
              <a
                key={p}
                href={`/platforms/${encodeURIComponent(p)}`}
                className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100"
              >
                {p}
              </a>
            ))}
          </div>
        </div>

        {metrics.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Success Metrics</h2>
            <div className="space-y-2">
              {metrics.map((m: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{m.metric || m.target}</span>
                  <span className="font-mono text-green-600">{m.target}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Publishing Schedule</h2>
        {schedule.length === 0 ? (
          <p className="text-sm text-gray-400">No schedule defined</p>
        ) : (
          <div className="space-y-2">
            {schedule.map((s: any, i: number) => {
              const article = getArticleById(s.article_id);
              return (
                <div key={i} className="flex items-center gap-4 px-3 py-2 bg-gray-50 rounded-lg">
                  <span className="text-xs font-mono text-gray-500 w-12">
                    Day {s.day}
                  </span>
                  <span className="text-xs font-medium text-gray-700 w-24">{s.platform}</span>
                  <span className="text-xs text-gray-500 flex-1">
                    {s.action}{article ? `: ${article.title}` : ""}
                  </span>
                  {article && (
                    <a
                      href={`/articles/${article.slug}`}
                      className="text-xs text-blue-600 hover:underline shrink-0"
                    >
                      View
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {steps.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Campaign Steps</h2>
          <div className="space-y-2">
            {steps.map((s) => {
              const article = s.article_id ? getArticleById(s.article_id) : null;
              return (
                <div key={s.id} className="flex items-start gap-4 px-3 py-2 rounded-lg hover:bg-gray-50">
                  <span className="text-xs font-mono text-gray-400 w-6 mt-0.5">
                    {s.step_order}.
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium px-1.5 py-0.5 bg-gray-100 rounded">
                        {s.step_type}
                      </span>
                      {s.platform && (
                        <span className="text-xs text-gray-600">{s.platform}</span>
                      )}
                    </div>
                    {s.content_plan && (
                      <p className="text-xs text-gray-500 mt-1">{s.content_plan}</p>
                    )}
                    {article && (
                      <a
                        href={`/articles/${article.slug}`}
                        className="text-xs text-blue-600 hover:underline mt-1 inline-block"
                      >
                        {article.title}
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
