'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { MapContainer, TileLayer, Marker, Tooltip, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom Map Pin Icon using Lucide styling
const createCustomIcon = (isSelected: boolean, isHovered: boolean) => {
  const color = isSelected ? '#3b82f6' : isHovered ? '#60a5fa' : '#ef4444';
  const size = isSelected || isHovered ? 40 : 30;
  
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5)); transition: all 0.3s ease;">
      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
      <circle cx="12" cy="10" r="3" fill="white"></circle>
    </svg>`,
    iconSize: [size, size],
    iconAnchor: [size/2, size],
    popupAnchor: [0, -size]
  });
};

// Component to handle map camera movements based on Zustand state
function MapController() {
  const map = useMap();
  const { cityCoords, selectedRestaurant } = useAppStore();

  useMapEvents({
    zoomend: () => {
      // If the user zooms out significantly, transition back to the 3D globe
      if (map.getZoom() < 10) {
        // Tell the globe to restore camera at the city, at an altitude based on current map zoom
        const currentZoom = map.getZoom();
        // Map zoom 9 = ~altitude 0.5, zoom 8 = ~altitude 1.0
        const altitudeMap: Record<number, number> = { 9: 0.4, 8: 0.6, 7: 1.0, 6: 1.5, 5: 2.0 };
        const restoreAlt = altitudeMap[currentZoom] ?? 0.6;
        useAppStore.getState().setGlobeRestoreAltitude(restoreAlt);
        useAppStore.getState().setViewMode('globe');
      }
    }
  });

  useEffect(() => {
    if (selectedRestaurant) {
      map.flyTo([selectedRestaurant.latitude, selectedRestaurant.longitude], 16, { duration: 1.5 });
    } else if (cityCoords) {
      map.flyTo([cityCoords.lat, cityCoords.lng], 13, { duration: 1.5 });
    }
  }, [cityCoords, selectedRestaurant, map]);

  return null;
}

export default function MapView() {
  const { restaurants, cityCoords, selectedRestaurant, hoveredRestaurant, setSelectedRestaurant, setHoveredRestaurant } = useAppStore();

  if (!cityCoords) return null;

  return (
    <div className="absolute inset-0 z-0 bg-black">
      <MapContainer 
        center={[cityCoords.lat, cityCoords.lng]} 
        zoom={13} 
        zoomControl={false}
        className="w-full h-full"
        style={{ background: '#0a0a0a' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapController />

        {restaurants.map((restaurant, idx) => (
          <Marker 
            key={idx}
            position={[restaurant.latitude, restaurant.longitude]}
            icon={createCustomIcon(
              selectedRestaurant?.name === restaurant.name,
              hoveredRestaurant?.name === restaurant.name
            )}
            eventHandlers={{
              click: () => {
                window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(restaurant.name + ' ' + restaurant.address)}`, '_blank');
              },
              mouseover: () => setHoveredRestaurant(restaurant),
              mouseout: () => setHoveredRestaurant(null)
            }}
          >
            <Tooltip 
              permanent 
              direction="right" 
              offset={[15, -15]}
              className={`custom-tooltip ${hoveredRestaurant?.name === restaurant.name ? 'tooltip-hovered' : ''}`}
            >
              <div className="font-sans">
                <div className="font-bold whitespace-nowrap">{restaurant.name}</div>
                <div className="text-yellow-400 text-xs mt-0.5">★ {restaurant.avg_rating}</div>
              </div>
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>

      {/* Global override for Leaflet tooltip styles to make it look premium */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-leaflet-marker {
          background: transparent;
          border: none;
        }
        .leaflet-tooltip.custom-tooltip {
          background: rgba(0, 0, 0, 0.7);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          color: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
          backdrop-filter: blur(4px);
          padding: 6px 10px;
          transition: all 0.2s ease;
        }
        .leaflet-tooltip.custom-tooltip::before {
          border-right-color: rgba(0, 0, 0, 0.7);
        }
        .leaflet-tooltip.custom-tooltip.tooltip-hovered {
          background: rgba(59, 130, 246, 0.9);
          border-color: rgba(96, 165, 250, 0.5);
          transform: scale(1.05);
          z-index: 1000 !important;
        }
        .leaflet-tooltip.custom-tooltip.tooltip-hovered::before {
          border-right-color: rgba(59, 130, 246, 0.9);
        }
      `}} />
    </div>
  );
}
