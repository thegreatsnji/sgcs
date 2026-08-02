import { NavLink } from "react-router-dom";

interface PillSubNavTab {
  to: string;
  label: string;
  end?: boolean;
}

interface PillSubNavProps {
  tabs: PillSubNavTab[];
  ariaLabel: string;
}

export function PillSubNav({ tabs, ariaLabel }: PillSubNavProps) {
  return (
    <nav
      className="flex gap-1 overflow-x-auto rounded-2xl border border-slate-200/80 bg-white p-1.5 shadow-sm"
      aria-label={ariaLabel}
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) =>
            `shrink-0 rounded-xl px-4 py-2.5 text-sm font-medium transition focus-ring ${
              isActive
                ? "bg-primary-600 text-white shadow-md shadow-primary-600/20"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
