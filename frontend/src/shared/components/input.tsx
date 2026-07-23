import * as React from "react";
import { cn } from "../lib/utils";
import { Input as ShadcnInput } from "./ui/input";

interface InputProps extends React.ComponentProps<"input"> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Input({ className, leftIcon, rightIcon, ...props }: InputProps) {
  return (
    <div className="relative flex items-center justify-center w-full">
      {/* Left Icon */}
      {leftIcon && (
        <div className="absolute left-3 flex items-center justify-center text-muted-foreground">
          {leftIcon}
        </div>
      )}

      <ShadcnInput
        className={cn(
          "h-auto px-4 py-3.5 rounded-2xl",
          "text-[#1A1A2E] placeholder:text-[#1A1A2E]/50",
          leftIcon && "pl-11",
          rightIcon && "pr-11",
          className,
        )}
        {...props}
      />

      {/* Right Icon */}
      {rightIcon && (
        <div className="absolute right-3 flex items-center justify-center text-muted-foreground">
          {rightIcon}
        </div>
      )}
    </div>
  );
}