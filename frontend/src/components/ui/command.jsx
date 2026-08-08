import * as React from "react";
import { Command as CommandPrimitive } from "cmdk";
import { Search } from "lucide-react";
import { cn } from "./utils";
import { Dialog, DialogContent } from "./dialog";

const Command = React.forwardRef(({ className, ...props }, ref) => <CommandPrimitive ref={ref} className={cn("flex h-full w-full flex-col overflow-hidden rounded-2xl bg-white text-slate-950", className)} {...props} />);
Command.displayName = CommandPrimitive.displayName;
function CommandDialog({ children, ...props }) { return <Dialog {...props}><DialogContent className="overflow-hidden p-0 shadow-2xl"><Command className="[&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-semibold [&_[cmdk-group-heading]]:text-slate-500">{children}</Command></DialogContent></Dialog>; }
const CommandInput = React.forwardRef(({ className, ...props }, ref) => <div className="flex items-center border-b border-slate-100 px-4" cmdk-input-wrapper=""><Search className="mr-2 h-4 w-4 shrink-0 text-slate-400" /><CommandPrimitive.Input ref={ref} className={cn("flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-50", className)} {...props} /></div>);
CommandInput.displayName = CommandPrimitive.Input.displayName;
const CommandList = React.forwardRef(({ className, ...props }, ref) => <CommandPrimitive.List ref={ref} className={cn("max-h-[300px] overflow-y-auto overflow-x-hidden", className)} {...props} />);
CommandList.displayName = CommandPrimitive.List.displayName;
const CommandEmpty = React.forwardRef((props, ref) => <CommandPrimitive.Empty ref={ref} className="py-8 text-center text-sm text-slate-500" {...props} />);
CommandEmpty.displayName = CommandPrimitive.Empty.displayName;
const CommandGroup = React.forwardRef(({ className, ...props }, ref) => <CommandPrimitive.Group ref={ref} className={cn("overflow-hidden p-2 text-slate-950 [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-semibold [&_[cmdk-group-heading]]:text-slate-500", className)} {...props} />);
CommandGroup.displayName = CommandPrimitive.Group.displayName;
const CommandSeparator = React.forwardRef(({ className, ...props }, ref) => <CommandPrimitive.Separator ref={ref} className={cn("-mx-1 h-px bg-slate-100", className)} {...props} />);
CommandSeparator.displayName = CommandPrimitive.Separator.displayName;
const CommandItem = React.forwardRef(({ className, ...props }, ref) => <CommandPrimitive.Item ref={ref} className={cn("relative flex cursor-default select-none items-center rounded-lg px-3 py-2 text-sm outline-none data-[disabled=true]:pointer-events-none data-[selected=true]:bg-slate-100 data-[disabled=true]:opacity-50", className)} {...props} />);
CommandItem.displayName = CommandPrimitive.Item.displayName;
const CommandShortcut = ({ className, ...props }) => <span className={cn("ml-auto text-xs tracking-widest text-slate-400", className)} {...props} />;
export { Command, CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem, CommandShortcut, CommandSeparator };
