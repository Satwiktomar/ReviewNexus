import { create } from 'zustand';
import { Restaurant } from '../services/api';

interface AppState {
  // Search state
  dish: string;
  city: string;
  setSearch: (dish: string, city: string) => void;
  
  // App Modes
  mode: 'idle' | 'searching' | 'results';
  setMode: (mode: 'idle' | 'searching' | 'results') => void;
  viewMode: 'globe' | 'map';
  setViewMode: (mode: 'globe' | 'map') => void;

  // Globe camera restore altitude (set when transitioning back from Map to Globe)
  globeRestoreAltitude: number | null;
  setGlobeRestoreAltitude: (alt: number | null) => void;

  // Search Progress
  progress: number;
  statusText: string;
  setProgress: (progress: number, text: string) => void;

  // Data
  restaurants: Restaurant[];
  cityCoords: { lat: number, lng: number } | null;
  setResults: (restaurants: Restaurant[], lat: number, lng: number) => void;

  // Interactions
  selectedRestaurant: Restaurant | null;
  setSelectedRestaurant: (restaurant: Restaurant | null) => void;
  hoveredRestaurant: Restaurant | null;
  setHoveredRestaurant: (restaurant: Restaurant | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  dish: '',
  city: '',
  setSearch: (dish, city) => set({ dish, city }),

  mode: 'idle',
  setMode: (mode) => set({ mode }),

  viewMode: 'globe',
  setViewMode: (viewMode) => set({ viewMode }),

  globeRestoreAltitude: null,
  setGlobeRestoreAltitude: (globeRestoreAltitude) => set({ globeRestoreAltitude }),

  progress: 0,
  statusText: 'Initializing...',
  setProgress: (progress, statusText) => set({ progress, statusText }),

  restaurants: [],
  cityCoords: null,
  setResults: (restaurants, lat, lng) => set({ restaurants, cityCoords: { lat, lng } }),

  selectedRestaurant: null,
  setSelectedRestaurant: (selectedRestaurant) => set({ selectedRestaurant }),
  
  hoveredRestaurant: null,
  setHoveredRestaurant: (hoveredRestaurant) => set({ hoveredRestaurant }),
}));
