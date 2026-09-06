import { useState } from "react";
import { getApiErrorMessage } from "../api/client";
import { importFoodDiaryPdf } from "../api/imports";
import type { ImportResult } from "../api/types";

export function ImportFoodDiary() {
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFileSelected(file: File) {
    setError(null);
    setResult(null);
    setIsUploading(true);
    try {
      const importResult = await importFoodDiaryPdf(file);
      setResult(importResult);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsUploading(false);
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
          {result.entries.length > 0 && (
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
                {result.entries.map((entry) => (
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
          )}
          {result.skipped_rows.length > 0 && (
            <>
              <h3 className="section-title" style={{ marginTop: "1rem" }}>
                Skipped {result.skipped_rows.length} row(s)
              </h3>
              <ul>
                {result.skipped_rows.map((skipped, index) => (
                  <li key={index} className="muted">
                    {skipped.reason}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
