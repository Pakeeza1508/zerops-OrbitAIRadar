import { Toaster as Sonner } from "sonner";
export function Toaster(props) {
  return <Sonner position="top-right" richColors closeButton toastOptions={{ classNames: { toast: "rounded-2xl border border-slate-200 bg-white shadow-xl", title: "text-slate-950", description: "text-slate-500" } }} {...props} />;
}
