export default function MetricCard({ label, value, hint, icon: Icon, tone = "slate" }) {
  const accent = {
    slate: "text-[#d5ff69]",
    blue: "text-[#76baff]",
    amber: "text-[#ffcb6b]",
    white: "text-[#69f0c0]",
  }[tone] || "text-[#d5ff69]";

  return (
    <div className="orbit-panel rounded-2xl border border-white/[.075] bg-[#0c1715] p-4 shadow-[inset_0_1px_rgba(255,255,255,.02),0_14px_35px_rgba(0,0,0,.14)]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-[#738781]">{label}</p>
          <div className="mt-3 flex items-end gap-2">
            <p className="font-display text-2xl font-extrabold tracking-tight text-white">{value}</p>
            {hint && <p className={`mb-1 truncate text-[10px] ${accent}`}>{hint}</p>}
          </div>
        </div>
        {Icon && (
          <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl border border-white/[.06] bg-white/[.025] text-[#738781]">
            <Icon size={15} />
          </div>
        )}
      </div>
    </div>
  );
}
