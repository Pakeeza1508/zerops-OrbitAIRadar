import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { DayPicker } from "react-day-picker";
import { cn } from "./utils";
import { buttonVariants } from "./button";

function Calendar({ className, classNames, showOutsideDays = true, ...props }) {
  return <DayPicker showOutsideDays={showOutsideDays} className={cn("p-3", className)} classNames={{ months: "flex flex-col sm:flex-row gap-4", month: "space-y-4", caption: "flex justify-center pt-1 relative items-center", caption_label: "text-sm font-semibold", nav: "space-x-1 flex items-center", nav_button: cn(buttonVariants({ variant: "outline", size: "icon" }), "h-7 w-7 bg-transparent p-0 opacity-60 hover:opacity-100"), nav_button_previous: "absolute left-1", nav_button_next: "absolute right-1", table: "w-full border-collapse space-y-1", head_row: "flex", head_cell: "text-slate-500 rounded-md w-9 font-normal text-[0.8rem]", row: "flex w-full mt-2", cell: "h-9 w-9 text-center text-sm p-0 relative", day: cn(buttonVariants({ variant: "ghost", size: "icon" }), "h-9 w-9 p-0 font-normal aria-selected:opacity-100"), day_selected: "bg-blue-600 text-white hover:bg-blue-600 hover:text-white", day_today: "bg-slate-100 text-slate-950", day_outside: "text-slate-400 opacity-50", day_disabled: "text-slate-400 opacity-50", day_range_middle: "aria-selected:bg-slate-100 aria-selected:text-slate-950", day_hidden: "invisible", ...classNames }} components={{ IconLeft: () => <ChevronLeft className="h-4 w-4" />, IconRight: () => <ChevronRight className="h-4 w-4" /> }} {...props} />;
}
Calendar.displayName = "Calendar";
export { Calendar };
