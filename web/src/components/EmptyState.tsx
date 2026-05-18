import Link from "next/link";

interface EmptyStateProps {
  title?: string;
  description?: string;
  ctaText?: string;
  ctaLink?: string;
  testid?: string;
}

export default function EmptyState({
  title = "Nenhum item encontrado",
  description = "Você ainda não possui registros.",
  ctaText,
  ctaLink,
  testid = "empty-state",
}: EmptyStateProps) {
  return (
    <div className="text-center py-12 bg-white shadow rounded-lg" data-testid={testid}>
      <div className="text-4xl mb-4">📭</div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6">{description}</p>
      {ctaText && ctaLink && (
        <Link href={ctaLink}
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 min-h-[48px]"
          data-testid={`${testid}-cta`}>
          {ctaText}
        </Link>
      )}
    </div>
  );
}
