"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const Navigation = () => {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Home" },
    { href: "/settings", label: "Settings" },
  ];

  return (
    <nav className="flex items-center space-x-4 lg:space-x-6 mb-8">
      {links.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === href
              ? "text-black dark:text-white"
              : "text-muted-foreground"
          )}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
};

export default Navigation;
