"use client";

import React, { useState, useRef } from "react";

interface SlidingBottomSheetProps {
  children: React.ReactNode;
  rawDescription: string;
  onDescriptionChange: (text: string) => void;
  selectedPhoto: File | null;
  onPhotoSelected: (file: File | null) => void;
  className?: string;
}

export const SlidingBottomSheet: React.FC<SlidingBottomSheetProps> = ({
  children,
  rawDescription,
  onDescriptionChange,
  selectedPhoto,
  onPhotoSelected,
  className = "",
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onPhotoSelected(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleRemovePhoto = () => {
    onPhotoSelected(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <section
      data-testid="sliding-bottom-sheet"
      className={`w-full bg-white rounded-t-[24px] shadow-modal z-modal flex flex-col transition-all duration-300 relative border-t border-slate-100 ${className}`}
      style={{
        boxShadow: "0px -4px 32px rgba(0, 0, 0, 0.12)",
      }}
    >
      {/* Top Grab Handle Bar */}
      <div className="w-full flex items-center justify-center pt-3 pb-2 cursor-grab select-none">
        <div
          data-testid="grab-handle"
          className="w-[36px] h-[4px] rounded-full bg-[#CBD5E1]"
        />
      </div>

      <div className="px-5 pb-6 space-y-4">
        {/* Main Title & Problem Description Area */}
        <div className="space-y-1.5">
          <label
            htmlFor="incident-description"
            className="block text-section font-bold text-[#1E293B]"
          >
            What is the problem?
          </label>
          <textarea
            id="incident-description"
            data-testid="incident-description-input"
            rows={3}
            value={rawDescription}
            onChange={(e) => onDescriptionChange(e.target.value)}
            placeholder="Describe the failure, hazard, or municipal issue..."
            className="w-full p-3.5 rounded-xl border border-slate-200 text-body text-[#1E293B] placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B6B61] focus:border-transparent transition-all resize-none text-sm bg-slate-50/50"
          />
        </div>

        {/* Photo Upload & Instant Thumbnail Preview */}
        <div className="flex items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            className="hidden"
            id="camera-file-input"
            data-testid="camera-file-input"
          />

          <label
            htmlFor="camera-file-input"
            data-testid="add-photo-button"
            className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-full border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold cursor-pointer shadow-subtle transition-all select-none min-h-[44px]"
          >
            <svg
              className="w-4 h-4 text-[#0B6B61]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            <span>{selectedPhoto ? "Change Photo" : "Add Photo"}</span>
          </label>

          {/* Instant Thumbnail Preview */}
          {previewUrl && (
            <div
              data-testid="photo-thumbnail-container"
              className="relative w-12 h-12 rounded-lg overflow-hidden border-2 border-[#0B6B61] shadow-subtle group"
            >
              <img
                src={previewUrl}
                alt="Selected evidence thumbnail"
                data-testid="photo-thumbnail"
                className="w-full h-full object-cover"
              />
              <button
                type="button"
                onClick={handleRemovePhoto}
                title="Remove photo"
                className="absolute top-0 right-0 bg-red-600/80 text-white w-4 h-4 rounded-bl flex items-center justify-center text-[10px] font-bold"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Children Slots: Category Selector, AI Suggestion Banner & Submit Button */}
        {children}
      </div>
    </section>
  );
};

export default SlidingBottomSheet;

