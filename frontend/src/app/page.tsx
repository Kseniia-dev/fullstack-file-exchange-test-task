"use client";

import { FormEvent, useState } from "react";
import { Alert, Button, Card, Col, Container, Row, Spinner } from "react-bootstrap";

import { AlertsTable } from "@/features/dashboard/components/alerts-table";
import { FilesTable } from "@/features/dashboard/components/files-table";
import { PaginationControls } from "@/features/dashboard/components/pagination-controls";
import { SectionCard } from "@/features/dashboard/components/section-card";
import { UploadFileModal } from "@/features/dashboard/components/upload-file-modal";
import { useDashboardData } from "@/features/dashboard/hooks/use-dashboard-data";
import { getDownloadUrl, uploadFile } from "@/shared/api";

export default function Page() {
  const { alerts, errorMessage, files, isLoading, refresh, setAlertsPage, setFilesPage } =
    useDashboardData();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitErrorMessage, setSubmitErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      setSubmitErrorMessage("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    setSubmitErrorMessage(null);

    try {
      await uploadFile(title, selectedFile);
      setShowModal(false);
      setTitle("");
      setSelectedFile(null);
      await refresh();
    } catch (error) {
      setSubmitErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  const combinedError = submitErrorMessage ?? errorMessage;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => void refresh()}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => setShowModal(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {combinedError ? (
            <Alert variant="danger" className="shadow-sm">
              {combinedError}
            </Alert>
          ) : null}

          <SectionCard title="Файлы" total={files.total}>
            {isLoading ? (
              <div className="d-flex justify-content-center py-5">
                <Spinner animation="border" />
              </div>
            ) : (
              <>
                <FilesTable files={files.items} downloadUrlFactory={getDownloadUrl} />
                <PaginationControls
                  page={files.page}
                  totalPages={files.total_pages}
                  onPageChange={setFilesPage}
                />
              </>
            )}
          </SectionCard>

          <SectionCard title="Алерты" total={alerts.total}>
            {isLoading ? (
              <div className="d-flex justify-content-center py-5">
                <Spinner animation="border" />
              </div>
            ) : (
              <>
                <AlertsTable alerts={alerts.items} />
                <PaginationControls
                  page={alerts.page}
                  totalPages={alerts.total_pages}
                  onPageChange={setAlertsPage}
                />
              </>
            )}
          </SectionCard>
        </Col>
      </Row>

      <UploadFileModal
        isSubmitting={isSubmitting}
        show={showModal}
        title={title}
        onClose={() => {
          setShowModal(false);
          setSubmitErrorMessage(null);
        }}
        onSubmit={handleSubmit}
        onTitleChange={setTitle}
        onFileChange={setSelectedFile}
      />
    </Container>
  );
}
