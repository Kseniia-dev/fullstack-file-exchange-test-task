import { Button, ButtonGroup } from "react-bootstrap";

type PaginationControlsProps = {
  page: number;
  totalPages: number;
  disabled?: boolean;
  onPageChange: (page: number) => void;
};

export function PaginationControls({
  page,
  totalPages,
  disabled = false,
  onPageChange,
}: PaginationControlsProps) {
  const safeTotalPages = Math.max(totalPages, 1);

  return (
    <div className="d-flex justify-content-between align-items-center gap-3 flex-wrap mt-3">
      <span className="small text-secondary">
        Страница {Math.min(page, safeTotalPages)} из {safeTotalPages}
      </span>
      <ButtonGroup>
        <Button
          variant="outline-secondary"
          disabled={disabled || page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Назад
        </Button>
        <Button
          variant="outline-secondary"
          disabled={disabled || page >= safeTotalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Вперед
        </Button>
      </ButtonGroup>
    </div>
  );
}
