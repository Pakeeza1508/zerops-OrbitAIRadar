import { useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  Bookmark,
  Compass,
  LayoutDashboard,
  LogOut,
  Menu,
  Radar,
  UserRound,
  X,
} from "lucide-react";
import OrbitLogo from "./OrbitLogo";

const nav = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/discover", label: "Discover", icon: Compass },
  { to: "/saved", label: "Saved", icon: Bookmark },
  { to: "/ingestion", label: "Radar Status", icon: Radar },
];

export default function AppShell({ children, profile, onLogout }) {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const titleMap = {
    "/dashboard": "Overview",
    "/discover": "Discover",
    "/saved": "Saved Opportunities",
    "/ingestion": "Radar Status",
    "/profile": "Profile",
  };
  const pageTitle = location.pathname.startsWith("/opportunities/")
    ? "Opportunity"
    : titleMap[location.pathname] || "Orbit";

  const initials = (profile?.fullName || "Orbit User")
    .split(" ")
    .map((x) => x[0])
    .join("")
    .slice(0, 2);

  const sidebar = (
    <div className="orbit-sidebar flex h-full flex-col border-r border-white/[.07] bg-[#091310]/95 px-4 py-5 text-white backdrop-blur-xl">
      <div className="px-2">
        <OrbitLogo inverse />
      </div>

      <div className="mt-9 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-[#50635f]">
        Workspace
      </div>
      <nav className="mt-3 space-y-1.5">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              `orbit-nav-link relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
                isActive
                  ? "active bg-white/[.055] text-white"
                  : "text-[#879995] hover:bg-white/[.035] hover:text-white"
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
            {to === "/ingestion" && (
              <span className="ml-auto h-1.5 w-1.5 rounded-full bg-[#69f0c0] shadow-[0_0_10px_#69f0c0]" />
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mt-8 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-[#50635f]">
        Account
      </div>
      <NavLink
        to="/profile"
        onClick={() => setOpen(false)}
        className={({ isActive }) =>
          `orbit-nav-link relative mt-3 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
            isActive
              ? "active bg-white/[.055] text-white"
              : "text-[#879995] hover:bg-white/[.035] hover:text-white"
          }`
        }
      >
        <UserRound size={18} /> Profile
      </NavLink>

      <div className="mt-auto rounded-2xl border border-white/[.08] bg-[#0b1614] p-3.5 shadow-[inset_0_1px_rgba(255,255,255,.025)]">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-gradient-to-br from-[#263c36] to-[#10231e] text-xs font-black text-white">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold text-white">
              {profile?.fullName || "Orbit User"}
            </p>
            <p className="mt-0.5 truncate text-[10px] text-[#71857f]">
              {profile?.field || "Student"}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="grid h-8 w-8 place-items-center rounded-lg text-[#71857f] transition hover:bg-white/5 hover:text-white"
            aria-label="Log out"
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="orbit-app-shell min-h-screen bg-[#07100f] text-[#eef7f4]">
      <div className="pointer-events-none fixed inset-x-0 top-0 z-[60] h-px bg-gradient-to-r from-transparent via-lime-200/30 to-transparent" />

      <div className="orbit-desktop-layout">
        <aside className="orbit-desktop-sidebar">
          {sidebar}
        </aside>

        <div className="orbit-desktop-content">

      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setOpen(false)}
            aria-label="Close navigation"
          />
          <aside className="relative h-full w-[280px] shadow-2xl">
            {sidebar}
            <button
              className="absolute right-4 top-4 grid h-9 w-9 place-items-center rounded-xl border border-white/10 bg-white/5 text-white"
              onClick={() => setOpen(false)}
              aria-label="Close navigation"
            >
              <X size={17} />
            </button>
          </aside>
        </div>
      )}

        <header className="sticky top-0 z-20 flex h-[76px] items-center justify-between border-b border-white/[.065] bg-[#07100f]/82 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setOpen(true)}
              className="grid h-10 w-10 place-items-center rounded-xl border border-white/[.08] bg-white/[.035] text-[#a8bbb5] lg:hidden"
              aria-label="Open navigation"
            >
              <Menu size={18} />
            </button>
            <div className="hidden items-center gap-2 text-sm text-[#8ea09b] sm:flex">
              <span>{pageTitle === "Overview" ? "Good evening," : pageTitle}</span>
              {pageTitle === "Overview" && <span className="font-semibold text-white">{(profile?.fullName || "Orbit User").split(" ")[0]}</span>}
              {pageTitle === "Overview" && <span>👋</span>}
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="hidden items-center gap-2 rounded-xl border border-white/[.08] bg-white/[.035] px-3.5 py-2 text-[11px] text-[#8fa19e] xl:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-[#69f0c0] shadow-[0_0_8px_#69f0c0]" />
              Radar is live
            </div>
            <button
              className="grid h-10 w-10 place-items-center rounded-xl border border-white/[.08] bg-white/[.035] text-[#96aaa4] transition hover:text-white"
              aria-label="Notifications"
            >
              <Bell size={17} />
            </button>
            <button
              onClick={() => navigate("/discover")}
              className="hidden rounded-xl bg-[#eafdb7] px-4 py-2.5 text-xs font-black text-[#102016] transition hover:brightness-110 sm:block"
            >
              Find opportunities
            </button>
            <button
              onClick={() => navigate("/profile")}
              className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-gradient-to-br from-[#263c36] to-[#10231e] text-xs font-black text-white"
              aria-label="Open profile"
            >
              {initials}
            </button>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-7">
          {children}
        </main>
        </div>
      </div>

      <nav className="fixed inset-x-3 bottom-3 z-30 grid grid-cols-4 rounded-2xl border border-white/[.09] bg-[#0a1513]/95 p-1.5 shadow-2xl backdrop-blur-xl lg:hidden">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 rounded-xl px-1 py-2 text-[9px] font-bold transition ${
                isActive
                  ? "bg-[#eafdb7] text-[#102016]"
                  : "text-[#71857f]"
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
