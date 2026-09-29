import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getApiErrorMessage } from "../api/client";
import { getGoalVsActual, getMacroBreakdown, getMicroSummary, getMonthlyCalories, getWeeklyCalories, getYearlyCalories } from "../api/reports";
import type { DailyCalories, GoalVsActualMetric, MacroBreakdownDay, MicroNutrient, MonthlyCalories, YearlyCalories } from "../api/types";

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

const tooltipProps = {
  contentStyle: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: 8,
    color: "var(--color-text)",
    fontSize: "0.85rem",
  },
  labelStyle: { color: "var(--color-text-muted)", marginBottom: 4 },
};

export function Reports() {
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 6);
    return isoDate(d);
  });
  const [endDate, setEndDate] = useState(() => isoDate(new Date()));

  const [calories, setCalories] = useState<DailyCalories[]>([]);
  const [macros, setMacros] = useState<MacroBreakdownDay[]>([]);
  const [micros, setMicros] = useState<MicroNutrient[]>([]);
  const [goalComparison, setGoalComparison] = useState<GoalVsActualMetric[] | null>(null);
  const [yearlyCalories, setYearlyCalories] = useState<YearlyCalories[]>([]);
  const [monthlyCalories, setMonthlyCalories] = useState<MonthlyCalories[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [goalError, setGoalError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const range = { startDate, endDate };
    const tenYearsAgoYear = new Date(endDate).getFullYear() - 10;
    const last_10_years = { startDate: `${tenYearsAgoYear}-01-01`, endDate };
    setIsLoading(true);
    setError(null);
    setGoalError(null);

    Promise.all([
      getWeeklyCalories(range),
      getMacroBreakdown(range),
      getMicroSummary(range),
      getYearlyCalories(last_10_years),
      getMonthlyCalories(),
    ])
      .then(([cal, mac, mic, yearCal, monthlyCal]) => {
        setCalories(cal);
        setMacros(mac);
        setMicros(mic);
        setYearlyCalories(yearCal);
        setMonthlyCalories(monthlyCal);
      })
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoading(false));

    getGoalVsActual(range)
      .then(setGoalComparison)
      .catch((err) => {
        setGoalComparison(null);
        setGoalError(getApiErrorMessage(err));
      });
  }, [startDate, endDate]);

  return (
    <div className="page">
      <h1>Nutrition Reports</h1>
      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-grid">
          <div className="field">
            <label htmlFor="report_start">From</label>
            <input id="report_start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="report_end">To</label>
            <input id="report_end" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="page-loading"><span className="spinner" />Loading reports...</div>
      ) : (
        <div className="charts-grid">
          <div className="card">
            <h2 className="section-title">Weekly Calorie Trend</h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={calories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip {...tooltipProps} />
                <Line type="monotone" dataKey="calories" stroke="#4f46e5" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2 className="section-title">Macronutrient Breakdown</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={macros}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip {...tooltipProps} />
                <Legend />
                <Bar dataKey="protein_g" name="Protein (g)" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                <Bar dataKey="carbs_g" name="Carbs (g)" fill="#16a34a" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fat_g" name="Fat (g)" fill="#d97706" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2 className="section-title">Micronutrient Summary</h2>
            {micros.length === 0 ? (
              <p className="muted">No micronutrient data logged in this range.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Nutrient</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {micros.map((m) => (
                    <tr key={m.nutrient}>
                      <td>{m.nutrient}</td>
                      <td>{m.total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="card">
            <h2 className="section-title">Goal vs. Actual (daily average)</h2>
            {goalError ? (
              <p className="muted">{goalError}</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={goalComparison ?? []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip {...tooltipProps} />
                  <Legend />
                  <Bar dataKey="goal" name="Goal" fill="#d7dae4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="actual" name="Actual" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="card">
            <h2 className="section-title">Calories — Last 10 Years</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={yearlyCalories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip {...tooltipProps} />
                <Bar dataKey="calories" name="Calories" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2 className="section-title">Calories — This Year by Month</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={monthlyCalories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip {...tooltipProps} />
                <Bar dataKey="calories" name="Calories" fill="#16a34a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
