import { ReactNode } from "react";
import { Badge, Card } from "react-bootstrap";

type SectionCardProps = {
  title: string;
  total: number;
  children: ReactNode;
};

export function SectionCard({ title, total, children }: SectionCardProps) {
  return (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Header className="bg-white border-0 pt-4 px-4">
        <div className="d-flex justify-content-between align-items-center">
          <h2 className="h5 mb-0">{title}</h2>
          <Badge bg="secondary">{total}</Badge>
        </div>
      </Card.Header>
      <Card.Body className="px-4 pb-4">{children}</Card.Body>
    </Card>
  );
}
