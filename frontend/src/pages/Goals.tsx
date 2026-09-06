import { useEffect, useState, type FormEvent } from "react";
import { getGoal, getGoalHistory, upsertGoal } from "../api/goals";
import { getApiErrorMessage } from "../api/client";
import type { Goal, GoalInput } from "../api/types";

const EMPTY_GOAL: GoalInput = {
  calorie_target: 2000,
  protein_target_g: 100,
  carb_target_g: 200,
  fat_target_g: 65,
  weight_goal_kg: null,
};

export function Goals() {
  const [form, setForm] = useState<GoalInput>(EMPTY_GOAL);
  const [history, setHistory] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  function loadHistory() {
    getGoalHistory()
      .then(setHistory)
      .catch(() => {
        /* no goals set yet */
      });
  }

  useEffect(() => {
    getGoal()
      .then((goal) => setForm(goal))
      .catch(() => {
        /* no goal set yet — keep defaults */
      })
      .finally(() => setIsLoading(false));
    loadHistory();
  }, []);

  function updateField<K extends keyof GoalInput>(key: K, value: GoalInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSavedMessage(null);
    setIsSaving(true);
    try {
      const saved = await upsertGoal(form);
      setForm(saved);
      setSavedMessage("Goals saved.");
      loadHistory();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) return <div className="page-loading"><span className="spinner" />Loading...</div>;

  const currentGoal = history[0];
  const pastGoals = history.slice(1);

  return (
    <div className="page">
      <h1>Health Goals</h1>
      {error && <div className="error-banner">{error}</div>}
      {savedMessage && <div className="info-banner">{savedMessage}</div>}
      <form className="card" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="field">
            <label htmlFor="calorie_target">Daily calorie target</label>
            <input
              id="calorie_target"
              type="number"
              min={0}
              step="any"
              required
              value={form.calorie_target}
              onChange={(e) => updateField("calorie_target", Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label htmlFor="protein_target_g">Protein target (g)</label>
            <input
              id="protein_target_g"
              type="number"
              min={0}
              step="any"
              required
              value={form.protein_target_g}
              onChange={(e) => updateField("protein_target_g", Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label htmlFor="carb_target_g">Carb target (g)</label>
            <input
              id="carb_target_g"
              type="number"
              min={0}
              step="any"
              required
              value={form.carb_target_g}
              onChange={(e) => updateField("carb_target_g", Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label htmlFor="fat_target_g">Fat target (g)</label>
            <input
              id="fat_target_g"
              type="number"
              min={0}
              step="any"
              required
              value={form.fat_target_g}
              onChange={(e) => updateField("fat_target_g", Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label htmlFor="weight_goal_kg">Weight goal (kg, optional)</label>
            <input
              id="weight_goal_kg"
              type="number"
              min={0}
              step="any"
              value={form.weight_goal_kg ?? ""}
              onChange={(e) => updateField("weight_goal_kg", e.target.value ? Number(e.target.value) : null)}
            />
          </div>
        </div>
        <button className="btn" type="submit" disabled={isSaving} style={{ marginTop: "1rem" }}>
          {isSaving ? "Saving..." : "Save goals"}
        </button>
      </form>

      {currentGoal && (
        <div className="card">
          <h2 className="section-title">Current goal</h2>
          <p className="muted" style={{ marginBottom: "0.75rem" }}>
            Set on {new Date(currentGoal.created_at).toLocaleDateString()}
          </p>
          <div className="macro-row">
            <div className="macro-item">
              <div className="stat-label">Calories</div>
              {currentGoal.calorie_target}
            </div>
            <div className="macro-item">
              <div className="stat-label">Protein</div>
              {currentGoal.protein_target_g}g
            </div>
            <div className="macro-item">
              <div className="stat-label">Carbs</div>
              {currentGoal.carb_target_g}g
            </div>
            <div className="macro-item">
              <div className="stat-label">Fat</div>
              {currentGoal.fat_target_g}g
            </div>
            {currentGoal.weight_goal_kg != null && (
              <div className="macro-item">
                <div className="stat-label">Weight goal</div>
                {currentGoal.weight_goal_kg}kg
              </div>
            )}
          </div>
        </div>
      )}

      {pastGoals.length > 0 && (
        <div className="card">
          <h2 className="section-title">Past goals</h2>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Set on</th>
                  <th>Calories</th>
                  <th>Protein</th>
                  <th>Carbs</th>
                  <th>Fat</th>
                  <th>Weight goal</th>
                </tr>
              </thead>
              <tbody>
                {pastGoals.map((goal) => (
                  <tr key={goal.id}>
                    <td>{new Date(goal.created_at).toLocaleDateString()}</td>
                    <td>{goal.calorie_target}</td>
                    <td>{goal.protein_target_g}g</td>
                    <td>{goal.carb_target_g}g</td>
                    <td>{goal.fat_target_g}g</td>
                    <td>{goal.weight_goal_kg != null ? `${goal.weight_goal_kg}kg` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
