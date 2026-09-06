import { useEffect, useState } from "react";
import { MealEntryForm } from "../components/MealEntryForm";
import { getApiErrorMessage } from "../api/client";
import { createFoodEntry, deleteFoodEntry, listFoodEntries, updateFoodEntry } from "../api/foodEntries";
import type { FoodEntry, FoodEntryInput, MealType } from "../api/types";
import { EditIcon, PlusIcon, TrashIcon } from "../components/icons";

const PAGE_SIZE_OPTIONS = [5, 10, 20, 30] as const;
const DEFAULT_PAGE_SIZE = 10;

export function MealLog() {
  const [entries, setEntries] = useState<FoodEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [mealType, setMealType] = useState<MealType | "">("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<FoodEntry | null>(null);

  async function refresh() {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listFoodEntries({
        startDate: startDate ? `${startDate}T00:00:00` : undefined,
        endDate: endDate ? `${endDate}T23:59:59` : undefined,
        mealType: mealType || undefined,
        page,
        pageSize,
      });
      setEntries(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, startDate, endDate, mealType]);

  async function handleCreate(input: FoodEntryInput) {
    await createFoodEntry(input);
    setIsFormOpen(false);
    setPage(1);
    await refresh();
  }

  async function handleUpdate(input: FoodEntryInput) {
    if (!editingEntry) return;
    await updateFoodEntry(editingEntry.id, input);
    setEditingEntry(null);
    await refresh();
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this food entry?")) return;
    try {
      await deleteFoodEntry(id);
      await refresh();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  }

  const totalPages = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="page">
      <h1>Meal Log</h1>
      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-grid">
          <div className="field">
            <label htmlFor="start_date">From</label>
            <input id="start_date" type="date" value={startDate} onChange={(e) => { setPage(1); setStartDate(e.target.value); }} />
          </div>
          <div className="field">
            <label htmlFor="end_date">To</label>
            <input id="end_date" type="date" value={endDate} onChange={(e) => { setPage(1); setEndDate(e.target.value); }} />
          </div>
          <div className="field">
            <label htmlFor="filter_meal_type">Meal type</label>
            <select
              id="filter_meal_type"
              value={mealType}
              onChange={(e) => { setPage(1); setMealType(e.target.value as MealType | ""); }}
            >
              <option value="">All</option>
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
          </div>
        </div>
      </div>

      {editingEntry ? (
        <>
          <h2 className="section-title">Edit entry</h2>
          <MealEntryForm
            initialValues={editingEntry}
            submitLabel="Save changes"
            onSubmit={handleUpdate}
            onCancel={() => setEditingEntry(null)}
          />
        </>
      ) : isFormOpen ? (
        <>
          <h2 className="section-title">Add entry</h2>
          <MealEntryForm submitLabel="Add entry" onSubmit={handleCreate} onCancel={() => setIsFormOpen(false)} />
        </>
      ) : (
        <button className="btn btn-icon-label" onClick={() => setIsFormOpen(true)} style={{ marginBottom: "1rem" }}>
          <PlusIcon />
          Add food entry
        </button>
      )}

      <div className="card">
        {isLoading ? (
          <div className="page-loading"><span className="spinner" />Loading...</div>
        ) : entries.length === 0 ? (
          <p className="muted">No food entries found for this filter.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Meal</th>
                <th>Food</th>
                <th>Qty</th>
                <th>Calories</th>
                <th>P / C / F (g)</th>
                <th></th>
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
                  <td>
                    {entry.quantity} {entry.unit}
                  </td>
                  <td>{entry.calories}</td>
                  <td>
                    {entry.protein_g} / {entry.carbs_g} / {entry.fat_g}
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        className="icon-btn"
                        aria-label="Edit entry"
                        title="Edit entry"
                        onClick={() => {
                          setIsFormOpen(false);
                          setEditingEntry(entry);
                        }}
                      >
                        <EditIcon />
                      </button>
                      <button
                        className="icon-btn icon-btn-danger"
                        aria-label="Delete entry"
                        title="Delete entry"
                        onClick={() => handleDelete(entry.id)}
                      >
                        <TrashIcon />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="pagination">
          <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <span className="muted">
            Page {page} of {totalPages} ({total} total)
          </span>
          <button className="btn btn-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
          <label className="muted" htmlFor="page_size" style={{ marginLeft: "auto" }}>
            Per page
          </label>
          <select
            id="page_size"
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
