import { apiClient } from "./client";
import type { ImportResult, PdfImportDetail, PdfImportSummary } from "./types";

export async function importFoodDiaryPdf(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<ImportResult>("/api/import/pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listPdfImports(): Promise<PdfImportSummary[]> {
  const { data } = await apiClient.get<PdfImportSummary[]>("/api/import/pdf");
  return data;
}

export async function getPdfImportDetail(id: number): Promise<PdfImportDetail> {
  const { data } = await apiClient.get<PdfImportDetail>(`/api/import/pdf/${id}`);
  return data;
}

export async function getPdfImportFileUrl(id: number): Promise<string> {
  const { data } = await apiClient.get(`/api/import/pdf/${id}/file`, { responseType: "blob" });
  return URL.createObjectURL(data as Blob);
}
