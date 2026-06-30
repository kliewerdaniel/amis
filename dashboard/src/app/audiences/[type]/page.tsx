import { notFound } from "next/navigation";
import { getAudienceSummaries } from "@/lib/data";

export function generateStaticParams() {
  const summaries = getAudienceSummaries();
  return Object.keys(summaries).map((type) => ({ type }));
}

export default function AudienceDetailPage({ params }: { params: { type: string } }) {
  const summaries = getAudienceSummaries();
  const audience = Object.values(summaries).find(
    (a: any) => a.audience_type === params.type
  );
  if (!audience) notFound();

  const aud = audience as any;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <a href="/audiences" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Audiences
      </a>

      <h1 className="text-2xl font-bold text-gray-900 mb-2 capitalize">
        {aud.audience_type.replace(/_/g, " ")}
      </h1>
      <div className="flex gap-4 text-sm text-gray-500 mb-6">
        <span>Avg Relevance: <strong>{Math.round(aud.avg_relevance * 10) / 10}</strong></span>
        <span>Articles: <strong>{aud.total_articles}</strong></span>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Mapped Articles</h2>
        <div className="space-y-2">
          {aud.top_articles.map((a: any) => (
            <a
              key={a.article_id}
              href={`/articles/${a.slug}`}
              className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50"
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">{a.title}</div>
                {a.reasoning && (
                  <p className="text-xs text-gray-500 truncate mt-0.5">{a.reasoning}</p>
                )}
              </div>
              <span className="text-purple-600 font-mono text-sm ml-3 shrink-0">
                {a.relevance_score}
              </span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
