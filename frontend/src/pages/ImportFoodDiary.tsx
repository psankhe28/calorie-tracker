import { useEffect, useState } from "react";
import { getApiErrorMessage } from "../api/client";
import { getPdfImportDetail, getPdfImportFileUrl, importFoodDiaryPdf, listPdfImports } from "../api/imports";
import type { ImportResult, PdfImportDetail, PdfImportSummary } from "../api/types";

function EntriesTable({ entries }: { entries: PdfImportDetail["entries"] }) {
  if (entries.length === 0) return null;
  return (
    <table>
      <thead>
        <tr>
          <th>When</th>
          <th>Meal</th>
          <th>Food</th>
          <th>Calories</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => (
          <tr key={entry.id}>
            <td>{new Date(entry.logged_at).toLocaleString()}</td>
            <td>
              <span className={`pill ${entry.meal_type}`}>{entry.meal_type}</span>
            </td>
            <td>{entry.food_name}</td>
            <td>{entry.calories}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function SkippedList({ skippedRows }: { skippedRows: PdfImportDetail["skipped_rows"] }) {
  if (skippedRows.length === 0) return null;
  return (
    <>
      <h3 className="section-title" style={{ marginTop: "1rem" }}>
        Skipped {skippedRows.length} row(s)
      </h3>
      <ul>
        {skippedRows.map((skipped, index) => (
          <li key={index} className="muted">
            {skipped.reason}
          </li>
        ))}
      </ul>
    </>
  );
}

export function ImportFoodDiary() {
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [history, setHistory] = useState<PdfImportSummary[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<PdfImportDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [isLoadingPdf, setIsLoadingPdf] = useState(false);

  function refreshHistory() {
    setIsLoadingHistory(true);
    listPdfImports()
      .then(setHistory)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoadingHistory(false));
  }

  useEffect(refreshHistory, []);

  async function handleFileSelected(file: File) {
    setError(null);
    setResult(null);
    setIsUploading(true);
    try {
      const importResult = await importFoodDiaryPdf(file);
      setResult(importResult);
      refreshHistory();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSelectImport(id: number) {
    setSelectedId(id);
    setDetail(null);
    setDetailError(null);
    setIsLoadingDetail(true);
    try {
      const data = await getPdfImportDetail(id);
      setDetail(data);
    } catch (err) {
      setDetailError(getApiErrorMessage(err));
    } finally {
      setIsLoadingDetail(false);
    }
  }

  async function handleViewOriginalPdf(id: number) {
    setIsLoadingPdf(true);
    try {
      const url = await getPdfImportFileUrl(id);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      setDetailError(getApiErrorMessage(err));
    } finally {
      setIsLoadingPdf(false);
    }
  }

  return (
    <div className="page">
      <h1>Import Food Diary</h1>
      <p className="muted">
        Upload a food diary or nutrition history exported as a PDF. Tabular exports are parsed directly;
        free-form text falls back to AI-assisted extraction.
      </p>
      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <input
          type="file"
          accept="application/pdf"
          disabled={isUploading}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFileSelected(file);
            e.target.value = "";
          }}
        />
        {isUploading && <p className="muted">Parsing PDF...</p>}
      </div>

      {result && (
        <div className="card">
          <h2 className="section-title">
            Imported {result.imported_count} {result.imported_count === 1 ? "entry" : "entries"}
          </h2>
          <EntriesTable entries={result.entries} />
          <SkippedList skippedRows={result.skipped_rows} />
        </div>
      )}

      <div className="card">
        <h2 className="section-title">Past uploads</h2>
        {isLoadingHistory ? (
          <div className="page-loading">
            <span className="spinner" />
            Loading...
          </div>
        ) : history.length === 0 ? (
          <p className="muted">No PDFs uploaded yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Uploaded</th>
                <th>Imported</th>
                <th>Skipped</th>
              </tr>
            </thead>
            <tbody>
              {history.map((upload) => (
                <tr
                  key={upload.id}
                  onClick={() => handleSelectImport(upload.id)}
                  className={`clickable-row${selectedId === upload.id ? " selected" : ""}`}
                >
                  <td>{upload.file_name}</td>
                  <td>{new Date(upload.created_at).toLocaleString()}</td>
                  <td>{upload.imported_count}</td>
                  <td>{upload.skipped_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selectedId !== null && (
        <div className="card">
          {isLoadingDetail ? (
            <div className="page-loading">
              <span className="spinner" />
              Loading...
            </div>
          ) : detailError ? (
            <div className="error-banner">{detailError}</div>
          ) : detail ? (
            <>
              <div className="row-actions" style={{ justifyContent: "space-between", alignItems: "center" }}>
                <h2 className="section-title" style={{ margin: 0 }}>
                  {detail.file_name}
                </h2>
                <button className="btn btn-secondary" disabled={isLoadingPdf} onClick={() => handleViewOriginalPdf(detail.id)}>
                  {isLoadingPdf ? "Opening..." : "View original PDF"}
                </button>
              </div>
              <p className="muted" style={{ marginTop: "0.5rem" }}>
                Uploaded {new Date(detail.created_at).toLocaleString()} — {detail.imported_count} imported,{" "}
                {detail.skipped_rows.length} skipped
              </p>
              <EntriesTable entries={detail.entries} />
              <SkippedList skippedRows={detail.skipped_rows} />
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
