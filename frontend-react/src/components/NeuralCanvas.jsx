/**
 * Canvas animé de réseau neuronal décoratif.
 * Dessine des nœuds flottants reliés par des lignes, avec interaction souris.
 * Props configurables : nodeCount, connectionDist, mouseRadius, opacity.
 * Utilise IntersectionObserver pour ne s'animer que quand visible (performance).
 */
import { useEffect, useRef } from "react";

export default function NeuralCanvas({
  nodeCount = 160,
  connectionDist = 120,
  mouseRadius = 200,
  opacity = 1,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;
    let running = false;
    let mouse = { x: -9999, y: -9999 };

    // Couleurs du thème BetaLab (bleu marine + or)
    const COLORS = {
      nodeCore: "rgba(20, 33, 61, 0.9)",
      line: "rgba(20, 33, 61, ",
      glow: "rgba(233, 176, 0, ",
      accent: "rgba(233, 176, 0, 0.6)",
    };

    const NODE_COUNT = nodeCount;
    const CONNECTION_DIST = connectionDist;
    const MOUSE_RADIUS = mouseRadius;
    let nodes = [];

    // Redimensionne le canvas selon le conteneur parent (gestion HiDPI)
    function resize() {
      const parent = canvas.parentElement;
      if (!parent) return;
      const rect = parent.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvas.style.width = rect.width + "px";
      canvas.style.height = rect.height + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    // Génère les nœuds aléatoires avec position, vitesse et taille
    function createNodes() {
      const parent = canvas.parentElement;
      if (!parent) return;
      const w = parent.clientWidth;
      const h = parent.clientHeight;
      if (w === 0 || h === 0) return;
      nodes = [];
      for (let i = 0; i < NODE_COUNT; i++) {
        nodes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 1.2 + (Math.random() > 0.5 ? 0.3 : -0.3),
          vy: (Math.random() - 0.5) * 1.2 + (Math.random() > 0.5 ? 0.3 : -0.3),
          r: Math.random() * 2.5 + 1.5,
          pulse: Math.random() * Math.PI * 2,
          isAccent: Math.random() < 0.12,
        });
      }
    }

    const MIN_SPEED = 0.3;

    // Boucle d'animation principale : déplacement des nœuds, connexions, interaction souris
    function animate() {
      if (!running) return;
      const parent = canvas.parentElement;
      if (!parent) return;
      const w = parent.clientWidth;
      const h = parent.clientHeight;
      if (w === 0 || h === 0) {
        animId = requestAnimationFrame(animate);
        return;
      }
      ctx.clearRect(0, 0, w, h);

      for (const n of nodes) {
        n.pulse += 0.02;
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
        n.x = Math.max(0, Math.min(w, n.x));
        n.y = Math.max(0, Math.min(h, n.y));

        const dx = n.x - mouse.x;
        const dy = n.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < MOUSE_RADIUS && dist > 0) {
          const force = (1 - dist / MOUSE_RADIUS) * 0.8;
          n.vx += (dx / dist) * force;
          n.vy += (dy / dist) * force;
        }

        // Dampen mouse impulse but enforce minimum speed so nodes never stop
        n.vx *= 0.998;
        n.vy *= 0.998;
        const speed = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
        if (speed < MIN_SPEED) {
          const scale = MIN_SPEED / (speed || 0.001);
          n.vx *= scale;
          n.vy *= scale;
        }
      }

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECTION_DIST) {
            const alpha = (1 - dist / CONNECTION_DIST) * 0.35;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = COLORS.line + alpha + ")";
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      for (const n of nodes) {
        const dx = n.x - mouse.x;
        const dy = n.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < MOUSE_RADIUS) {
          const alpha = (1 - dist / MOUSE_RADIUS) * 0.4;
          ctx.beginPath();
          ctx.moveTo(mouse.x, mouse.y);
          ctx.lineTo(n.x, n.y);
          ctx.strokeStyle = COLORS.glow + alpha + ")";
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      for (const n of nodes) {
        const pulseR = n.r + Math.sin(n.pulse) * 0.8;
        ctx.beginPath();
        ctx.arc(n.x, n.y, pulseR * 3, 0, Math.PI * 2);
        ctx.fillStyle = n.isAccent
          ? "rgba(233, 176, 0, 0.06)"
          : "rgba(255, 215, 94, 0.08)";
        ctx.fill();
        ctx.beginPath();
        ctx.arc(n.x, n.y, pulseR, 0, Math.PI * 2);
        ctx.fillStyle = n.isAccent ? COLORS.accent : COLORS.nodeCore;
        ctx.fill();
        ctx.beginPath();
        ctx.arc(n.x, n.y, pulseR * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = n.isAccent
          ? "rgba(255, 215, 94, 0.8)"
          : "rgba(255, 248, 225, 0.8)";
        ctx.fill();
      }

      animId = requestAnimationFrame(animate);
    }

    function start() {
      if (running) return;
      running = true;
      resize();
      if (nodes.length === 0) createNodes();
      animate();
    }

    function stop() {
      running = false;
      cancelAnimationFrame(animId);
    }

    function onMouseMove(e) {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    }

    function onMouseLeave() {
      mouse.x = -9999;
      mouse.y = -9999;
    }

    // Use IntersectionObserver so canvas initializes correctly
    // when it scrolls into view (off-screen elements have 0 dimensions)
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            start();
          } else {
            stop();
          }
        }
      },
      { threshold: 0 },
    );
    observer.observe(canvas);

    const onResize = () => {
      resize();
      createNodes();
    };
    window.addEventListener("resize", onResize);
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mouseleave", onMouseLeave);

    return () => {
      stop();
      observer.disconnect();
      window.removeEventListener("resize", onResize);
      canvas.removeEventListener("mousemove", onMouseMove);
      canvas.removeEventListener("mouseleave", onMouseLeave);
    };
  }, [nodeCount, connectionDist, mouseRadius]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "auto",
        zIndex: 0,
        opacity,
      }}
    />
  );
}
