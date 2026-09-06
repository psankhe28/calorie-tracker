import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { DashboardIcon, GoalIcon, ImportIcon, MealIcon, ReportsIcon } from "./icons";
import { ThemeToggle } from "./ThemeToggle";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: DashboardIcon, end: true },
  { to: "/meals", label: "Meal Log", icon: MealIcon },
  { to: "/goals", label: "Goals", icon: GoalIcon },
  { to: "/reports", label: "Reports", icon: ReportsIcon },
  { to: "/import", label: "Import Food Diary", icon: ImportIcon },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        Calorie Tracker
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink key={to} to={to} end={end} className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}>
            <Icon />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <ThemeToggle className="sidebar-theme-toggle" />
        <div className="sidebar-user" title={user.email}>
          {user.email}
        </div>
        <button className="btn-logout" onClick={logout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
