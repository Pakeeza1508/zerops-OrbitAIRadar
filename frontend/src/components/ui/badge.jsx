import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "./utils";

const badgeVariants = cva("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors", {
  variants: {
    variant: {
      default: "border-transparent bg-slate-950 text-white",
      secondary: "border-transparent bg-slate-100 text-slate-700",
      blue: "border-blue-100 bg-blue-50 text-blue-700",
      success: "border-emerald-100 bg-emerald-50 text-emerald-700",
      warning: "border-amber-100 bg-amber-50 text-amber-700",
      destructive: "border-red-100 bg-red-50 text-red-700",
      outline: "border-slate-200 bg-white text-slate-700",
    },
  },
  defaultVariants: { variant: "default" },
});

function Badge({ className, variant, ...props }) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
export { Badge, badgeVariants };
