import React from "react";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "CitySense | Field Portal",
  description: "Field crew work order management and resolution portal.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#1E293B",
};

export default function FieldLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // High-contrast dark mobile shell for outdoor field use
    <div className="min-h-screen bg-[#0F172A] flex justify-center items-start sm:p-4">
      <div className="w-full max-w-md mx-auto min-h-screen sm:min-h-[844px] bg-[#1E293B] relative flex flex-col">
        {/* Field Portal Top Bar */}
        <div className="flex items-center justify-between px-5 py-3 bg-[#0B6B61] border-b border-[#08544C]">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center text-white font-bold text-xs">
              🔧
            </div>
            <div>
              <div className="text-white font-bold text-sm leading-none">
                CitySense Field Portal
              </div>
              <div className="text-[#A8DADC] text-[10px] font-medium">
                Work Order Management
              </div>
            </div>
          </div>
          <div className="text-[10px] font-bold text-[#A8DADC] uppercase tracking-wider bg-white/10 px-2.5 py-1 rounded-full">
            Field Lead
          </div>
        </div>

        {/* Content Viewport */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}

