"use client";

import React from "react";
import { FilterChip } from "@/components/ui/FilterChip";

export interface CategoryOption {
  id: string;
  label: string;
  backendValue: string;
}

export const CATEGORY_OPTIONS: CategoryOption[] = [
  { id: "drainage", label: "Drainage", backendValue: "Waterlogging & Drainage" },
  { id: "road", label: "Road damage", backendValue: "Road Failure & Potholes" },
  { id: "waste", label: "Waste", backendValue: "Waste Management" },
  { id: "streetlight", label: "Streetlight", backendValue: "Street Lighting" },
  { id: "utilities", label: "Utilities", backendValue: "Public Utilities" },
];

interface CategorySelectorProps {
  selectedCategory: string; // e.g. "Waterlogging & Drainage" or id
  onSelectCategory: (backendValue: string) => void;
  className?: string;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategory,
  onSelectCategory,
  className = "",
}) => {
  return (
    <div className={`space-y-1.5 ${className}`}>
      <span className="text-micro font-bold text-slate-500 uppercase tracking-wider">
        Category
      </span>
      <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-none no-scrollbar">
        {CATEGORY_OPTIONS.map((cat) => {
          const isActive =
            selectedCategory === cat.backendValue || selectedCategory === cat.id;
          return (
            <FilterChip
              key={cat.id}
              label={cat.label}
              active={isActive}
              onClick={() => onSelectCategory(cat.backendValue)}
              className="flex-shrink-0"
            />
          );
        })}
      </div>
    </div>
  );
};

export default CategorySelector;

