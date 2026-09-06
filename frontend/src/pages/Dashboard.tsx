import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageSizeSelect } from "../components/PageSizeSelect";
import { getApiErrorMessage } from "../api/client";
import { listFoodEntries } from "../api/foodEntries";
import { getGoal } from "../api/goals";
import type { FoodEntry, Goal } from "../api/types";

const DEFAULT_PAGE_SIZE = 5;

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function pct(actual: number, target: number): number {
  if (target <= 0) return 0;
  return Math.min((actual / target) * 100, 100);
}

function MacroStat({ label, actual, target, unit }: { label: string; actual: number; target?: number; unit: string }) {
  return (
    <div className="macro-item">
      <div className="stat-label">{label}</div>
      <div>
        {actual}
        {unit}
        {target !== undefined && <span className="stat-goal"> / {target}{unit}</span>}
      </div>
      {target !== undefined && (
        <div className="progress-bar">
          <div className={`progress-fill${actual > target ? " over" : ""}`} style={{ width: `${pct(actual, target)}%` }} />
        </div>
      )}
    </div>
  );
}

export function Dashboard() {
  const [todayEntries, setTodayEntries] = useState<FoodEntry[]>([]);
  const [goal, setGoal] = useState<Goal | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  useEffect(() => {
    const today = isoDate(new Date());
    Promise.all([
      listFoodEntries({ startDate: `${today}T00:00:00`, endDate: `${today}T23:59:59`, page: 1, pageSize: 100 }),
      getGoal().catch(() => null),
    ])
      .then(([entriesPage, goalResult]) => {
        setTodayEntries(entriesPage.items);
        setGoal(goalResult);
      })
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div className="page-loading"><span className="spinner" />Loading...</div>;

  const totals = todayEntries.reduce(
    (acc, e) => ({
      calories: acc.calories + e.calories,
      protein_g: acc.protein_g + e.protein_g,
      carbs_g: acc.carbs_g + e.carbs_g,
      fat_g: acc.fat_g + e.fat_g,
    }),
    { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 },
  );

  const totalPages = Math.max(Math.ceil(todayEntries.length / pageSize), 1);
  const pageEntries = todayEntries.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="page dashboard-page">
      <h1>Today's Summary</h1>
      {error && <div className="error-banner">{error}</div>}

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Calories today</div>
          <div className="stat-value">
            {totals.calories}
            {goal && <span className="stat-goal"> / {goal.calorie_target}</span>}
          </div>
          {goal && (
            <div className="progress-bar">
              <div
                className={`progress-fill${totals.calories > goal.calorie_target ? " over" : ""}`}
                style={{ width: `${pct(totals.calories, goal.calorie_target)}%` }}
              />
            </div>
          )}
        </div>

        <div className="stat-card">
          <div className="stat-label">Macros today</div>
          <div className="macro-row">
            <MacroStat label="Protein" actual={totals.protein_g} target={goal?.protein_target_g} unit="g" />
            <MacroStat label="Carbs" actual={totals.carbs_g} target={goal?.carb_target_g} unit="g" />
            <MacroStat label="Fat" actual={totals.fat_g} target={goal?.fat_target_g} unit="g" />
          </div>
        </div>
      </div>

      {!goal && (
        <div className="info-banner">
          You haven't set any health goals yet. <Link to="/goals">Set your goals</Link> to track progress.
        </div>
      )}

      <div className="card">
        <h2 className="section-title">Meals logged today</h2>
        {todayEntries.length === 0 ? (
          <p className="muted">
            Nothing logged yet. <Link to="/meals">Log a meal</Link>.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Meal</th>
                <th>Food</th>
                <th>Calories</th>
              </tr>
            </thead>
            <tbody>
              {pageEntries.map((entry) => (
                <tr key={entry.id}>
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

        {todayEntries.length > 0 && (
          <div className="pagination">
            <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </button>
            <span className="muted">
              Page {page} of {totalPages} ({todayEntries.length} total)
            </span>
            <button className="btn btn-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next
            </button>
            <PageSizeSelect
              value={pageSize}
              onChange={(size) => {
                setPageSize(size);
                setPage(1);
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
