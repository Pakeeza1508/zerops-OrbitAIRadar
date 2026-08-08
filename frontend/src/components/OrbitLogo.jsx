import { Radar } from "lucide-react";

export default function OrbitLogo({ compact = false, inverse = false }) {
  return (
    <div className="flex items-center gap-2.5">
      <div className={`grid h-9 w-9 place-items-center rounded-xl ${inverse ? "bg-white text-slate-950" : "bg-slate-950 text-white"}`}>
        <Radar size={18} strokeWidth={2.2} />
      </div>
      {!compact && (
        <div className="leading-none">
          <div className={`text-[15px] font-black tracking-[0.16em] ${inverse ? "text-white" : "text-slate-950"}`}>ORBIT</div>
          <div className={`mt-1 text-[9px] font-semibold tracking-[0.14em] ${inverse ? "text-slate-400" : "text-slate-400"}`}>OPPORTUNITY RADAR</div>
        </div>
      )}
    </div>
  );
}
