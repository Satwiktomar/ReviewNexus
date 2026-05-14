/**
 * results.js — Leaflet map initialisation + card stagger animations.
 * Expects window.PLACES_DATA to be set by the template.
 */
(function () {
  'use strict';

  /* ── Map ──────────────────────────────────────────────────── */
  let map, markers = [];

  function initMap() {
    if (typeof L === 'undefined') return;

    const places = window.PLACES_DATA || [];
    const mapEl  = document.getElementById('map');
    if (!mapEl) return;

    // Filter valid coordinates (non-zero)
    const valid = places.filter(p =>
      p.latitude  && p.longitude &&
      Math.abs(p.latitude)  > 0.001 &&
      Math.abs(p.longitude) > 0.001
    );

    if (valid.length === 0) {
      document.getElementById('map-wrapper').style.display = 'none';
      return;
    }

    // Centre on mean of valid points
    const avgLat = valid.reduce((s, p) => s + p.latitude,  0) / valid.length;
    const avgLng = valid.reduce((s, p) => s + p.longitude, 0) / valid.length;

    map = L.map('map', { zoomControl: true, attributionControl: true })
           .setView([avgLat, avgLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© <a href="https://www.openstreetmap.org/copyright" style="color:#a78bfa">OpenStreetMap</a>',
    }).addTo(map);

    // Build a global index: placeIndex → marker index (only valid places)
    window._markerForPlace = {};
    let mi = 0;

    places.forEach((place, idx) => {
      const lat = place.latitude;
      const lng = place.longitude;
      if (!lat || !lng || Math.abs(lat) < 0.001 || Math.abs(lng) < 0.001) return;

      const rank    = idx + 1;
      const isTop3  = rank <= 3;
      const colors  = ['#f59e0b','#94a3b8','#b45309'];
      const bgColor = isTop3 ? colors[rank - 1] : '#7c3aed';

      const icon = L.divIcon({
        className: '',
        html: `<div style="
          background:${bgColor};
          color:white;border-radius:50%;
          width:34px;height:34px;
          display:flex;align-items:center;justify-content:center;
          font-weight:800;font-size:14px;
          border:3px solid rgba(255,255,255,0.9);
          box-shadow:0 2px 12px rgba(0,0,0,0.4);
          font-family:'Space Grotesk',sans-serif;
        ">${rank}</div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -20],
      });

      const sentNum = parseFloat(place.sentiment) || 0;
      const sentEmoji = sentNum >= 0.3 ? '😍' : sentNum >= 0 ? '😊' : sentNum >= -0.2 ? '😐' : '😟';

      const popup = L.popup({ maxWidth: 260 }).setContent(`
        <div style="font-family:'Inter',sans-serif;padding:4px;">
          <div style="font-weight:800;font-size:14px;margin-bottom:6px;color:#f1f5f9;">${place.name}</div>
          <div style="color:#94a3b8;font-size:11px;margin-bottom:10px;line-height:1.4;">${place.address || ''}</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">
            <span style="background:rgba(245,158,11,.15);color:#fcd34d;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">⭐ ${place.avg_rating}</span>
            <span style="background:rgba(124,58,237,.15);color:#a78bfa;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">🏆 ${place.score}</span>
            <span style="background:rgba(255,255,255,.07);color:#94a3b8;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">${sentEmoji} ${place.sentiment}</span>
          </div>
          <a href="${place.url}" target="_blank" rel="noopener noreferrer"
            style="color:#a78bfa;font-weight:600;font-size:11px;text-decoration:none;">
            View on Google Maps →
          </a>
        </div>
      `);

      const marker = L.marker([lat, lng], { icon }).addTo(map).bindPopup(popup);
      markers.push(marker);
      window._markerForPlace[idx] = mi;
      mi++;
    });

    if (markers.length) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.15));
    }
  }

  /* ── Public: highlight marker from card click ─────────────── */
  window.highlightMarker = function (placeIdx) {
    const mi = window._markerForPlace ? window._markerForPlace[placeIdx] : null;
    if (mi === undefined || mi === null || !markers[mi]) return;

    map.setView(markers[mi].getLatLng(), 15, { animate: true });
    markers.forEach(m => m.closePopup());
    markers[mi].openPopup();

    // Highlight card
    document.querySelectorAll('.restaurant-card').forEach(c => c.classList.remove('map-active'));
    const card = document.getElementById('card-' + placeIdx);
    if (card) {
      card.classList.add('map-active');
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  /* ── Stagger card entrance via IntersectionObserver ───────── */
  function initCardAnimations() {
    const cards = document.querySelectorAll('.restaurant-card');
    if (!cards.length) return;

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const card = entry.target;
          const delay = parseInt(card.dataset.delay || '0', 10);
          setTimeout(() => card.classList.add('visible'), delay);
          obs.unobserve(card);
        }
      });
    }, { threshold: 0.1 });

    cards.forEach((card, i) => {
      card.dataset.delay = i * 70;
      obs.observe(card);
    });
  }

  /* ── Boot ─────────────────────────────────────────────────── */
  function boot() {
    initMap();
    initCardAnimations();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
