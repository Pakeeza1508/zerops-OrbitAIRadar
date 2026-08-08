import { GripVertical } from "lucide-react";
import * as ResizablePrimitive from "react-resizable-panels";
import { cn } from "./utils";
const ResizablePanelGroup = ({ className, ...props }) => <ResizablePrimitive.PanelGroup className={cn("flex h-full w-full data-[panel-group-direction=vertical]:flex-col", className)} {...props} />;
const ResizablePanel = ResizablePrimitive.Panel;
const ResizableHandle = ({ withHandle, className, ...props }) => <ResizablePrimitive.PanelResizeHandle className={cn("relative flex w-px items-center justify-center bg-slate-200 after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 data-[panel-group-direction=vertical]:h-px data-[panel-group-direction=vertical]:w-full", className)} {...props}>{withHandle && <div className="z-10 flex h-4 w-3 items-center justify-center rounded-sm border border-slate-200 bg-white"><GripVertical className="h-2.5 w-2.5" /></div>}</ResizablePrimitive.PanelResizeHandle>;
export { ResizablePanelGroup, ResizablePanel, ResizableHandle };
