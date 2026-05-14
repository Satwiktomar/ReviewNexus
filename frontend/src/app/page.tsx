'use client';

import dynamic from 'next/dynamic';
import GlobeView from '@/components/Globe/GlobeView';
import SearchPanel from '@/components/SearchPanel/SearchPanel';
import LoadingScreen from '@/components/LoadingScreen/LoadingScreen';
import RestaurantCard from '@/components/RestaurantCard/RestaurantCard';
import { useAppStore } from '@/store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';

// Dynamically import MapView to avoid SSR issues with Leaflet
const MapView = dynamic(() => import('@/components/Map/MapView'), { 
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black z-0"></div>
});

export default function Home() {
  const { viewMode } = useAppStore();

  return (
    <main className="relative w-full h-screen overflow-hidden bg-black font-sans selection:bg-blue-500/30">
      
      {/* Render Globe (always mounted to preserve camera state) */}
      <div 
        className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${viewMode === 'globe' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}
      >
        <GlobeView />
      </div>

      {/* Render 2D Map (always mounted to preserve camera state) */}
      <div
        className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${viewMode === 'map' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}
      >
        <MapView />
      </div>

      {/* UI Overlays */}
      <SearchPanel />
      <LoadingScreen />
      <RestaurantCard />
    </main>
  );
}
