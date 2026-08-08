import { Link } from "react-router-dom";
import { ArrowUpRight, Bookmark, BookmarkCheck, CalendarDays, CheckCircle2, Globe2, MapPin, Sparkles } from "lucide-react";

const categoryStyles = {
  Fellowship: "bg-violet-50 text-violet-700 border-violet-100",
  Internship: "bg-blue-50 text-blue-700 border-blue-100",
  Scholarship: "bg-emerald-50 text-emerald-700 border-emerald-100",
  Hackathon: "bg-amber-50 text-amber-700 border-amber-100",
  "Open Source": "bg-cyan-50 text-cyan-700 border-cyan-100",
  Research: "bg-fuchsia-50 text-fuchsia-700 border-fuchsia-100",
  Competition: "bg-orange-50 text-orange-700 border-orange-100",
};

export default function OpportunityCard({ opportunity, saved = false, onToggleSave, compact = false }) {
  const closing = opportunity.daysRemaining <= 14;
  return (
    <article className="group rounded-[22px] border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">
      <div className="flex gap-4">
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl border border-slate-200 bg-slate-50 text-sm font-black text-slate-700">
          {opportunity.organization.split(" ").map((x) => x[0]).join("").slice(0, 2)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] ${categoryStyles[opportunity.category] || "bg-slate-50 text-slate-700 border-slate-200"}`}>
                  {opportunity.category}
                </span>
                {opportunity.isNew && <span className="rounded-full bg-slate-950 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] text-white">New</span>}
                {closing && <span className="rounded-full bg-red-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] text-red-700">Closing soon</span>}
              </div>
              <Link to={`/opportunities/${opportunity.id}`} className="mt-3 block text-lg font-black leading-tight tracking-tight text-slate-950 transition group-hover:text-blue-700">
                {opportunity.title}
              </Link>
              <p className="mt-1 text-sm font-medium text-slate-500">{opportunity.organization}</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="rounded-xl bg-slate-950 px-3 py-2 text-right text-white">
                <div className="text-lg font-black leading-none">{opportunity.match}%</div>
                <div className="mt-1 text-[9px] font-semibold uppercase tracking-wider text-slate-400">Match</div>
              </div>
              <button onClick={() => onToggleSave?.(opportunity)} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50" aria-label={saved ? "Remove saved opportunity" : "Save opportunity"}>
                {saved ? <BookmarkCheck size={17} className="text-blue-600" /> : <Bookmark size={17} />}
              </button>
            </div>
          </div>

          {!compact && <p className="mt-3 line-clamp-2 text-sm leading-6 text-slate-600">{opportunity.shortDescription}</p>}

          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-medium text-slate-500">
            <span className="flex items-center gap-1.5"><CalendarDays size={14} /> {opportunity.daysRemaining} days left</span>
            <span className="flex items-center gap-1.5"><MapPin size={14} /> {opportunity.location}</span>
            {opportunity.remote && <span className="flex items-center gap-1.5"><Globe2 size={14} /> Remote</span>}
            <span className="flex items-center gap-1.5"><Sparkles size={14} /> {opportunity.funding}</span>
          </div>

          <div className="mt-4 flex items-center justify-between gap-3 border-t border-slate-100 pt-4">
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              {opportunity.verified && <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-700"><CheckCircle2 size={13} /> Official source</span>}
              <span className="truncate text-[11px] text-slate-400">Checked {opportunity.lastChecked}</span>
            </div>
            <Link to={`/opportunities/${opportunity.id}`} className="flex shrink-0 items-center gap-1 text-xs font-bold text-slate-950 hover:text-blue-700">
              View <ArrowUpRight size={13} />
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}
