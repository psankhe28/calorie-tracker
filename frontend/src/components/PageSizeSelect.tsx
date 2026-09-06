const PAGE_SIZE_OPTIONS = [5, 10, 20, 30] as const;

interface PageSizeSelectProps {
  value: number;
  onChange: (size: number) => void;
}

export function PageSizeSelect({ value, onChange }: PageSizeSelectProps) {
  return (
    <div className="page-size-select">
      <label htmlFor="page_size">Per page</label>
      <select id="page_size" value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {PAGE_SIZE_OPTIONS.map((size) => (
          <option key={size} value={size}>
            {size}
          </option>
        ))}
      </select>
    </div>
  );
}
