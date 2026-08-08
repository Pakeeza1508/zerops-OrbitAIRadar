export default function MetricCard({ label, value, hint, icon: Icon, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-950 text-white",
    blue: "bg-blue-600 text-white",
    amber: "bg-amber-50 text-amber-950 border-amber-100",
    white: "bg-white text-slate-950 border-slate-200",
  };
  return (
    <div className={`rounded-2xl border p-5 shadow-sm ${tones[tone]}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={`text-xs font-semibold uppercase tracking-[0.14em] ${tone === "slate" || tone === "blue" ? "text-white/60" : "text-slate-500"}`}>{label}</p>
          <p className="mt-3 text-3xl font-black tracking-tight">{value}</p>
          {hint && <p className={`mt-1.5 text-xs ${tone === "slate" || tone === "blue" ? "text-white/60" : "text-slate-500"}`}>{hint}</p>}
        </div>
        {Icon && (
          <div className={`grid h-10 w-10 place-items-center rounded-xl ${tone === "slate" || tone === "blue" ? "bg-white/10" : "bg-slate-100"}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
    </div>
  );
}
