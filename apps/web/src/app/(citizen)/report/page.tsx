"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import LocationPickerMap from "@/components/citizen/LocationPickerMap";
import SlidingBottomSheet from "@/components/citizen/SlidingBottomSheet";
import CategorySelector from "@/components/citizen/CategorySelector";
import AISuggestionBanner from "@/components/citizen/AISuggestionBanner";
import ActionButton from "@/components/ui/ActionButton";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportIncidentPage() {
  const router = useRouter();

  // Location State (Defaulting to Ward 12 center)
  const [latitude, setLatitude] = useState(12.9716);
  const [longitude, setLongitude] = useState(77.5946);
  const [address, setAddress] = useState("Ward 12 Municipal Corridor");

  // Form State
  const [rawDescription, setRawDescription] = useState("");
  const [userCategory, setUserCategory] = useState("Waterlogging & Drainage");
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null);

  // Status & Telemetry
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<{
    id: string;
    tracking_id: string;
    created_at: string;
  } | null>(null);

  const handleLocationChange = (lat: number, lon: number, addr?: string) => {
    setLatitude(lat);
    setLongitude(lon);
    if (addr) setAddress(addr);
  };

  const handleSubmit = async () => {
    if (!rawDescription.trim() || rawDescription.trim().length < 5) {
      setErrorMsg("Please provide at least 5 characters describing the problem.");
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_description: rawDescription.trim(),
          latitude,
          longitude,
          user_category: userCategory,
          formatted_address: address,
          media_url: selectedPhoto ? "data:image/jpeg;base64,mockphoto" : null,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Submission failed with HTTP ${response.status}`);
      }

      const data = await response.json();
      setSuccessResult(data);

      // Keep success modal visible; navigate after 5s or let user click CTA
      setTimeout(() => {
        if (data.tracking_id) {
          router.push(`/track/${data.tracking_id}`);
        }
      }, 8000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit report. Ensure the backend server is reachable.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col justify-between">
      {/* 1. Full-Screen Interactive Location Picker (Background Layer) */}
      <div className="flex-1 w-full relative min-h-[320px]">
        <LocationPickerMap
          latitude={latitude}
          longitude={longitude}
          onChange={handleLocationChange}
          className="w-full h-full"
        />
      </div>

      {/* 2. Sliding Bottom Sheet with Incident Form (Foreground Layer) */}
      <SlidingBottomSheet
        rawDescription={rawDescription}
        onDescriptionChange={setRawDescription}
        selectedPhoto={selectedPhoto}
        onPhotoSelected={setSelectedPhoto}
      >
        {/* Category Selector Chips */}
        <CategorySelector
          selectedCategory={userCategory}
          onSelectCategory={setUserCategory}
        />

        {/* Real-Time AI Suggestion Banner */}
        <AISuggestionBanner
          detectedCategory={userCategory.includes("Drainage") ? "Drainage" : userCategory.includes("Road") ? "Road Damage" : "General"}
          detectedPriority="High"
          similarReportsCount={2}
          explanation={`AI classified this issue as ${userCategory} based on incident description and proximity to Ward 12 infrastructure.`}
        />

        {/* Error Alert */}
        {errorMsg && (
          <div
            data-testid="submission-error"
            className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center justify-between"
          >
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="font-bold ml-2">✕</button>
          </div>
        )}

        {/* Primary CTA: Send Report */}
        <div className="pt-1">
          <ActionButton
            type="button"
            variant="primary"
            fullWidth
            isLoading={submitting}
            onClick={handleSubmit}
            data-testid="send-report-button"
          >
            {submitting ? "Submitting Report..." : "Send report"}
          </ActionButton>
        </div>

        {/* Subtle Navigation Links */}
        <div className="pt-2 flex items-center justify-around text-xs text-slate-500 border-t border-slate-100">
          <button
            type="button"
            onClick={() => router.push("/report")}
            className="font-bold text-[#0B6B61] py-1 px-2"
          >
            Report
          </button>
          <button
            type="button"
            onClick={() => router.push("/track/CS-HAZD-1001")}
            className="hover:text-slate-800 py-1 px-2"
          >
            Track Demo Report
          </button>
          <a
            href="/"
            className="hover:text-slate-800 py-1 px-2"
          >
            Design System
          </a>
        </div>
      </SlidingBottomSheet>

      {/* Success Modal Confirmation Dialog */}
      {successResult && (
        <div
          data-testid="submission-success-modal"
          className="fixed inset-0 z-modal flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in"
        >
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 text-center space-y-4 shadow-modal">
            <div className="w-14 h-14 rounded-full bg-[#E1F2EF] text-[#0B6B61] flex items-center justify-center mx-auto text-2xl font-bold">
              ✓
            </div>
            <div className="space-y-1">
              <h3 className="text-display font-bold text-[#1E293B]">
                Report Submitted!
              </h3>
              <p className="text-body text-[#64748B]">
                Your incident has been submitted for municipal triage.
              </p>
            </div>

            {/* Tracking ID Capsule */}
            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Your Tracking ID
              </div>
              <div
                data-testid="success-tracking-id"
                className="text-xl font-mono font-bold text-[#0B6B61]"
              >
                {successResult.tracking_id}
              </div>
            </div>

            <div className="pt-2">
              <ActionButton
                variant="primary"
                fullWidth
                onClick={() => router.push(`/track/${successResult.tracking_id}`)}
              >
                View Status Tracker
              </ActionButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

