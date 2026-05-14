/**
 * loading.js — Three.js rotating wireframe orb for the loading state.
 * Renders into #loading-canvas.
 */
(function () {
  'use strict';

  function init() {
    const canvas = document.getElementById('loading-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    const W = canvas.clientWidth  || 220;
    const H = canvas.clientHeight || 220;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(W, H);

    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 100);
    camera.position.z = 4;

    // Outer wireframe icosahedron
    const geo1  = new THREE.IcosahedronGeometry(1.4, 1);
    const wire1 = new THREE.WireframeGeometry(geo1);
    const mat1  = new THREE.LineBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.7 });
    const orb1  = new THREE.LineSegments(wire1, mat1);
    scene.add(orb1);

    // Inner smaller orb (different axis rotation)
    const geo2  = new THREE.IcosahedronGeometry(0.85, 0);
    const wire2 = new THREE.WireframeGeometry(geo2);
    const mat2  = new THREE.LineBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.5 });
    const orb2  = new THREE.LineSegments(wire2, mat2);
    scene.add(orb2);

    // Ambient glow via point light (not directly visible but adds mood)
    const light = new THREE.PointLight(0x7c3aed, 2, 10);
    light.position.set(0, 0, 3);
    scene.add(light);

    let raf;
    function animate(t) {
      raf = requestAnimationFrame(animate);
      orb1.rotation.x = t * 0.0005;
      orb1.rotation.y = t * 0.0008;
      orb2.rotation.x = -t * 0.0007;
      orb2.rotation.z =  t * 0.0004;

      // Pulsing opacity
      mat1.opacity = 0.45 + 0.3 * Math.sin(t * 0.002);
      mat2.opacity = 0.3  + 0.2 * Math.sin(t * 0.003 + 1);

      renderer.render(scene, camera);
    }

    animate(0);

    window._stopLoadingOrb = function () {
      if (raf) cancelAnimationFrame(raf);
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
