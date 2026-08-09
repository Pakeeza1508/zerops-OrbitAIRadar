import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  Bookmark,
  BookmarkCheck,
  CalendarDays,
  CheckCircle2,
  Globe2,
  MapPin,
  Sparkles,
} from "lucide-react";

const categoryStyles = {
  Fellowship: "text-[#c9a9ff] bg-[#a77cff]/[.07] border-[#a77cff]/10",
  Internship: "text-[#8cc6ff] bg-[#76baff]/[.07] border-[#76baff]/10",
  Scholarship: "text-[#81f5cc] bg-[#69f0c0]/[.07] border-[#69f0c0]/10",
  Hackathon: "text-[#ffcf78] bg-[#ffcb6b]/[.07] border-[#ffcb6b]/10",
  "Open Source": "text-[#83e8dd] bg-[#69f0c0]/[.07] border-[#69f0c0]/10",
  Research: "text-[#d7a4ef] bg-[#cc83e7]/[.07] border-[#cc83e7]/10",
  Competition: "text-[#ffb985] bg-[#ff9c62]/[.07] border-[#ff9c62]/10",
};

export default function OpportunityCard({ opportunity, saved = false, onToggleSave, compact = false }) {
  const closing = opportunity.daysRemaining <= 14;
  const initials = opportunity.organization
    .split(" ")
    .map((x) => x[0])
    .join("")
    .slice(0, 2);

  return (
    <article className="group orbit-panel rounded-[22px] border border-white/[.075] bg-[#0d1917] p-5 shadow-[inset_0_1px_rgba(255,255,255,.02),0_16px_40px_rgba(0,0,0,.12)] transition duration-200 hover:-translate-y-0.5 hover:border-[#d5ff69]/20 hover:bg-[#0f1d1a]">
      <div className="flex gap-4">
        <div className="hidden h-12 w-12 shrink-0 place-items-center rounded-2xl border border-white/[.07] bg-[#152a25] text-sm font-black text-[#d5ff69] sm:grid">
          {initials}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2 text-[10px]">
                {opportunity.verified && (
                  <span className="font-bold text-[#69f0c0]">VERIFIED</span>
                )}
                {opportunity.verified && <span className="text-white/20">•</span>}
                <span
                  className={`rounded-md border px-1.5 py-0.5 font-semibold ${
                    categoryStyles[opportunity.category] ||
                    "border-white/[.08] bg-white/[.03] text-[#8fa19e]"
                  }`}
                >
                  {opportunity.category}
                </span>
                {opportunity.isNew && (
                  <span className="rounded-md bg-[#76baff]/10 px-1.5 py-0.5 text-[#8cc6ff]">New</span>
                )}
                {closing && (
                  <span className="rounded-md bg-[#ffcb6b]/10 px-1.5 py-0.5 text-[#ffcb6b]">Closing soon</span>
                )}
              </div>

              <Link
                to={`/opportunities/${opportunity.id}`}
                className="mt-2 block font-display text-[16px] font-bold leading-6 text-white transition group-hover:text-[#eafdb7] sm:text-[17px]"
              >
                {opportunity.title}
              </Link>
              <p className="mt-1 text-[11px] font-medium text-[#7f948e]">
                {opportunity.organization}
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <div
                className="orbit-match-ring relative grid h-14 w-14 place-items-center rounded-full"
                style={{ "--match": opportunity.match }}
                aria-label={`${opportunity.match}% match`}
              >
                <div className="absolute inset-[5px] rounded-full bg-[#0d1917]" />
                <span className="relative z-10 text-[12px] font-black text-[#d5ff69]">
                  {opportunity.match}%
                </span>
              </div>
              <button
                onClick={() => onToggleSave?.(opportunity)}
                className="grid h-10 w-10 place-items-center rounded-xl border border-white/[.08] bg-white/[.025] text-[#8fa19e] transition hover:border-[#d5ff69]/20 hover:text-[#d5ff69]"
                aria-label={saved ? "Remove saved opportunity" : "Save opportunity"}
              >
                {saved ? (
                  <BookmarkCheck size={17} className="text-[#d5ff69]" />
                ) : (
                  <Bookmark size={17} />
                )}
              </button>
            </div>
          </div>

          {!compact && (
            <p className="mt-3 line-clamp-2 text-[12px] leading-5 text-[#8fa19d]">
              {opportunity.shortDescription}
            </p>
          )}

          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-[10px] font-medium text-[#71857f]">
            <span className={`flex items-center gap-1.5 ${closing ? "text-[#ffcb6b]" : ""}`}>
              <CalendarDays size={13} /> {opportunity.daysRemaining} days left
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin size={13} /> {opportunity.location}
            </span>
            {opportunity.remote && (
              <span className="flex items-center gap-1.5">
                <Globe2 size={13} /> Remote
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <Sparkles size={13} /> {opportunity.funding}
            </span>
          </div>

          <div className="mt-4 flex items-center justify-between gap-3 border-t border-white/[.055] pt-3.5">
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              {opportunity.verified && (
                <span className="flex items-center gap-1 text-[10px] font-bold text-[#69f0c0]">
                  <CheckCircle2 size={12} /> Official source
                </span>
              )}
              <span className="truncate text-[10px] text-[#60736e]">
                Checked {opportunity.lastChecked}
              </span>
            </div>
            <Link
              to={`/opportunities/${opportunity.id}`}
              className="flex shrink-0 items-center gap-1 text-[10px] font-bold text-[#d5ff69] transition hover:text-white"
            >
              View details <ArrowUpRight size={13} />
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}
