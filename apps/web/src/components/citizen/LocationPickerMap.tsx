"use client";

import React, { useEffect, useRef, useState } from "react";

interface LocationPickerMapProps {
  latitude: number;
  longitude: number;
  onChange: (lat: number, lon: number, address?: string) => void;
  className?: string;
}

export const LocationPickerMap: React.FC<LocationPickerMapProps> = ({
  latitude,
  longitude,
  onChange,
  className = "",
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  const [locating, setLocating] = useState(false);
  const [accuracy, setAccuracy] = useState<number | null>(15);
  const [geoError, setGeoError] = useState<string | null>(null);
  const [coords, setCoords] = useState<{ lat: number; lon: number }>({
    lat: latitude,
    lon: longitude,
  });

  // Initialize MapLibre GL JS safely on client
  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      if (!mapContainerRef.current) return;

      try {
        const maplibregl = (await import("maplibre-gl")).default;
        // Import maplibre css if available
        try {
          // @ts-ignore
          await import("maplibre-gl/dist/maplibre-gl.css");
        } catch (_) {}

        if (!isMounted || !mapContainerRef.current) return;

        // Custom soft-mint vector style or open raster style
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
                id: "osm-layer",
                type: "raster",
                source: "osm",
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: [longitude, latitude],
          zoom: 16,
        });

        mapInstanceRef.current = map;

        // Add Center Pin Marker
        const el = document.createElement("div");
        el.className = "w-8 h-8 flex items-center justify-center cursor-pointer";
        el.innerHTML = `
          <div style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#C53030" stroke="#FFFFFF" stroke-width="2">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
              <circle cx="12" cy="9" r="2.5" fill="#FFFFFF"/>
            </svg>
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el, draggable: true })
          .setLngLat([longitude, latitude])
          .addTo(map);

        markerRef.current = marker;

        marker.on("dragend", () => {
          const lngLat = marker.getLngLat();
          setCoords({ lat: lngLat.lat, lon: lngLat.lng });
          onChange(lngLat.lat, lngLat.lng);
        });

        map.on("click", (e: any) => {
          marker.setLngLat(e.lngLat);
          setCoords({ lat: e.lngLat.lat, lon: e.lngLat.lng });
          onChange(e.lngLat.lat, e.lngLat.lng);
        });
      } catch (err) {
        console.warn("MapLibre GL initialization fallback:", err);
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

  // Update marker position if props change externally
  useEffect(() => {
    if (markerRef.current && mapInstanceRef.current) {
      markerRef.current.setLngLat([longitude, latitude]);
      mapInstanceRef.current.flyTo({ center: [longitude, latitude] });
    }
    setCoords({ lat: latitude, lon: longitude });
  }, [latitude, longitude]);

  // "Use My Location" Geolocation Trigger
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError("Geolocation is not supported by your browser.");
      return;
    }

    setLocating(true);
    setGeoError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocating(false);
        const { latitude: userLat, longitude: userLon, accuracy: acc } = pos.coords;
        setAccuracy(Math.round(acc));
        setCoords({ lat: userLat, lon: userLon });
        onChange(userLat, userLon, `Ward 12 Municipal Corridor [GPS ±${Math.round(acc)}m]`);

        if (mapInstanceRef.current) {
          mapInstanceRef.current.flyTo({
            center: [userLon, userLat],
            zoom: 17,
            speed: 1.4,
          });
        }
        if (markerRef.current) {
          markerRef.current.setLngLat([userLon, userLat]);
        }
      },
      (err) => {
        setLocating(false);
        setGeoError(err.message || "Unable to acquire GPS coordinates.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  return (
    <div className={`relative w-full h-full min-h-[360px] bg-[#EAEFEA] overflow-hidden ${className}`}>
      {/* Map Container */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-map" />

      {/* Accuracy circle badge & coordinate display */}
      <div className="absolute top-4 left-4 z-floating bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-200/80 shadow-subtle flex items-center gap-2 text-xs">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="font-semibold text-slate-700">
          {coords.lat.toFixed(4)}, {coords.lon.toFixed(4)}
        </span>
        {accuracy !== null && (
          <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded-full">
            ±{accuracy}m
          </span>
        )}
      </div>

      {/* Floating "Use My Location" Button */}
      <div className="absolute top-4 right-4 z-floating">
        <button
          type="button"
          onClick={handleUseMyLocation}
          disabled={locating}
          data-testid="use-my-location-button"
          className="bg-white hover:bg-slate-50 active:bg-slate-100 text-[#0B6B61] border border-slate-200 shadow-floating px-3.5 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all select-none cursor-pointer focus:ring-2 focus:ring-[#0B6B61]"
        >
          <svg
            className={`w-4 h-4 text-[#0B6B61] ${locating ? "animate-spin" : ""}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v3m0 14v3M2 12h3m14 0h3" />
          </svg>
          <span>{locating ? "Locating..." : "Use My Location"}</span>
        </button>
      </div>

      {/* GPS Error Alert */}
      {geoError && (
        <div className="absolute top-16 left-4 right-4 z-floating bg-amber-50 border border-amber-200 text-amber-800 text-xs px-3 py-2 rounded-xl shadow-subtle flex items-center justify-between">
          <span>{geoError}</span>
          <button onClick={() => setGeoError(null)} className="font-bold ml-2">✕</button>
        </div>
      )}
    </div>
  );
};

export default LocationPickerMap;
