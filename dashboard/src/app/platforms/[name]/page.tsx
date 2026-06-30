import { notFound } from "next/navigation";
import { getPlatformSummaries, getPlatformNames } from "@/lib/data";

export function generateStaticParams() {
  return getPlatformNames().map((name) => ({ name }));
}

export default function PlatformDetailPage({ params }: { params: { name: string } }) {
  const platforms = getPlatformSummaries();
  const platform = platforms[params.name];
  if (!platform) notFound();

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <a href="/platforms" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Platforms
      </a>

      <h1 className="text-2xl font-bold text-gray-900 mb-2">{platform.platform}</h1>
      <div className="flex gap-4 text-sm text-gray-500 mb-6">
        <span>Avg Suitability: <strong>{Math.round(platform.avg_suitability * 10) / 10}</strong></span>
        <span>Total Articles: <strong>{platform.total_articles}</strong></span>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Top Articles for {platform.platform}</h2>
        <div className="space-y-2">
          {platform.top_articles.map((a: any) => (
            <a
              key={a.article_id}
              href={`/articles/${a.slug}`}
              className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50"
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">{a.title}</div>
                {a.reason && <p className="text-xs text-gray-500 truncate mt-0.5">{a.reason}</p>}
                <div className="flex gap-3 mt-1">
                  {a.optimal_format && (
                    <span className="text-xs text-gray-400">Format: {a.optimal_format}</span>
                  )}
                  {a.posting_frequency && (
                    <span className="text-xs text-gray-400">Freq: {a.posting_frequency}</span>
                  )}
                </div>
              </div>
              <span className="text-blue-600 font-mono text-sm ml-3 shrink-0">
                {a.suitability_score}
              </span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
