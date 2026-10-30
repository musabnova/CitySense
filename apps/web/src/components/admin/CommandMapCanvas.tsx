"use client";

import React, { useEffect, useRef, useState } from "react";
import { ReportItem } from "./IncidentDetailPanel";
import { ClusterItem } from "./ActionBriefModal";

interface CommandMapCanvasProps {
  reports: ReportItem[];
  hotspots: ClusterItem[];
  selectedReport?: ReportItem | null;
  onSelectReport: (report: ReportItem) => void;
  onSelectCluster: (cluster: ClusterItem) => void;
  className?: string;
}

export const CommandMapCanvas: React.FC<CommandMapCanvasProps> = ({
  reports,
  hotspots,
  selectedReport,
  onSelectReport,
  onSelectCluster,
  className = "",
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [hoveredReport, setHoveredReport] = useState<ReportItem | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  // Initialize MapLibre GL JS Map
  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      if (!mapContainerRef.current) return;

      try {
        const maplibregl = (await import("maplibre-gl")).default;
        try {
          // @ts-ignore
          await import("maplibre-gl/dist/maplibre-gl.css");
        } catch (_) {}

        if (!isMounted || !mapContainerRef.current) return;

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: {
            version: 8,
            sources: {
              osm: {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution: "© OpenStreetMap contributors",
              },
            },
            layers: [
              {
                id: "osm-tiles",
                type: "raster",
                source: "osm",
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: [77.595, 12.972], // Bangalore Ward 12 Center
          zoom: 15,
        });

        mapInstanceRef.current = map;

        map.on("load", () => {
          // Add Hotspot Polygons Layer
          if (hotspots.length > 0) {
            const features = hotspots
              .filter((h) => h.boundary_geojson)
              .map((h) => ({
                type: "Feature" as const,
                geometry: h.boundary_geojson,
                properties: { cluster_id: h.cluster_id, title: h.title },
              }));

            map.addSource("hotspots-source", {
              type: "geojson",
              data: {
                type: "FeatureCollection",
                features: features,
              },
            });

            // Fill Layer: rgba(197, 48, 48, 0.12)
            map.addLayer({
              id: "hotspots-fill",
              type: "fill",
              source: "hotspots-source",
              paint: {
                "fill-color": "#C53030",
                "fill-opacity": 0.12,
              },
            });

            // Dashed Border Layer: #C53030
            map.addLayer({
              id: "hotspots-border",
              type: "line",
              source: "hotspots-source",
              paint: {
                "line-color": "#C53030",
                "line-width": 2,
                "line-dasharray": [3, 2],
              },
            });

            map.on("click", "hotspots-fill", (e: any) => {
              const clusterId = e.features?.[0]?.properties?.cluster_id;
              const matched = hotspots.find((h) => h.cluster_id === clusterId);
              if (matched) onSelectCluster(matched);
            });
          }
        });
      } catch (err) {
        console.warn("MapLibre GL desktop canvas fallback:", err);
      }
    }

    initMap();

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update incident markers when reports change
  useEffect(() => {
    async function updateMarkers() {
      if (!mapInstanceRef.current) return;
      const maplibregl = (await import("maplibre-gl")).default;

      // Remove existing markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      reports.forEach((r) => {
        const el = document.createElement("div");
        el.className = "cursor-pointer transition-transform hover:scale-130";

        // Priority Color Mapping
        let color = "#0D9488"; // Mint (Low)
        if (r.priority_rank === "Priority 1") color = "#C53030"; // Rust red (High)
        else if (r.priority_rank === "Priority 2" || r.priority_rank === "Priority 3")
          color = "#B45309"; // Gold (Medium)

        const isSelected = selectedReport?.id === r.id;

        el.innerHTML = `
          <div style="
            width: ${isSelected ? "20px" : "14px"};
            height: ${isSelected ? "20px" : "14px"};
            border-radius: 50%;
            background-color: ${color};
            border: 2px solid #FFFFFF;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
          "></div>
        `;

        el.addEventListener("click", () => {
          onSelectReport(r);
        });

        el.addEventListener("mouseenter", (e) => {
          setHoveredReport(r);
          setTooltipPos({ x: e.clientX, y: e.clientY });
        });

        el.addEventListener("mouseleave", () => {
          setHoveredReport(null);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([r.longitude, r.latitude])
          .addTo(mapInstanceRef.current);

        markersRef.current.push(marker);
      });
    }

    updateMarkers();
  }, [reports, selectedReport]);

  // Center map on selected report
  useEffect(() => {
    if (selectedReport && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo({
        center: [selectedReport.longitude, selectedReport.latitude],
        zoom: 17,
        speed: 1.2,
      });
    }
  }, [selectedReport]);

  return (
    <div className={`relative w-full h-full bg-[#EAEFEA] ${className}`}>
      {/* Map Canvas Layer */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-map" />

      {/* Floating Hotspot Cluster Labels Layer */}
      <div className="absolute top-24 left-1/2 -translate-x-1/2 z-pins flex flex-wrap items-center gap-3 pointer-events-none">
        {hotspots.map((cluster) => (
          <button
            key={cluster.cluster_id}
            type="button"
            data-testid={`hotspot-capsule-${cluster.cluster_id}`}
            onClick={() => onSelectCluster(cluster)}
            className="pointer-events-auto inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold text-white shadow-floating border border-red-500/40 hover:scale-105 transition-all select-none cursor-pointer"
            style={{ backgroundColor: "#1E293B" }}
          >
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
            <span>
              {cluster.cluster_id === "cluster-mg-road-corridor"
                ? "MG Road Hotspot - 8 Reports"
                : `${cluster.title} - ${cluster.total_reports} Reports`}
            </span>
          </button>
        ))}
      </div>

      {/* Interactive Hover Tooltip */}
      {hoveredReport && tooltipPos && (
        <div
          data-testid="map-hover-tooltip"
          className="fixed z-popover pointer-events-none -translate-x-1/2 -translate-y-full mb-3 p-2.5 bg-slate-900/95 text-white rounded-xl shadow-floating text-xs border border-slate-700 backdrop-blur-xs space-y-0.5 animate-in fade-in duration-100"
          style={{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y - 10}px` }}
        >
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-teal-400">
              {hoveredReport.tracking_id}
            </span>
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">
              {hoveredReport.priority_rank}
            </span>
          </div>
          <div className="font-medium text-slate-200 max-w-xs truncate">
            {hoveredReport.concise_summary || hoveredReport.raw_description.slice(0, 60)}
          </div>
        </div>
      )}
    </div>
  );
};

export default CommandMapCanvas;
