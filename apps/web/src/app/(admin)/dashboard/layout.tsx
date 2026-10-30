import React from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CitySense Command Console | Municipal GIS Triage",
  description: "Administrative spatial command center for municipal asset management, AI triage, and work order dispatch.",
};

export default function AdminDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="w-screen h-screen overflow-hidden bg-[#EAEFEA] relative flex flex-col font-sans select-none">
      {children}
    </div>
  );
}

