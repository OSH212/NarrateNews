"use client"

import { Library, Settings } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <nav className="fixed left-0 top-0 h-full w-12 bg-background border-r flex flex-col items-center py-4 space-y-4">
      {[
        { icon: Library, href: "/", title: "Library" },
        { icon: Settings, href: "/settings", title: "Settings" },
      ].map(({ icon: Icon, href, title }) => (
        <Link
          key={href}
          href={href}
          title={title}
          className={cn(
            "p-2 rounded-md hover:bg-accent transition-colors",
            pathname === href && "bg-accent"
          )}
        >
          <Icon className="h-5 w-5" />
        </Link>
      ))}
    </nav>
  );
}