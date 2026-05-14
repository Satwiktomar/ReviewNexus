'use client';

import { useState } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { api } from '@/services/api';
import {
  Search, MapPin, Utensils, X, FlaskConical,
  BarChart3, Star, MessageSquare, Zap, Globe2, Brain
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// ── Shared modal wrapper ────────────────────────────────────────────────────
function Modal({ onClose, children }: { onClose: () => void; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[999] flex items-center justify-center p-4"
      style={{ backdropFilter: 'blur(14px)', background: 'rgba(0,0,0,0.75)' }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.88, opacity: 0, y: 24 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.88, opacity: 0, y: 24 }}
        transition={{ type: 'spring', stiffness: 320, damping: 30 }}
        className="relative w-full max-w-xl max-h-[85vh] overflow-y-auto rounded-2xl border border-white/10"
        style={{ background: 'linear-gradient(135deg, rgba(10,15,30,0.98), rgba(5,10,25,0.98))' }}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}

// ── Rating Formula Modal ────────────────────────────────────────────────────
function FormulaModal({ onClose }: { onClose: () => void }) {
  return (
    <Modal onClose={onClose}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <FlaskConical className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <h2 className="text-white font-bold text-base">Rating Formula</h2>
            <p className="text-gray-500 text-xs">Bayesian composite scoring</p>
          </div>
        </div>
        <button onClick={onClose} className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/15 flex items-center justify-center transition-colors">
          <X className="w-3.5 h-3.5 text-gray-400" />
        </button>
      </div>

      <div className="px-6 py-5 space-y-4">
        {/* Formula */}
        <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-3 text-center">
          <p className="text-gray-500 text-xs mb-1.5 uppercase tracking-widest font-semibold">Final Score (/10)</p>
          <p className="text-white text-lg font-mono font-bold">
            S = 0.45·<span className="text-blue-400">R̂</span> + 0.30·<span className="text-cyan-400">V̂</span> + 0.25·<span className="text-green-400">Ŝ</span>
          </p>
        </div>

        {/* Components grid */}
        <div className="space-y-3">
          {/* Bayesian */}
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-3.5 h-3.5 text-blue-400" />
              <p className="text-blue-400 font-semibold text-sm">R̂ — Bayesian Rating (45%)</p>
            </div>
            <div className="bg-black/30 rounded-lg px-3 py-2 font-mono text-xs text-white mb-2">
              R̂ = (C·m + n·r) / (C + n)
            </div>
            <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
              <span><code className="text-blue-300">r</code> = raw star rating</span>
              <span><code className="text-blue-300">n</code> = review count</span>
              <span><code className="text-blue-300">m</code> = global avg (≈4.3)</span>
              <span><code className="text-blue-300">C</code> = confidence (25)</span>
            </div>
          </div>

          {/* Volume */}
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
              <p className="text-cyan-400 font-semibold text-sm">V̂ — Volume Score (30%)</p>
            </div>
            <div className="bg-black/30 rounded-lg px-3 py-2 font-mono text-xs text-white">
              V̂ = log(1+n) / log(1+n<sub>max</sub>)
            </div>
            <p className="text-gray-500 text-xs mt-2">Log-normalized so viral places don't dominate</p>
          </div>

          {/* Sentiment */}
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-4">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="w-3.5 h-3.5 text-green-400" />
              <p className="text-green-400 font-semibold text-sm">Ŝ — AI Sentiment (25%)</p>
            </div>
            <p className="text-gray-400 text-xs leading-relaxed">
              Review text is analyzed by a <strong className="text-white">DistilBERT</strong> sentiment classifier.
              Each review scores –1 to +1. The mean is normalized to [0, 1].
            </p>
          </div>
        </div>

        <p className="text-gray-600 text-xs text-center">
          High ratings + many reviews + positive language = top score. Pure star count alone won't do it.
        </p>
      </div>
    </Modal>
  );
}

// ── How It Works Modal ──────────────────────────────────────────────────────
function HowItWorksModal({ onClose }: { onClose: () => void }) {
  const steps = [
    {
      icon: <Search className="w-4 h-4 text-blue-400" />,
      color: 'bg-blue-500/20',
      title: '1. You search',
      desc: 'Enter a dish and a city. Our system builds optimized Google Maps search queries to maximize coverage.'
    },
    {
      icon: <Globe2 className="w-4 h-4 text-cyan-400" />,
      color: 'bg-cyan-500/20',
      title: '2. We scrape',
      desc: 'A headless Playwright browser silently browses Google Maps, scrolls results, and extracts names, ratings, review counts, addresses, and exact GPS coordinates.'
    },
    {
      icon: <Brain className="w-4 h-4 text-purple-400" />,
      color: 'bg-purple-500/20',
      title: '3. AI reads every review',
      desc: 'A DistilBERT transformer model reads the text of each scraped review and assigns a sentiment score. No stars needed — it understands language.'
    },
    {
      icon: <BarChart3 className="w-4 h-4 text-green-400" />,
      color: 'bg-green-500/20',
      title: '4. We rank',
      desc: 'A Bayesian composite score is calculated: star quality + popularity + AI sentiment. The best restaurant rises to the top on merit, not marketing.'
    },
    {
      icon: <MapPin className="w-4 h-4 text-red-400" />,
      color: 'bg-red-500/20',
      title: '5. You explore',
      desc: 'Results appear on an interactive 2D city map with exact pins, or browse the ranked list. Click any pin to open Google Maps navigation directly.'
    },
  ];

  return (
    <Modal onClose={onClose}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-white font-bold text-base">How It Works</h2>
            <p className="text-gray-500 text-xs">From search to ranked map in seconds</p>
          </div>
        </div>
        <button onClick={onClose} className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/15 flex items-center justify-center transition-colors">
          <X className="w-3.5 h-3.5 text-gray-400" />
        </button>
      </div>

      <div className="px-6 py-5 space-y-3">
        {steps.map((step, i) => (
          <div key={i} className="flex gap-4 rounded-xl bg-white/[0.03] border border-white/5 p-4">
            <div className={`w-8 h-8 rounded-lg ${step.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
              {step.icon}
            </div>
            <div>
              <p className="text-white font-semibold text-sm mb-1">{step.title}</p>
              <p className="text-gray-400 text-xs leading-relaxed">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </Modal>
  );
}

// ── About Modal ─────────────────────────────────────────────────────────────
function AboutModal({ onClose }: { onClose: () => void }) {
  return (
    <Modal onClose={onClose}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-orange-500/20 flex items-center justify-center">
            <Globe2 className="w-4 h-4 text-orange-400" />
          </div>
          <div>
            <h2 className="text-white font-bold text-base">About ReviewNexus</h2>
            <p className="text-gray-500 text-xs">The story behind it</p>
          </div>
        </div>
        <button onClick={onClose} className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/15 flex items-center justify-center transition-colors">
          <X className="w-3.5 h-3.5 text-gray-400" />
        </button>
      </div>

      <div className="px-6 py-5 space-y-4">
        <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 px-4 py-4">
          <p className="text-orange-300 text-sm font-medium italic leading-relaxed">
            "You land in a new city — maybe for work, travel, or just a weekend trip. You're hungry. You don't know anyone. You open maps, search for food, and get hit with a hundred generic results, all claiming to be the best. Which one do you actually trust?"
          </p>
        </div>

        <p className="text-gray-300 text-sm leading-relaxed">
          That feeling of being completely clueless about where to eat in an unfamiliar city is something most of us have felt. Too many options, too little signal. Star ratings are gamed. "Top 10" lists are months old. Friends' recommendations don't always match your taste.
        </p>

        <p className="text-gray-400 text-sm leading-relaxed">
          <strong className="text-white">ReviewNexus</strong> was built to solve exactly that. We scrape live data directly from Google Maps, read what real people are actually saying in reviews using AI, and compute a fair, transparent score — so you get a reliable answer fast, no matter where in the world you are.
        </p>

        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Live Data', desc: 'Scraped fresh on every search' },
            { label: 'AI Reviewed', desc: 'Not just star counts' },
            { label: 'Global', desc: 'Works in any city, worldwide' },
          ].map((item, i) => (
            <div key={i} className="rounded-xl bg-white/[0.03] border border-white/5 p-3 text-center">
              <p className="text-white font-semibold text-sm">{item.label}</p>
              <p className="text-gray-500 text-xs mt-1">{item.desc}</p>
            </div>
          ))}
        </div>

        <p className="text-gray-600 text-xs text-center">
          Built with Playwright · DistilBERT · Nominatim · Three.js · Leaflet · Next.js
        </p>
      </div>
    </Modal>
  );
}

// ── Header ──────────────────────────────────────────────────────────────────
function Header({ onFormula, onHowItWorks, onAbout }: {
  onFormula: () => void;
  onHowItWorks: () => void;
  onAbout: () => void;
}) {
  return (
    <div className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-8 py-5 pointer-events-auto">
      <div className="flex items-center gap-2">
        <span className="text-white font-extrabold text-xl tracking-tight">
          Review<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Nexus</span>
        </span>
      </div>
      <nav className="flex items-center gap-6">
        <button onClick={onFormula} className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm font-medium transition-colors group">
          <FlaskConical className="w-3.5 h-3.5 group-hover:text-blue-400 transition-colors" />
          Rating Formula
        </button>
        <button onClick={onHowItWorks} className="text-gray-400 hover:text-white text-sm font-medium transition-colors">How it works</button>
        <button onClick={onAbout} className="text-gray-400 hover:text-white text-sm font-medium transition-colors">About</button>
      </nav>
    </div>
  );
}

// ── Main Component ──────────────────────────────────────────────────────────
export default function SearchPanel() {
  const { mode, setMode, setSearch, setProgress, setResults } = useAppStore();
  const [localDish, setLocalDish] = useState('');
  const [localCity, setLocalCity] = useState('');
  const [error, setError] = useState('');
  const [localMaxPlaces, setLocalMaxPlaces] = useState(10);
  const [modal, setModal] = useState<'formula' | 'how' | 'about' | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!localDish.trim() || !localCity.trim()) {
      setError('Please enter both a dish and a city.');
      return;
    }
    setError('');
    setSearch(localDish, localCity);
    setMode('searching');
    setProgress(10, 'Initializing search pipeline...');

    try {
      await api.search(localDish, localCity, localMaxPlaces);

      const pollInterval = setInterval(async () => {
        try {
          const status = await api.getStatus(localDish, localCity);
          setProgress(status.progress, status.status);

          if (status.status === 'completed' || status.status.startsWith('Error') || status.status === 'error') {
            clearInterval(pollInterval);
            if (status.status === 'completed') {
              const results = await api.getResults(localDish, localCity);
              setResults(results.restaurants, results.city_lat, results.city_lng);
              setMode('results');
              setTimeout(() => {
                if (useAppStore.getState().mode === 'results') {
                  useAppStore.getState().setViewMode('map');
                }
              }, 3000);
            } else {
              setError(status.status);
              setMode('idle');
            }
          }
        } catch (err) {
          console.error('Polling error', err);
        }
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'An error occurred during search.');
      setMode('idle');
    }
  };

  return (
    <>
      {/* Header */}
      <AnimatePresence>
        {mode === 'idle' && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <Header
              onFormula={() => setModal('formula')}
              onHowItWorks={() => setModal('how')}
              onAbout={() => setModal('about')}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modals */}
      <AnimatePresence>
        {modal === 'formula' && <FormulaModal onClose={() => setModal(null)} />}
        {modal === 'how' && <HowItWorksModal onClose={() => setModal(null)} />}
        {modal === 'about' && <AboutModal onClose={() => setModal(null)} />}
      </AnimatePresence>

      {/* Search panel */}
      <AnimatePresence>
        {mode === 'idle' && (
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50, filter: 'blur(10px)' }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="absolute inset-y-0 left-0 flex flex-col justify-center px-8 md:px-[10vw] z-10 pointer-events-none w-full lg:w-[60vw]"
          >
            <div className="mb-8 max-w-xl mt-20">
              <h4 className="text-blue-400 font-bold tracking-widest text-xs uppercase mb-4">AI-Powered Restaurant Discovery</h4>
              <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white mb-5 leading-tight">
                Discover the best restaurants in any city,{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">ranked by AI.</span>
              </h1>
              <p className="text-gray-400 text-lg leading-relaxed">
                We scrape real data, analyze reviews with AI, and rank the top places so you can eat the best, every time.
              </p>
            </div>

            <div className="w-full max-w-md p-6 rounded-3xl bg-black/40 backdrop-blur-2xl border border-white/10 shadow-[0_0_50px_rgba(59,130,246,0.15)] pointer-events-auto relative">
              <h2 className="text-white font-semibold mb-5 flex items-center gap-2">
                Find the best restaurants <span className="text-blue-400">✧</span>
              </h2>

              <form onSubmit={handleSearch} className="space-y-4 relative z-10">
                <div className="space-y-3">
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Utensils className="h-5 w-5 text-gray-500 group-focus-within:text-blue-400 transition-colors" />
                    </div>
                    <input
                      type="text"
                      value={localDish}
                      onChange={(e) => setLocalDish(e.target.value)}
                      placeholder="What are you craving? (e.g. cheesecake)"
                      className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all hover:bg-white/10"
                      required
                    />
                  </div>

                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <MapPin className="h-5 w-5 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                    </div>
                    <input
                      type="text"
                      value={localCity}
                      onChange={(e) => setLocalCity(e.target.value)}
                      placeholder="Enter city (e.g. Tokyo, London, New York)"
                      className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all hover:bg-white/10"
                      required
                    />
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-gray-400 text-sm font-medium w-32">Number of results</div>
                    <select
                      value={localMaxPlaces}
                      onChange={(e) => setLocalMaxPlaces(parseInt(e.target.value))}
                      className="block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all hover:bg-white/10 appearance-none cursor-pointer"
                    >
                      <option value={5} className="bg-gray-900">5 Places</option>
                      <option value={10} className="bg-gray-900">10 Places</option>
                      <option value={15} className="bg-gray-900">15 Places</option>
                      <option value={20} className="bg-gray-900">20 Places</option>
                    </select>
                  </div>
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="text-red-400 text-sm text-center bg-red-400/10 py-2 rounded-lg border border-red-400/20"
                  >
                    {error}
                  </motion.div>
                )}

                <button
                  type="submit"
                  className="w-full relative group overflow-hidden rounded-xl p-[1px] mt-2"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-xl opacity-80 group-hover:opacity-100 transition-opacity" />
                  <div className="relative flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-500 px-4 py-3 rounded-xl transition-all group-hover:brightness-110">
                    <Search className="h-5 w-5 text-white" />
                    <span className="text-white font-semibold tracking-wide">Explore Global Cuisine</span>
                  </div>
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
