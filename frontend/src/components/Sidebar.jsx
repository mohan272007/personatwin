import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: "◇" },
  { to: "/chat", label: "Chat", icon: "▷" },
  { to: "/memory", label: "Memory Timeline", icon: "◈" },
  { to: "/analytics", label: "Analytics", icon: "▤" },
  { to: "/profile", label: "Profile", icon: "◎" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

export default function Sidebar({ user, onLogout }) {
  const navigate = useNavigate();

  return (
    <aside className="w-60 shrink-0 h-screen sticky top-0 flex flex-col border-r border-border bg-surface/60">
      <div
        className="px-5 py-5 flex items-center gap-2 cursor-pointer"
        onClick={() => navigate("/dashboard")}
      >
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet to-cyan flex items-center justify-center font-display font-bold text-base">
          P
        </div>
        <span className="font-display font-semibold tracking-tight">PersonaTwin</span>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-violet/15 text-violet border border-violet/30"
                  : "text-muted hover:text-ink hover:bg-surface2"
              }`
            }
          >
            <span className="w-4 text-center">{l.icon}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-surface2 flex items-center justify-center text-xs font-mono">
            {(user?.name || "U")[0].toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-sm truncate">{user?.name || "Demo User"}</p>
            <p className="text-xs text-muted truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="w-full text-xs text-muted hover:text-red-400 border border-border rounded-lg py-2 transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
