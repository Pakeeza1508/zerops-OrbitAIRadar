import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "./utils";

const Progress = React.forwardRef(({ className, value = 0, ...props }, ref) => (
  <ProgressPrimitive.Root ref={ref} className={cn("relative h-2 w-full overflow-hidden rounded-full bg-slate-100", className)} {...props}>
    <ProgressPrimitive.Indicator className="h-full w-full flex-1 bg-blue-600 transition-all" style={{ transform: `translateX(-${100 - Math.max(0, Math.min(100, value))}%)` }} />
  </ProgressPrimitive.Root>
));
Progress.displayName = ProgressPrimitive.Root.displayName;
export { Progress };
