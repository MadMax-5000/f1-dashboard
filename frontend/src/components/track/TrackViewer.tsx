"use client"

import { useRef, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls, Line, Text } from "@react-three/drei"
import * as THREE from "three"
import { useF1Store } from "@/lib/store"

function TrackPath() {
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = []
    const segments = 80
    for (let i = 0; i <= segments; i++) {
      const t = (i / segments) * Math.PI * 2
      const r = 8 + Math.sin(t * 3) * 2 + Math.cos(t * 5) * 0.8
      pts.push(
        new THREE.Vector3(
          Math.cos(t) * r,
          Math.sin(t * 2) * 0.3,
          Math.sin(t) * r
        )
      )
    }
    return pts
  }, [])

  return (
    <Line
      points={points}
      color="#333344"
      lineWidth={2}
      dashed={false}
    />
  )
}

function Cars() {
  const twinState = useF1Store((s) => s.twinState)
  const focusedDriver = useF1Store((s) => s.focusedDriver)

  return (
    <group>
      {twinState?.order.map((did, idx) => {
        const ds = twinState.drivers[did]
        if (!ds) return null
        const isFocused = focusedDriver === did
        const progress = ((ds.position - 1) / Math.max(twinState.order.length - 1, 1))
        const t = (progress) * Math.PI * 2
        const r = 8 + Math.sin(t * 3) * 2 + Math.cos(t * 5) * 0.8
        const x = Math.cos(t) * r
        const z = Math.sin(t) * r

        return (
          <group key={did}>
            <mesh position={[x, 0.2, z]}>
              <boxGeometry args={[0.4, 0.15, 0.8]} />
              <meshStandardMaterial
                color={isFocused ? "#e10600" : "#ffffff"}
                emissive={isFocused ? "#e10600" : "#333333"}
                emissiveIntensity={isFocused ? 0.5 : 0.1}
              />
            </mesh>
            <Text
              position={[x, 0.6, z]}
              fontSize={0.15}
              color={isFocused ? "#e10600" : "#888888"}
            >
              {ds.position}
            </Text>
          </group>
        )
      })}
    </group>
  )
}

function Scene() {
  return (
    <>
      <color attach="background" args={["#0f0f1a"]} />
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 15, 10]} intensity={0.8} />
      <pointLight position={[-5, 5, -5]} intensity={0.3} color="#e10600" />

      {/* Grid */}
      <gridHelper args={[30, 30, "#1a1a2e", "#1a1a2e"]} />

      <TrackPath />
      <Cars />

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        target={[0, 0, 0]}
        minDistance={5}
        maxDistance={30}
      />
    </>
  )
}

export function TrackViewer() {
  return (
    <div className="w-full h-full bg-f1-darker relative">
      <Canvas camera={{ position: [0, 15, 15], fov: 50 }}>
        <Scene />
      </Canvas>

      {/* Overlay info */}
      <div className="absolute top-3 left-3 bg-black/70 px-3 py-1.5 rounded text-xs text-gray-400">
        <span className="text-f1-red">●</span> Drag to orbit · Scroll to zoom
      </div>

      <div className="absolute bottom-3 right-3 bg-black/70 px-3 py-1.5 rounded text-xs text-gray-400">
        F1 Digital Twin v0.1
      </div>
    </div>
  )
}
