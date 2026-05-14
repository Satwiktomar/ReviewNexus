'use client';

import { useAppStore } from '@/store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';

export default function LoadingScreen() {
  const { mode, progress, statusText } = useAppStore();

  return (
    <AnimatePresence>
      {mode === 'searching' && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { duration: 0.5 } }}
          className="absolute inset-0 z-20 flex flex-col items-center justify-end pb-32 pointer-events-none"
        >
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-full max-w-md px-6 pointer-events-auto"
          >
            <div className="bg-black/50 backdrop-blur-md rounded-2xl p-6 border border-white/10 shadow-2xl relative overflow-hidden">
              
              {/* Progress bar background glow */}
              <div 
                className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-500 ease-out shadow-[0_0_10px_#3b82f6]"
                style={{ width: `${progress}%` }}
              />

              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-medium tracking-wide">Processing Coordinates</h3>
                <span className="text-cyan-400 font-mono text-sm">{progress}%</span>
              </div>

              <div className="flex items-center gap-4">
                <div className="relative flex items-center justify-center h-8 w-8">
                  <div className="absolute inset-0 border-2 border-white/20 rounded-full"></div>
                  <div className="absolute inset-0 border-2 border-cyan-400 rounded-full border-t-transparent animate-spin"></div>
                </div>
                <p className="text-gray-300 text-sm animate-pulse">{statusText}</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
