"use client";

import dynamic from "next/dynamic";

// R3F touches `window`, so the canvas must never render on the server.
const HeroSceneCanvas = dynamic(() => import("./hero-scene-canvas"), { ssr: false });

/** Three.js hero canvas — client-only, lazy-loaded. */
export function HeroScene() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
      <HeroSceneCanvas />
    </div>
  );
}
