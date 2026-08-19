import { useEffect, useRef } from 'react';

const SingularityHologram = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    let animationFrameId: number;
    let time = 0;

    const resize = () => {
      if (canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
      }
    };

    window.addEventListener('resize', resize);
    resize();

    const render = () => {
      // Fondo negro puro con un ligero fade para rastro de onda
      ctx.fillStyle = 'rgba(5, 7, 10, 0.4)'; 
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const centerY = canvas.height / 2;
      const filterX = canvas.width * 0.5; // El núcleo procesador en el medio
      
      // Dibujar la barrera del motor cuántico (Rust Core)
      ctx.beginPath();
      ctx.moveTo(filterX, 0);
      ctx.lineTo(filterX, canvas.height);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.setLineDash([5, 5]);
      ctx.stroke();
      ctx.setLineDash([]); // Reset

      // Dibujar la Onda de Frecuencia
      ctx.beginPath();
      for (let x = 0; x < canvas.width; x += 2) { 
        // Onda base real (el movimiento verdadero del dron que queremos mantener)
        const baseWave = Math.sin((x * 0.015) - time) * 30; 
        
        let finalY = centerY + baseWave;

        // Zona Izquierda (Caos / Ruido del motor a 12,000 RPM)
        if (x < filterX) {
           // Añadir armónicos de alta frecuencia y ruido aleatorio simulando el chasis vibrando
           const chaoticNoise = (Math.random() - 0.5) * 60; 
           const harmonicVibration = Math.sin((x * 0.2) - (time * 8)) * 20; 
           finalY += chaoticNoise + harmonicVibration;
        }

        if (x === 0) {
          ctx.moveTo(x, finalY);
        } else {
          ctx.lineTo(x, finalY);
        }
      }
      
      // Crear un gradiente de color para la onda (Rojo = Peligro/Ruido, Cyan = Seguro/Limpio)
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
      gradient.addColorStop(0, '#ff0055'); // Rojo
      gradient.addColorStop(0.48, '#ff0055'); // Rojo hasta el centro
      gradient.addColorStop(0.5, '#ffffff'); // Destello blanco de procesamiento (7.91ns)
      gradient.addColorStop(0.52, '#00f0ff'); // Cyan perfecto desde el centro
      gradient.addColorStop(1, '#00f0ff');
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2.5;
      ctx.lineJoin = 'round';
      
      // Efecto Glow Holográfico
      ctx.shadowBlur = 15;
      ctx.shadowColor = '#00f0ff';
      ctx.stroke();
      
      ctx.shadowBlur = 0;

      // Velocidad extrema del flujo de datos
      time += 0.25; 
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="w-full h-64 md:h-80 relative bg-[#05070a] border border-white/10 overflow-hidden">
      {/* HUD Telemetry Overlay */}
      <div className="absolute top-4 left-4 text-[#ff0055] font-mono text-[10px] tracking-widest z-10 flex flex-col gap-1 pointer-events-none">
        <span>[ RAW IMU TELEMETRY ]</span>
        <span className="opacity-70 text-[9px]">NOISE: 12,000 RPM HARMONICS</span>
        <span className="opacity-70 text-[9px]">STATUS: CATASTROPHIC VIBRATION</span>
      </div>
      
      <div className="absolute top-4 right-4 text-[#00f0ff] font-mono text-[10px] tracking-widest z-10 text-right flex flex-col gap-1 pointer-events-none">
        <span>[ SINGULARITY PURIFIED SIGNAL ]</span>
        <span className="opacity-70 text-[9px]">PROCESS TIME: 7.91ns</span>
        <span className="opacity-70 text-[9px]">STATUS: STABLE TRAJECTORY</span>
      </div>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/40 font-mono text-[9px] tracking-[0.3em] z-10 text-center uppercase pointer-events-none">
        Tzanix Rust Core // In-Flight Mode
      </div>
      
      <canvas ref={canvasRef} className="absolute inset-0 block w-full h-full" />
    </div>
  );
};

export default SingularityHologram;
