import React from "react";
import type { Metadata, Viewport } from "next";
import ServiceWorkerRegister from "@/components/citizen/ServiceWorkerRegister";

export const metadata: Metadata = {
  title: "CitySense | Report & Track Civic Issues",
  description: "Citizen mobile portal for reporting municipal issues and tracking civic action.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "CitySense",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#0B6B61",
};

export default function CitizenLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-900 flex justify-center items-center sm:p-4">
      {/* PWA Service Worker Registration */}
      <ServiceWorkerRegister />

      {/* Mobile Frame Container below 768px */}
      <div className="w-full max-w-md mx-auto min-h-screen sm:min-h-[844px] sm:max-h-[844px] sm:rounded-[36px] bg-[#F8FAFC] relative overflow-hidden flex flex-col shadow-2xl border-0 sm:border-8 sm:border-slate-800">
        {/* iOS style top status notch on framed desktop view */}
        <div className="hidden sm:flex justify-between items-center px-6 pt-3 pb-1 text-xs font-semibold text-slate-700 bg-transparent select-none z-50">
          <span>9:41</span>
          <div className="w-20 h-4 bg-slate-800 rounded-full" />
          <div className="flex items-center gap-1.5">
            <span className="text-[10px]">5G</span>
            <div className="w-5 h-2.5 border border-slate-700 rounded-xs p-0.5 flex items-center">
              <div className="w-full h-full bg-slate-700 rounded-2xs" />
            </div>
          </div>
        </div>

        {/* Content Viewport */}
        <div className="flex-1 relative overflow-y-auto overflow-x-hidden flex flex-col">
          {children}
        </div>
      </div>
    </div>
  );
}

