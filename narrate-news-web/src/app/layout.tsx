import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Suspense } from 'react';
import { LoadingSkeleton } from '@/components/LoadingSkeleton';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ThemeToggle } from "@/components/ThemeToggle";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Narrate News",
  description: "Listen to your favorite news articles",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SidebarProvider>
            <div className="flex relative">
              <div className="fixed left-0 h-full z-50">
                <AppSidebar />
              </div>
              <main className="flex-1 min-h-screen w-full">
                <div className="flex flex-col items-center w-full">
                  <div className="absolute left-4 top-4 z-40">
                    <SidebarTrigger />
                  </div>
                  <div className="w-full max-w-[1024px] px-4 mx-auto">
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSkeleton />}>
                        <div className="transition-opacity duration-200 ease-in-out pt-16">
                          {children}
                        </div>
                      </Suspense>
                    </ErrorBoundary>
                  </div>
                </div>
              </main>
            </div>
            <ThemeToggle />
            <Toaster />
          </SidebarProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
