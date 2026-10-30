import React from "react";
import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "CitySense | Civic Impact Platform",
  description: "AI-Powered Civic Impact Platform - From Complaints to Action",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#F8FAFC] text-[#1E293B] antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}

