import { useEffect, useState } from "react";

import { fetchAlerts, fetchFiles } from "@/shared/api";
import type { AlertItem, FileItem, PaginatedResponse, PaginationState } from "@/shared/types";

const DEFAULT_PAGINATION: PaginationState = {
  page: 1,
  perPage: 5,
};

type DashboardData = {
  alerts: PaginatedResponse<AlertItem>;
  files: PaginatedResponse<FileItem>;
  isLoading: boolean;
  errorMessage: string | null;
  refresh: () => Promise<void>;
  setAlertsPage: (page: number) => void;
  setFilesPage: (page: number) => void;
};

function emptyPage<T>(pagination: PaginationState): PaginatedResponse<T> {
  return {
    items: [],
    total: 0,
    page: pagination.page,
    per_page: pagination.perPage,
    total_pages: 0,
  };
}

export function useDashboardData(): DashboardData {
  const [filesPagination, setFilesPagination] = useState<PaginationState>(DEFAULT_PAGINATION);
  const [alertsPagination, setAlertsPagination] = useState<PaginationState>(DEFAULT_PAGINATION);
  const [files, setFiles] = useState<PaginatedResponse<FileItem>>(emptyPage<FileItem>(DEFAULT_PAGINATION));
  const [alerts, setAlerts] = useState<PaginatedResponse<AlertItem>>(emptyPage<AlertItem>(DEFAULT_PAGINATION));
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function refresh() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesResponse, alertsResponse] = await Promise.all([
        fetchFiles(filesPagination.page, filesPagination.perPage),
        fetchAlerts(alertsPagination.page, alertsPagination.perPage),
      ]);

      setFiles(filesResponse);
      setAlerts(alertsResponse);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [filesPagination.page, filesPagination.perPage, alertsPagination.page, alertsPagination.perPage]);

  return {
    alerts,
    files,
    isLoading,
    errorMessage,
    refresh,
    setAlertsPage: (page: number) =>
      setAlertsPagination((current) => ({
        ...current,
        page,
      })),
    setFilesPage: (page: number) =>
      setFilesPagination((current) => ({
        ...current,
        page,
      })),
  };
}
