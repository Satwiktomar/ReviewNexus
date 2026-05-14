'use client';

import { useAppStore } from '@/store/useAppStore';
import { motion } from 'framer-motion';
import { Star, MapPin, Navigation } from 'lucide-react';

export default function RestaurantCard() {
  const { mode, restaurants, selectedRestaurant, setHoveredRestaurant, setSelectedRestaurant, setMode, dish, city } = useAppStore();

  if (mode !== 'results') return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="absolute top-0 left-0 bottom-0 w-full md:w-[450px] bg-black/60 backdrop-blur-xl border-r border-white/10 z-10 flex flex-col pointer-events-auto"
    >
      <div className="p-6 border-b border-white/10 flex-shrink-0 bg-gradient-to-b from-black/80 to-transparent">
        <button 
          onClick={() => {
            setMode('idle');
            useAppStore.getState().setViewMode('globe');
          }}
          className="text-gray-400 hover:text-white text-sm font-medium mb-4 flex items-center gap-2 transition-colors"
        >
          ← New Search
        </button>
        <h2 className="text-2xl font-bold text-white mb-1">
          {dish}
        </h2>
        <p className="text-gray-400 flex items-center gap-1 text-sm">
          <MapPin className="w-3 h-3" /> {city} • {restaurants.length} Results
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {restaurants.map((restaurant, idx) => (
          <motion.div
            key={restaurant.name + idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            onMouseEnter={() => setHoveredRestaurant(restaurant)}
            onMouseLeave={() => setHoveredRestaurant(null)}
            onClick={() => setSelectedRestaurant(restaurant)}
            className={`
              relative p-5 rounded-2xl cursor-pointer transition-all duration-300 border
              ${selectedRestaurant?.name === restaurant.name 
                ? 'bg-blue-500/10 border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.15)]' 
                : 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/20'
              }
            `}
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-bold text-white leading-tight pr-4">{restaurant.name}</h3>
              <div className="flex flex-col items-end">
                <div className="bg-gradient-to-br from-blue-500 to-cyan-400 text-white text-xs font-bold px-2 py-1 rounded-md shadow-lg">
                  {restaurant.score.toFixed(1)}
                </div>
                <span className="text-[10px] text-gray-500 mt-1 uppercase tracking-wider">Score</span>
              </div>
            </div>
            
            <p className="text-sm text-gray-400 mb-4 line-clamp-2">{restaurant.address}</p>
            
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <span className="text-white font-medium">{restaurant.avg_rating}</span>
                <span className="text-gray-500">({restaurant.reviews})</span>
              </div>
              <div className="h-4 w-px bg-white/10"></div>
              <a 
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(restaurant.name + ' ' + restaurant.address)}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <Navigation className="w-3 h-3" />
                Directions
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
