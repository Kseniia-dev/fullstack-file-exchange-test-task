import type { AlertItem, FileItem, PaginatedResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    throw new Error("Не удалось выполнить запрос");
  }

  return response.json() as Promise<T>;
}

export function fetchFiles(page: number, perPage: number) {
  return request<PaginatedResponse<FileItem>>(`/files?page=${page}&per_page=${perPage}`);
}

export function fetchAlerts(page: number, perPage: number) {
  return request<PaginatedResponse<AlertItem>>(`/alerts?page=${page}&per_page=${perPage}`);
}

export async function uploadFile(title: string, file: File) {
  const formData = new FormData();
  formData.append("title", title.trim());
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/files`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Не удалось загрузить файл");
  }

  return response.json() as Promise<FileItem>;
}

export function getDownloadUrl(fileId: string) {
  return `${API_BASE_URL}/files/${fileId}/download`;
}
