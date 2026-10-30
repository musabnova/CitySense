"use client";

import React from "react";
import { ClusterItem } from "./ActionBriefModal";

interface HotspotClusterLayerProps {
  hotspots: ClusterItem[];
  onSelectCluster: (cluster: ClusterItem) => void;
  className?: string;
}

export const HotspotClusterLayer: React.FC<HotspotClusterLayerProps> = ({
  hotspots,
  onSelectCluster,
  className = "",
}) => {
  return (
    <div data-testid="hotspot-cluster-layer" className={`pointer-events-none ${className}`}>
      {hotspots.map((cluster) => {
        const isMgRoad =
          cluster.cluster_id === "cluster-mg-road-corridor" ||
          cluster.title.toLowerCase().includes("mg road");

        return (
          <div
            key={cluster.cluster_id}
            onClick={() => onSelectCluster(cluster)}
            className="pointer-events-auto cursor-pointer group transition-transform hover:scale-105"
          >
            {/* Hotspot Floating Capsule Label */}
            <div
              data-testid={`hotspot-label-${cluster.cluster_id}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white shadow-floating border border-red-500/30 transition-all select-none"
              style={{
                backgroundColor: "#1E293B",
              }}
            >
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
              <span>
                {isMgRoad ? "MG Road Hotspot - 8 Reports" : `${cluster.title} - ${cluster.total_reports} Reports`}
              </span>
              <span className="text-[10px] text-red-300 ml-1">⚡ Inspect</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default HotspotClusterLayer;

