import { useState, type FormEvent } from "react";
import { extractNutritionFromImage } from "../api/ai";
import { getApiErrorMessage } from "../api/client";
import type { FoodEntryInput, MealType } from "../api/types";
import { AI_FEATURES_ENABLED } from "../config";

const MEAL_TYPES: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

function capitalize(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function toLocalDateTimeInput(iso: string): string {
  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function defaultForm(): FoodEntryInput {
  return {
    meal_type: "breakfast",
    food_name: "",
    quantity: 1,
    unit: "serving",
    calories: 0,
    protein_g: 0,
    carbs_g: 0,
    fat_g: 0,
    micros: {},
    logged_at: toLocalDateTimeInput(new Date().toISOString()),
  };
}

interface Props {
  initialValues?: FoodEntryInput;
  submitLabel: string;
  onSubmit: (input: FoodEntryInput) => Promise<void>;
  onCancel?: () => void;
}

export function MealEntryForm({ initialValues, submitLabel, onSubmit, onCancel }: Props) {
  const [form, setForm] = useState<FoodEntryInput>(
    initialValues ? { ...initialValues, logged_at: toLocalDateTimeInput(initialValues.logged_at) } : defaultForm(),
  );
  const [microsText, setMicrosText] = useState(() =>
    Object.entries(form.micros)
      .map(([k, v]) => `${k}=${v}`)
      .join(", "),
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanNote, setScanNote] = useState<string | null>(null);

  function updateField<K extends keyof FoodEntryInput>(key: K, value: FoodEntryInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function parseMicros(text: string): Record<string, number> {
    const result: Record<string, number> = {};
    text
      .split(",")
      .map((pair) => pair.trim())
      .filter(Boolean)
      .forEach((pair) => {
        const [key, value] = pair.split("=").map((s) => s.trim());
        if (key && value && !Number.isNaN(Number(value))) {
          result[key] = Number(value);
        }
      });
    return result;
  }

  async function handlePhotoSelected(file: File) {
    setError(null);
    setScanNote(null);
    setIsScanning(true);
    try {
      const extracted = await extractNutritionFromImage(file);
      setForm((prev) => ({
        ...prev,
        food_name: extracted.food_name,
        quantity: extracted.quantity,
        unit: extracted.unit,
        calories: extracted.calories,
        protein_g: extracted.protein_g,
        carbs_g: extracted.carbs_g,
        fat_g: extracted.fat_g,
        micros: extracted.micros,
      }));
      setMicrosText(
        Object.entries(extracted.micros)
          .map(([k, v]) => `${k}=${v}`)
          .join(", "),
      );
      setScanNote(extracted.confidence_note ?? "Review the pre-filled values before saving.");
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsScanning(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({
        ...form,
        micros: parseMicros(microsText),
        logged_at: new Date(form.logged_at).toISOString(),
      });
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      {error && <div className="error-banner">{error}</div>}
      {scanNote && <div className="info-banner">AI scan: {scanNote}</div>}

      {AI_FEATURES_ENABLED && (
        <div className="field" style={{ marginBottom: "0.75rem" }}>
          <label htmlFor="photo">Scan a nutrition label or plate photo (optional)</label>
          <input
            id="photo"
            type="file"
            accept="image/png, image/jpeg, image/webp, image/gif"
            disabled={isScanning}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void handlePhotoSelected(file);
              e.target.value = "";
            }}
          />
          {isScanning && <span className="muted">Analyzing image...</span>}
        </div>
      )}

      <div className="form-grid">
        <div className="field">
          <label htmlFor="meal_type">Meal type</label>
          <select id="meal_type" value={form.meal_type} onChange={(e) => updateField("meal_type", e.target.value as MealType)}>
            {MEAL_TYPES.map((type) => (
              <option key={type} value={type}>
                {capitalize(type)}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="food_name">Food name</label>
          <input
            id="food_name"
            required
            value={form.food_name}
            onChange={(e) => updateField("food_name", e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="quantity">Quantity</label>
          <input
            id="quantity"
            type="number"
            min={0.01}
            step="0.01"
            required
            value={form.quantity}
            onChange={(e) => updateField("quantity", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="unit">Unit</label>
          <input id="unit" value={form.unit} onChange={(e) => updateField("unit", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="calories">Calories</label>
          <input
            id="calories"
            type="number"
            min={0}
            step="any"
            required
            value={form.calories}
            onChange={(e) => updateField("calories", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="protein_g">Protein (g)</label>
          <input
            id="protein_g"
            type="number"
            min={0}
            step="any"
            value={form.protein_g}
            onChange={(e) => updateField("protein_g", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="carbs_g">Carbs (g)</label>
          <input
            id="carbs_g"
            type="number"
            min={0}
            step="any"
            value={form.carbs_g}
            onChange={(e) => updateField("carbs_g", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="fat_g">Fat (g)</label>
          <input
            id="fat_g"
            type="number"
            min={0}
            step="any"
            value={form.fat_g}
            onChange={(e) => updateField("fat_g", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="logged_at">Date &amp; time</label>
          <input
            id="logged_at"
            type="datetime-local"
            required
            value={form.logged_at}
            onChange={(e) => updateField("logged_at", e.target.value)}
          />
        </div>
      </div>

      <div className="field" style={{ marginTop: "0.75rem" }}>
        <label htmlFor="micros">Micronutrients (optional, e.g. "iron_mg=3.5, vitamin_c_mg=12")</label>
        <input id="micros" value={microsText} onChange={(e) => setMicrosText(e.target.value)} />
      </div>

      <div className="row-actions" style={{ marginTop: "1rem" }}>
        <button className="btn" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button className="btn btn-secondary" type="button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
