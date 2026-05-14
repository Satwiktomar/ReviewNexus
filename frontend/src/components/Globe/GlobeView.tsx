'use client';

import dynamic from 'next/dynamic';
import { useAppStore } from '@/store/useAppStore';
import { useEffect, useRef, useState, useMemo } from 'react';
import { Restaurant } from '@/services/api';

const Globe = dynamic(() => import('react-globe.gl'), { 
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-black/90">
    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
});

/** Compute the Sun's approximate subsolar geographic position from UTC time */
function getSunPosition(): { lat: number; lng: number } {
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const dayOfYear = Math.floor((now.getTime() - start.getTime()) / 86400000);
  const declination = -23.45 * Math.cos((2 * Math.PI * (dayOfYear + 10)) / 365);
  const utcHours = now.getUTCHours() + now.getUTCMinutes() / 60;
  const lng = (utcHours - 12) * -15;
  return { lat: declination, lng };
}

export default function GlobeView() {
  const globeEl = useRef<any>(null);
  const {
    mode, viewMode, cityCoords, restaurants,
    hoveredRestaurant, selectedRestaurant,
    setHoveredRestaurant, setSelectedRestaurant,
    globeRestoreAltitude, setGlobeRestoreAltitude
  } = useAppStore();
  const [isClient, setIsClient] = useState(false);
  const [isRotating, setIsRotating] = useState(true);
  const [sunPos, setSunPos] = useState(getSunPosition());

  useEffect(() => { setIsClient(true); }, []);

  // Update sun position every minute (only in idle to save resources)
  useEffect(() => {
    if (mode !== 'idle') return;
    const t = setInterval(() => setSunPos(getSunPosition()), 60_000);
    return () => clearInterval(t);
  }, [mode]);

  // Restore globe camera when returning from 2D map
  useEffect(() => {
    if (viewMode === 'globe' && globeEl.current && cityCoords && globeRestoreAltitude !== null) {
      globeEl.current.pointOfView(
        { lat: cityCoords.lat, lng: cityCoords.lng, altitude: globeRestoreAltitude },
        0
      );
      setTimeout(() => setGlobeRestoreAltitude(null), 100);
    }
  }, [viewMode, globeRestoreAltitude]);

  // Poll altitude: control rotation and trigger map transition when zoomed close
  useEffect(() => {
    if (!globeEl.current || !isClient) return;
    const iv = setInterval(() => {
      try {
        const pov = globeEl.current.pointOfView();
        setIsRotating(pov.altitude >= 0.5);
        const state = useAppStore.getState();
        if (state.mode === 'results' && state.viewMode === 'globe' && pov.altitude < 0.2) {
          state.setViewMode('map');
        }
      } catch (_) {}
    }, 200);
    return () => clearInterval(iv);
  }, [isClient]);

  // Camera transitions on mode change
  useEffect(() => {
    if (!globeEl.current) return;
    if (mode === 'results' && cityCoords) {
      globeEl.current.pointOfView({ lat: cityCoords.lat, lng: cityCoords.lng, altitude: 0.1 }, 3000);
    } else if (mode === 'idle') {
      globeEl.current.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 3000);
    }
  }, [cityCoords, mode]);

  // Focus on selected restaurant
  useEffect(() => {
    if (selectedRestaurant && globeEl.current) {
      globeEl.current.pointOfView(
        { lat: selectedRestaurant.latitude, lng: selectedRestaurant.longitude, altitude: 0.02 },
        1500
      );
    }
  }, [selectedRestaurant]);

  // Apply auto-rotation logic via controls instead of props (fixes TS error)
  useEffect(() => {
    if (globeEl.current && globeEl.current.controls) {
      try {
        const controls = globeEl.current.controls();
        if (controls) {
          controls.autoRotate = isRotating;
          controls.autoRotateSpeed = mode === 'idle' ? 3.0 : mode === 'searching' ? 4.5 : 0.8;
        }
      } catch (err) {
        // Safe catch if controls aren't mounted yet
      }
    }
  }, [isRotating, mode]);

  const markersData = useMemo(() => {
    if (mode !== 'results') return [];
    return restaurants.map(r => ({
      ...r,
      size: r.score / 10,
      color: r.name === selectedRestaurant?.name
        ? '#3b82f6'
        : r.name === hoveredRestaurant?.name
          ? '#60a5fa'
          : '#ef4444'
    }));
  }, [restaurants, mode, selectedRestaurant, hoveredRestaurant]);

  const createGlobeMarker = (d: any) => {
    const el = document.createElement('div');
    const isFocused = d.name === hoveredRestaurant?.name || d.name === selectedRestaurant?.name;
    const size = isFocused ? 32 : 24;
    el.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24"
        fill="${d.color}" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        style="cursor:pointer;filter:drop-shadow(0px 0px 10px ${d.color});transition:all 0.3s ease;">
        <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
        <circle cx="12" cy="10" r="3" fill="white"></circle>
      </svg>`;
    el.style.transform = 'translate(-50%, -100%)';
    el.onclick = () => setSelectedRestaurant(d as Restaurant);
    el.onmouseenter = () => setHoveredRestaurant(d as Restaurant);
    el.onmouseleave = () => setHoveredRestaurant(null);
    return el;
  };

  if (!isClient) return null;

  const isIdle = mode === 'idle';

  return (
    <div className={`absolute inset-0 z-0 bg-black transition-transform duration-[1500ms] ease-in-out ${isIdle ? 'translate-x-[20vw] md:translate-x-[25vw]' : 'translate-x-0'}`}>
      <Globe
        ref={globeEl}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        atmosphereColor={isIdle ? '#4488ff' : '#3a228a'}
        atmosphereAltitude={isIdle ? 0.28 : 0.15}
        htmlElementsData={markersData}
        htmlLat="latitude"
        htmlLng="longitude"
        htmlElement={createGlobeMarker}
      />

      {/* ── Sun & Moon — search page only ── */}
      {isIdle && (
        <>
          <style>{`
            @keyframes sunPulse {
              0%,100% { transform:scale(1); filter:blur(0px); }
              50% { transform:scale(1.1); filter:blur(2px); }
            }
            @keyframes sunRays {
              0% { opacity:0.6; transform:scale(1) rotate(0deg); }
              50% { opacity:1; transform:scale(1.15) rotate(20deg); }
              100% { opacity:0.6; transform:scale(1) rotate(0deg); }
            }
            @keyframes moonGlow {
              0%,100% { box-shadow:0 0 28px 8px rgba(180,200,255,0.35); }
              50% { box-shadow:0 0 55px 18px rgba(180,200,255,0.6); }
            }
            @keyframes starsTwinkle {
              0%,100% { opacity:0.5; }
              50% { opacity:1; }
            }
          `}</style>

          {/* Sun corona glow (behind sun) */}
          <div className="absolute pointer-events-none" style={{
            top: '7%', right: '3%',
            width: 160, height: 160,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,220,80,0.4) 0%, rgba(255,120,0,0.15) 50%, transparent 75%)',
            animation: 'sunRays 5s ease-in-out infinite',
          }} />

          {/* Sun body */}
          <div className="absolute pointer-events-none" style={{
            top: '12%', right: '8%',
            width: 72, height: 72,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 38% 38%, #fffbe8 0%, #ffd700 45%, #ff8c00 100%)',
            boxShadow: '0 0 50px 18px rgba(255,210,50,0.65), 0 0 100px 40px rgba(255,140,0,0.3)',
            animation: 'sunPulse 4s ease-in-out infinite',
          }} />

          {/* Moon */}
          <div className="absolute pointer-events-none" style={{
            bottom: '16%', left: '5%',
            width: 52, height: 52,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 32% 32%, #f0f0f0 0%, #c8c8c8 55%, #808080 100%)',
            animation: 'moonGlow 6s ease-in-out infinite',
          }}>
            {/* Craters */}
            <div style={{ position:'absolute', width:11, height:11, borderRadius:'50%', background:'rgba(100,100,100,0.35)', top:'22%', left:'28%' }} />
            <div style={{ position:'absolute', width:7,  height:7,  borderRadius:'50%', background:'rgba(100,100,100,0.25)', top:'55%', left:'58%' }} />
            <div style={{ position:'absolute', width:5,  height:5,  borderRadius:'50%', background:'rgba(100,100,100,0.3)',  top:'30%', left:'62%' }} />
          </div>

          {/* A few decorative stars near moon */}
          {[
            { x:'8%', y:'8%',  s:2, delay:'0s' },
            { x:'14%',y:'22%', s:3, delay:'1s' },
            { x:'4%', y:'35%', s:2, delay:'2s' },
            { x:'18%',y:'14%', s:2, delay:'0.5s' },
          ].map((star, i) => (
            <div key={i} className="absolute rounded-full bg-white pointer-events-none"
              style={{
                left: star.x, top: star.y,
                width: star.s, height: star.s,
                animation: `starsTwinkle 3s ${star.delay} ease-in-out infinite`,
              }}
            />
          ))}
        </>
      )}
    </div>
  );
}
