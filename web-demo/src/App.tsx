import { useState } from 'react';
import SingularityHologram from './SingularityOscilloscope';

const drones = [
  { id: 'DRONE-AX7', status: 'connected', throughput: '12.4 MB/s', vibration: 'STABLE', noise: 'LOW' },
  { id: 'DRONE-B42', status: 'warning', throughput: '15.1 MB/s', vibration: 'CATASTROPHIC', noise: '15k RPM' },
  { id: 'DRONE-V99', status: 'connected', throughput: '11.8 MB/s', vibration: 'STABLE', noise: 'LOW' },
  { id: 'DRONE-X01', status: 'connected', throughput: '14.2 MB/s', vibration: 'STABLE', noise: 'MED' },
  { id: 'DRONE-K33', status: 'connected', throughput: '12.1 MB/s', vibration: 'STABLE', noise: 'LOW' },
  { id: 'DRONE-Z77', status: 'offline', throughput: '0.0 MB/s', vibration: 'OFFLINE', noise: '--' },
];

function App() {
  const [activeDrone, setActiveDrone] = useState('DRONE-B42');

  return (
    <div className="w-full min-h-screen bg-void text-white p-4 md:p-8 flex flex-col font-sans">
      
      {/* Header Corporativo */}
      <header className="mb-8 border-b border-white/10 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white mb-1 uppercase">TZANiX Singularity</h1>
          <p className="text-sm text-gray-400 font-mono tracking-widest uppercase">Fleet Command Center // v2.0.4-rc</p>
        </div>
        <div className="text-right hidden md:block">
          <div className="text-xs text-tzanix font-mono flex items-center justify-end gap-2">
            <span className="w-2 h-2 rounded-full bg-tzanix animate-pulse"></span>
            SYSTEM ONLINE
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Column: Swarm Grid */}
        <div className="lg:col-span-1 border border-white/10 bg-black/40 rounded-sm p-4 flex flex-col">
          <h2 className="text-sm font-bold text-gray-300 uppercase tracking-widest mb-4 border-b border-white/10 pb-2">Swarm Matrix</h2>
          
          <div className="flex-1 overflow-y-auto space-y-2">
            {drones.map((drone) => (
              <div 
                key={drone.id}
                onClick={() => setActiveDrone(drone.id)}
                className={`p-3 border text-xs font-mono cursor-pointer transition-colors ${
                  activeDrone === drone.id 
                    ? 'border-tzanix bg-tzanix/10 text-tzanix' 
                    : 'border-white/5 bg-white/5 hover:bg-white/10 text-gray-400'
                }`}
              >
                <div className="flex justify-between mb-1">
                  <span className="font-bold">{drone.id}</span>
                  <span className={drone.status === 'warning' ? 'text-danger animate-pulse' : drone.status === 'offline' ? 'text-gray-600' : 'text-tzanix'}>
                    {drone.status === 'warning' ? 'WARN' : drone.status === 'offline' ? 'OFF' : 'OK'}
                  </span>
                </div>
                <div className="flex justify-between text-[10px] opacity-70">
                  <span>{drone.throughput}</span>
                  <span>{drone.noise}</span>
                </div>
              </div>
            ))}
          </div>
          
          <button className="mt-4 w-full py-2 border border-white/20 text-xs font-mono hover:bg-white/10 transition-colors">
            + PROVISION NEW TOKEN
          </button>
        </div>

        {/* Center & Right Columns: Inspector & Telemetry */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          
          {/* Holographic Oscilloscope - Inspector Mode */}
          <div className="border border-white/10 bg-black/40 rounded-sm p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold text-gray-300 uppercase tracking-widest">
                Inspector Mode: <span className={activeDrone === 'DRONE-B42' ? 'text-danger' : 'text-tzanix'}>{activeDrone}</span>
              </h2>
              <span className="text-[10px] font-mono text-gray-500 border border-gray-600 px-2 py-1">LIVE WSS://</span>
            </div>
            
            <SingularityHologram />
            
            {/* Giant Metrics */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="p-4 border border-white/5 bg-white/5">
                <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-1">LATENCIA PROMEDIO</div>
                <div className="text-3xl md:text-4xl font-mono font-bold text-white">7.91 <span className="text-sm text-gray-500">ns</span></div>
              </div>
              <div className="p-4 border border-white/5 bg-white/5">
                <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-1">MUESTRAS / SEGUNDO</div>
                <div className="text-3xl md:text-4xl font-mono font-bold text-white">126,407,068</div>
              </div>
              <div className="p-4 border border-white/5 bg-white/5">
                <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-1">THROUGHPUT TOTAL</div>
                <div className="text-3xl md:text-4xl font-mono font-bold text-white">964.41 <span className="text-sm text-gray-500">MB/s</span></div>
              </div>
            </div>
          </div>

          {/* Predictive Alerts & Server Health */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Alerts */}
            <div className="border border-danger/30 bg-danger/5 rounded-sm p-4 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-danger"></div>
              <h3 className="text-xs font-bold text-danger uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="animate-pulse">⚠️</span> Alertas Mecánicas Predictivas
              </h3>
              <div className="text-sm font-mono text-gray-300">
                <span className="text-danger font-bold">[ DRONE-B42 ]</span> Falla mecánica inminente en motor 3 detectada. 
                El dron mantiene estabilidad de vuelo mediante filtro Tzanix, pero requiere mantenimiento en tierra inmediato. 
                Armónicos exceden límite de fatiga de chasis (15,000 RPM).
              </div>
            </div>

            {/* Server Health */}
            <div className="border border-white/10 bg-black/40 rounded-sm p-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Server Health (Rust Core)</h3>
              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">CORE LOAD</span>
                  <span className="text-tzanix">12%</span>
                </div>
                <div className="w-full bg-white/10 h-1"><div className="bg-tzanix w-[12%] h-full"></div></div>
                
                <div className="flex justify-between pt-2">
                  <span className="text-gray-500">RAM USAGE (WAL)</span>
                  <span className="text-white">42 MB / 32 GB</span>
                </div>
                <div className="w-full bg-white/10 h-1"><div className="bg-white/40 w-[2%] h-full"></div></div>
                
                <div className="flex justify-between pt-2">
                  <span className="text-gray-500">ACTIVE DRONES</span>
                  <span className="text-white">54 / 5000</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>

    </div>
  );
}

export default App;
