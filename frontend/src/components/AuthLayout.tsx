import type { ReactNode } from "react";
import { CheckIcon } from "./icons";
import { ThemeToggle } from "./ThemeToggle";

const FEATURES = [
  "Log meals across breakfast, lunch, dinner & snacks",
  "Set goals and track progress automatically",
  "Visualize macro & micronutrient trends over time",
];

interface Props {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}

export function AuthLayout({ title, subtitle, children, footer }: Props) {
  return (
    <div className="auth-shell">
      <div className="auth-brand-panel">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          Calorie Tracker
        </div>
        <h2>Track your nutrition with clarity.</h2>
        <p className="auth-brand-copy">
          Log meals, set goals, and see exactly where your calories and macros are going —
          all in one place.
        </p>
        <ul className="auth-feature-list">
          {FEATURES.map((feature) => (
            <li key={feature}>
              <CheckIcon />
              {feature}
            </li>
          ))}
        </ul>
      </div>

      <div className="auth-form-panel">
        <ThemeToggle className="auth-theme-toggle" />
        <div className="auth-form-inner">
          <h1>{title}</h1>
          <p className="muted auth-subtitle">{subtitle}</p>
          {children}
          <p className="muted auth-footer-link">{footer}</p>
        </div>
      </div>
    </div>
  );
}
