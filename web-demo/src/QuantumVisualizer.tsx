import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

interface Props {
  phase: number;
}

export function QuantumVisualizer({ phase }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let animationFrameId: number;
    let renderer: THREE.WebGLRenderer;
    let composer: EffectComposer;

    const setupScene = () => {
      if (!containerRef.current) return;

      const scene = new THREE.Scene();
      
      const camera = new THREE.PerspectiveCamera(50, containerRef.current.clientWidth / containerRef.current.clientHeight, 0.1, 100);
      camera.position.set(0, 4, 10);
      camera.lookAt(0, 0, 0);

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      containerRef.current.appendChild(renderer.domElement);

      // --- Post Processing (Bloom) ---
      const renderScene = new RenderPass(scene, camera);
      const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
      bloomPass.threshold = 0;
      bloomPass.strength = 1.2;
      bloomPass.radius = 0.5;

      composer = new EffectComposer(renderer);
      composer.addPass(renderScene);
      composer.addPass(bloomPass);

      const droneGroup = new THREE.Group();
      scene.add(droneGroup);

      // --- Grid Floor (Hangar Grid) ---
      const gridHelper = new THREE.GridHelper(20, 20, 0x004040, 0x001010);
      gridHelper.position.y = -1.5;
      gridHelper.material.transparent = true;
      gridHelper.material.opacity = 0.3;
      scene.add(gridHelper);

      // --- Procedural Drone Model ---
      const wireframeMaterial = new THREE.LineBasicMaterial({
        color: 0x00F0FF,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
      });

      // Central Body
      const bodyGeo = new THREE.BoxGeometry(1, 0.2, 1);
      const edgesGeo = new THREE.EdgesGeometry(bodyGeo);
      const bodyMesh = new THREE.LineSegments(edgesGeo, wireframeMaterial);
      droneGroup.add(bodyMesh);

      // Arms
      const armLength = 2;
      const armGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-armLength, 0, -armLength),
        new THREE.Vector3(armLength, 0, armLength),
        new THREE.Vector3(-armLength, 0, armLength),
        new THREE.Vector3(armLength, 0, -armLength),
      ]);
      const armsMesh = new THREE.LineSegments(armGeo, wireframeMaterial);
      droneGroup.add(armsMesh);

      // Props / Motors
      const propPositions = [
        new THREE.Vector3(-armLength, 0.1, -armLength),
        new THREE.Vector3(armLength, 0.1, armLength),
        new THREE.Vector3(-armLength, 0.1, armLength),
        new THREE.Vector3(armLength, 0.1, -armLength),
      ];

      const props: THREE.LineSegments[] = [];
      const propGeo = new THREE.EdgesGeometry(new THREE.CylinderGeometry(0.5, 0.5, 0.05, 12));
      
      const arrowHelpers: THREE.ArrowHelper[] = [];

      propPositions.forEach(pos => {
        const propMaterial = new THREE.LineBasicMaterial({ 
          color: 0x00F0FF, 
          transparent: true, 
          opacity: 0.5,
          blending: THREE.AdditiveBlending
        });
        const propMesh = new THREE.LineSegments(propGeo, propMaterial);
        propMesh.position.copy(pos);
        droneGroup.add(propMesh);
        props.push(propMesh);

        // Arrows representing gyro/accel clean vectors
        const dir = new THREE.Vector3(0, 1, 0);
        // Smaller arrow heads (length 1.5, headLength 0.2, headWidth 0.1), cyan color to reduce bloom blowout
        const arrow = new THREE.ArrowHelper(dir, pos, 1.5, 0x00F0FF, 0.2, 0.1);
        droneGroup.add(arrow);
        arrowHelpers.push(arrow);
      });

      // Dust / Noise Particles
      const dustGeo = new THREE.BufferGeometry();
      const dustCount = 1000;
      const dustPos = new Float32Array(dustCount * 3);
      for(let i=0; i<dustCount * 3; i++) dustPos[i] = (Math.random() - 0.5) * 5;
      dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
      const dustMat = new THREE.PointsMaterial({ 
        color: 0xFF2E63, 
        size: 0.05, 
        transparent: true, 
        opacity: 0,
        blending: THREE.AdditiveBlending
      });
      const dustSystem = new THREE.Points(dustGeo, dustMat);
      scene.add(dustSystem);

      // Resize handling
      const handleResize = () => {
        if (!containerRef.current) return;
        const w = containerRef.current.clientWidth;
        const h = containerRef.current.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
        composer.setSize(w, h);
      };
      window.addEventListener('resize', handleResize);

      // Animation Loop
      let time = 0;
      let phase3Time = 0;

      const animate = () => {
        time += 0.016;
        
        // Base Hover Animation
        droneGroup.position.y = Math.sin(time * 2) * 0.1;
        droneGroup.rotation.y = Math.sin(time * 0.5) * 0.2;

        // Prop rotation
        props.forEach(p => p.rotation.y += 0.5);

        // Flickering logic (Opacidad variable simulando inestabilidad energética)
        const flicker = 0.7 + (Math.sin(time * 50) * 0.1);
        wireframeMaterial.opacity = flicker;

        // State Machine logic
        if (phase === 1) {
          wireframeMaterial.color.setHex(0x00F0FF);
          props.forEach(p => (p.material as THREE.LineBasicMaterial).color.setHex(0x00F0FF));
          arrowHelpers.forEach(a => a.setDirection(new THREE.Vector3(0, 1, 0)));
          dustMat.opacity = 0;
          bloomPass.strength = 1.0;
          phase3Time = 0;
        } 
        else if (phase === 2) {
          wireframeMaterial.color.setHex(0xFF2E63);
          props.forEach(p => (p.material as THREE.LineBasicMaterial).color.setHex(0xFF2E63));
          
          droneGroup.position.x += (Math.random() - 0.5) * 0.4;
          droneGroup.position.y += (Math.random() - 0.5) * 0.4;
          droneGroup.position.z += (Math.random() - 0.5) * 0.4;
          
          arrowHelpers.forEach(a => {
            const randomDir = new THREE.Vector3(Math.random()-0.5, Math.random()-0.5, Math.random()-0.5).normalize();
            a.setDirection(randomDir);
          });
          
          dustMat.opacity = 0;
          bloomPass.strength = 2.0; // Intensificar brillo en caos
          phase3Time = 0;
        } 
        else if (phase === 3) {
          phase3Time += 0.016;
          
          wireframeMaterial.color.setHex(0x00F0FF);
          props.forEach(p => (p.material as THREE.LineBasicMaterial).color.setHex(0x00F0FF));
          arrowHelpers.forEach(a => a.setDirection(new THREE.Vector3(0, 1, 0)));
          
          dustMat.opacity = Math.max(0, 0.8 - phase3Time * 0.5); 
          const positions = dustGeo.attributes.position.array as Float32Array;
          for(let i=0; i<dustCount; i++) {
            positions[i*3] *= 1.05;
            positions[i*3+1] *= 1.05;
            positions[i*3+2] *= 1.05;
          }
          dustGeo.attributes.position.needsUpdate = true;
          
          if (phase3Time < 0.05) {
             for(let i=0; i<dustCount * 3; i++) positions[i] = (Math.random() - 0.5) * 2;
          }
          bloomPass.strength = 1.5;
        }

        // IMPORTANT: render via Composer, not renderer
        composer.render();
        animationFrameId = requestAnimationFrame(animate);
      };
      
      animate();

      return () => {
        window.removeEventListener('resize', handleResize);
      };
    };

    const cleanupResize = setupScene();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (cleanupResize) cleanupResize();
      if (renderer && containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
        renderer.dispose();
      }
    };
  }, [phase]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: '300px' }} />;
}
