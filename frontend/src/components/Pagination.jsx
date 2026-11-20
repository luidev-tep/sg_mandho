export default function Pagination({ page, pages, onPageChange }) {
  if (pages <= 1) return null;
  return <nav aria-label="Paginación" className="flex items-center justify-center gap-4 py-4 text-sm">
    <button type="button" className="btn border border-gray-300 dark:border-gray-600 disabled:opacity-40" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Anterior</button>
    <span aria-live="polite">Página {page} de {pages}</span>
    <button type="button" className="btn border border-gray-300 dark:border-gray-600 disabled:opacity-40" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>Siguiente</button>
  </nav>;
}
