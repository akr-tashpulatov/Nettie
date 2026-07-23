import { cn } from "@/shared/lib/utils"
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious, PaginationEllipsis } from "./ui/pagination";
import { useTranslations } from "next-intl";

export function TablePagination({ page, pageCount, onPageChange }: { page: number; pageCount: number; onPageChange: (page: number) => void }) {
  const t = useTranslations('pagination');

  const handlePageClick = (page: number) => {
    if (page < 1 || page > pageCount) return;
    onPageChange(page);
  }

  const handleNextClick = () => {
    if (page + 1 > pageCount) return;
    onPageChange(page + 1);
  }

  const handlePreviousClick = () => {
    if (page - 1 < 1) return;
    onPageChange(page - 1);
  }

  const getVisiblePages = () => {
    if (pageCount <= 5) {
      return Array.from({ length: pageCount }).map((_, i) => i + 1);
    }
    if (page <= 5) {
      return [1, 2, 3, '...', pageCount];
    }
    if (page >= pageCount - 2) {
      return [1, '...', pageCount - 2, pageCount - 1, pageCount];
    }
    return [1, '...', page - 1, page, page + 1, '...', pageCount];
  };

  return (
    <Pagination className="w-full flex justify-end">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious onClick={handlePreviousClick} text={t('previous')} />
        </PaginationItem>
        {
          getVisiblePages().map((p, index) => {
            if (p === '...') {
              return (
                <PaginationItem key={`ellipsis-${index}`}>
                  <PaginationEllipsis />
                </PaginationItem>
              );
            }
            return (
              <PaginationItem key={index}>
                <PaginationLink
                  onClick={() => handlePageClick(p as number)}
                  className={cn(p === page && 'bg-primary text-primary-foreground')}
                >
                  {p}
                </PaginationLink>
              </PaginationItem>
            );
          })
        }
        <PaginationItem>
          <PaginationNext onClick={handleNextClick} text={t('next')} />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  )
}