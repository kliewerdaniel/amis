import { notFound } from "next/navigation";
import { getArticleBySlug, getArticleSummaries } from "@/lib/data";
import ArticleDetailClient from "./client";

export function generateStaticParams() {
  return getArticleSummaries().map((a) => ({ slug: a.slug }));
}

export default async function ArticleDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const article = getArticleBySlug(slug);
  if (!article) notFound();

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <a href="/articles/" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Articles
      </a>

      <h1 className="text-2xl font-bold text-gray-900 mb-2">{article.title}</h1>

      {article.description && (
        <p className="text-gray-600 mb-4">{article.description}</p>
      )}

      <div className="flex flex-wrap gap-2 mb-6">
        {article.publication_date && (
          <span className="text-xs text-gray-500">{article.publication_date}</span>
        )}
        {article.reading_time_minutes && (
          <span className="text-xs text-gray-500">{article.reading_time_minutes} min read</span>
        )}
        {article.word_count && (
          <span className="text-xs text-gray-500">{article.word_count.toLocaleString()} words</span>
        )}
      </div>

      <ArticleDetailClient article={article} />
    </div>
  );
}
