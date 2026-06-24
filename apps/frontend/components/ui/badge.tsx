import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "green" | "blue" | "yellow" | "red" | "purple" | "gray";
}

const variants = {
  green: "badge-green",
  blue: "badge-blue",
  yellow: "badge-yellow",
  red: "badge-red",
  purple: "badge-purple",
  gray: "badge-gray",
};

const statusMap: Record<string, string> = {
  active: "green",
  inactive: "gray",
  new: "blue",
  qualified: "purple",
  contacted: "yellow",
  negotiating: "yellow",
  won: "green",
  lost: "red",
  draft: "gray",
  sent: "blue",
  accepted: "green",
  rejected: "red",
  expired: "red",
  completed: "green",
  pending: "yellow",
  cancelled: "red",
};

export function Badge({ className, variant, children, ...props }: BadgeProps) {
  const resolvedVariant = variant || (typeof children === "string" ? statusMap[children.toLowerCase()] : "gray") || "gray";
  return (
    <span className={cn("badge", variants[resolvedVariant as keyof typeof variants] || variants.gray, className)} {...props}>
      {children}
    </span>
  );
}
