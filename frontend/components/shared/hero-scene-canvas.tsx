"use client";

import { Float } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";

/**
 * Lightweight 3D hero: a floating, slowly-rotating ticket/queue motif.
 * Purely decorative — kept off the functional pages for bundle-size reasons.
 */
function TicketShape() {
  return (
    <Float speed={1.5} rotationIntensity={0.6} floatIntensity={1.2}>
      <mesh>
        <boxGeometry args={[1.4, 2.2, 0.18]} />
        <meshStandardMaterial color="#0ea5e9" />
      </mesh>
      <mesh position={[0, 0, 0.12]}>
        <torusGeometry args={[0.32, 0.06, 12, 32]} />
        <meshStandardMaterial color="#f8fafc" />
      </mesh>
    </Float>
  );
}

export default function HeroSceneCanvas() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 45 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
    >
      <ambientLight intensity={0.7} />
      <directionalLight position={[2, 3, 4]} intensity={1.2} />
      <TicketShape />
    </Canvas>
  );
}
