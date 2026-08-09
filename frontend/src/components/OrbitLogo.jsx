import { Radar } from "lucide-react";

export default function OrbitLogo({ compact = false, inverse = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative h-10 w-10 shrink-0">
        <div className={`absolute inset-[6px] rounded-full border ${inverse ? "border-[#d5ff69]/70" : "border-[#61736e]"}`} />
        <div className={`absolute inset-0 rotate-[24deg] rounded-full border ${inverse ? "border-white/10" : "border-slate-300"}`} />
        <span className={`absolute right-[2px] top-[8px] h-2 w-2 rounded-full ${inverse ? "bg-[#d5ff69] shadow-[0_0_14px_#d5ff69]" : "bg-slate-950"}`} />
        <Radar size={14} className="absolute inset-0 m-auto opacity-0" aria-hidden="true" />
      </div>
      {!compact && (
        <div className="leading-none">
          <div className={`font-display text-[17px] font-extrabold tracking-tight ${inverse ? "text-white" : "text-slate-950"}`}>
            ORBIT
          </div>
          <div className={`mt-1 text-[9px] font-semibold uppercase tracking-[.24em] ${inverse ? "text-[#6f8580]" : "text-slate-400"}`}>
            Opportunity Radar
          </div>
        </div>
      )}
    </div>
  );
}
