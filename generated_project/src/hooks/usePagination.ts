import { useState, useMemo } from 'react';

interface Pagination {
  currentPage: number;
  totalPages: number;
  startIndex: number;
  endIndex: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  canGoNext: boolean;
  canGoPrevious: boolean;
}

/**
 * Custom React hook for pagination logic.
 * @param totalItems Total number of items.
 * @param itemsPerPage Number of items per page.
 * @param initialPage Initial page to display.
 */
export function usePagination(totalItems: number, itemsPerPage: number, initialPage: number = 1): Pagination {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  // Calculate indices for items to display
  const startIndex = useMemo(() => (currentPage - 1) * itemsPerPage, [currentPage, itemsPerPage]);
  const endIndex = useMemo(() => Math.min(startIndex + itemsPerPage - 1, totalItems - 1), [startIndex, itemsPerPage, totalItems]);

  // Navigation functions
  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const nextPage = () => {
    setCurrentPage(prevPage => Math.min(prevPage + 1, totalPages));
  };

  const previousPage = () => {
    setCurrentPage(prevPage => Math.max(prevPage - 1, 1));
  };

  const canGoNext = currentPage < totalPages;
  const canGoPrevious = currentPage > 1;

  return {
    currentPage,
    totalPages,
    startIndex,
    endIndex,
    goToPage,
    nextPage,
    previousPage,
    canGoNext,
    canGoPrevious
  };
}