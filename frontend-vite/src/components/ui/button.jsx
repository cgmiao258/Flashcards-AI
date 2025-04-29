import * as React from "react";
import { cn } from "../../lib/utils"; // Adjust path if using aliases

const buttonVariants = {
  default: "bg-black text-white hover:bg-neutral-800",
  outline: "border border-gray-300 bg-white text-black hover:bg-gray-50",
  destructive: "bg-red-500 text-white hover:bg-red-600",
  ghost: "hover:bg-gray-100 text-gray-800",
};

const Button = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium px-4 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:pointer-events-none",
        buttonVariants[variant],
        className
      )}
      {...props}
    />
  );
});
Button.displayName = "Button";

export { Button };
