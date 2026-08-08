import { useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Bookmark, Compass, LayoutDashboard, LogOut, Menu, Radar, UserRound, X } from "lucide-react";
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
  const pageTitle = location.pathname.startsWith("/opportunities/") ? "Opportunity" : titleMap[location.pathname] || "Orbit";

  const sidebar = (
    <div className="flex h-full flex-col bg-slate-950 px-4 py-5 text-white">
      <div className="px-2"><OrbitLogo inverse /></div>
      <div className="mt-9 px-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">Workspace</div>
      <nav className="mt-3 space-y-1.5">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${isActive ? "bg-white text-slate-950" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}>
            <Icon size={17} /> {label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-8 px-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">Account</div>
      <NavLink to="/profile" onClick={() => setOpen(false)} className={({ isActive }) => `mt-3 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${isActive ? "bg-white text-slate-950" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}>
        <UserRound size={17} /> Profile
      </NavLink>
      <div className="mt-auto rounded-2xl border border-white/10 bg-white/[0.04] p-3">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-blue-600 text-xs font-black">{(profile?.fullName || "Orbit User").split(" ").map((x) => x[0]).join("").slice(0, 2)}</div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold text-white">{profile?.fullName || "Orbit User"}</p>
            <p className="truncate text-[10px] text-slate-500">{profile?.field || "Student"}</p>
          </div>
          <button onClick={onLogout} className="text-slate-500 hover:text-white" aria-label="Log out"><LogOut size={15} /></button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#f6f7f9] text-slate-950">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[244px] lg:block">{sidebar}</aside>
      {open && <div className="fixed inset-0 z-50 lg:hidden"><button className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" onClick={() => setOpen(false)} aria-label="Close navigation" /><aside className="relative h-full w-[280px] shadow-2xl">{sidebar}<button className="absolute right-4 top-4 text-white" onClick={() => setOpen(false)}><X /></button></aside></div>}
      <div className="lg:pl-[244px]">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <button onClick={() => setOpen(true)} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 lg:hidden"><Menu size={18} /></button>
            <div><div className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">Orbit workspace</div><div className="text-sm font-black">{pageTitle}</div></div>
          </div>
          <button onClick={() => navigate("/discover")} className="rounded-xl bg-slate-950 px-4 py-2 text-xs font-bold text-white transition hover:bg-slate-800">Find opportunities</button>
        </header>
        <main className="mx-auto w-full max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
      </div>
      <nav className="fixed inset-x-3 bottom-3 z-30 grid grid-cols-4 rounded-2xl border border-slate-200 bg-white/95 p-1.5 shadow-xl backdrop-blur lg:hidden">
        {nav.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({isActive}) => `flex flex-col items-center gap-1 rounded-xl px-1 py-2 text-[9px] font-bold ${isActive ? "bg-slate-950 text-white" : "text-slate-500"}`}><Icon size={16}/>{label}</NavLink>)}
      </nav>
    </div>
  );
}
