/**
 * hero.js — Three.js food-emoji particle field
 * Renders floating food particles on a fixed canvas behind the search UI.
 * Uses THREE.Sprite with canvas-generated emoji textures.
 */
(function () {
  'use strict';

  const EMOJIS = ['🍜','🍛','🍕','🌮','🍔','🍣','🍝','🥘','🌯','🥗','🍱','🍲'];
  const COUNT  = 80;

  let scene, camera, renderer, sprites = [], mouse = { x: 0, y: 0 }, raf;

  /* ── texture factory ─────────────────────────────────────── */
  function makeEmojiTexture(emoji) {
    const c = document.createElement('canvas');
    c.width = c.height = 96;
    const ctx = c.getContext('2d');
    ctx.font = '72px serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(emoji, 48, 52);
    const tex = new THREE.CanvasTexture(c);
    tex.needsUpdate = true;
    return tex;
  }

  /* ── random range ────────────────────────────────────────── */
  function rnd(min, max) { return min + Math.random() * (max - min); }

  /* ── init ────────────────────────────────────────────────── */
  function init() {
    const canvas = document.getElementById('hero-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);

    scene  = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
    camera.position.z = 50;

    // Pre-build one texture per emoji
    const textures = EMOJIS.map(makeEmojiTexture);

    for (let i = 0; i < COUNT; i++) {
      const tex = textures[i % textures.length];
      const mat = new THREE.SpriteMaterial({
        map: tex,
        transparent: true,
        opacity: rnd(0.25, 0.65),
        depthWrite: false,
      });
      const sprite = new THREE.Sprite(mat);
      const scale  = rnd(1.8, 4.5);
      sprite.scale.set(scale, scale, 1);
      sprite.position.set(
        rnd(-60, 60),
        rnd(-40, 40),
        rnd(-30, 0)
      );
      sprite.userData = {
        speedY: rnd(0.015, 0.06),
        speedR: rnd(-0.003, 0.003),
        originX: sprite.position.x,
        phase: rnd(0, Math.PI * 2),
      };
      scene.add(sprite);
      sprites.push(sprite);
    }

    window.addEventListener('resize', onResize);
    window.addEventListener('mousemove', onMouse);
    animate(0);
  }

  /* ── animation loop ──────────────────────────────────────── */
  function animate(t) {
    raf = requestAnimationFrame(animate);

    sprites.forEach(s => {
      const d = s.userData;
      // Float upward
      s.position.y += d.speedY;
      // Gentle sine drift on X
      s.position.x = d.originX + Math.sin(t * 0.0005 + d.phase) * 2.5;
      // Fade out near top, teleport to bottom
      const progress = (s.position.y + 40) / 80;
      s.material.opacity = progress < 0.85
        ? rnd(0.25, 0.65) * (1 - Math.max(0, (progress - 0.7) / 0.15))
        : 0;
      if (s.position.y > 42) {
        s.position.y = -42;
        s.position.x = rnd(-60, 60);
        d.originX = s.position.x;
        d.phase   = rnd(0, Math.PI * 2);
      }
    });

    // Subtle camera parallax on mouse
    camera.position.x += (mouse.x * 4 - camera.position.x) * 0.04;
    camera.position.y += (-mouse.y * 3 - camera.position.y) * 0.04;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  function onMouse(e) {
    mouse.x = (e.clientX / window.innerWidth)  * 2 - 1;
    mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
  }

  /* ── public stop ─────────────────────────────────────────── */
  window.stopHero = function () {
    if (raf) cancelAnimationFrame(raf);
    window.removeEventListener('resize', onResize);
    window.removeEventListener('mousemove', onMouse);
  };

  // Start when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
