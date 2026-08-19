use std::f64::consts::PI;
use std::time::Instant;

// Estructura de muestra inercial compacta
#[derive(Clone, Copy)]
struct ImuSample {
    raw_accel: f64,
}

// Filtro adaptativo rápido de Rust
#[inline(always)]
fn tzanix_filter(raw_sample: f64, prev_clean: f64, alpha: f64) -> f64 {
    prev_clean + alpha * (raw_sample - prev_clean)
}

fn main() {
    println!("======================================================");
    println!("🔥 INICIANDO PRUEBA DE ESTRÉS MASIVA - TZANiX ENGINE 🔥");
    println!("======================================================\n");

    // 1. Configuración de Carga Masiva: 10 Millones de Muestras
    let total_samples: usize = 10_000_000;
    println!("📦 Generando vector de datos: {} de muestras...", total_samples);

    let mut dataset: Vec<ImuSample> = Vec::with_capacity(total_samples);
    
    // Generar dataset con ruido caótico extremo
    for i in 0..total_samples {
        let t = i as f64 * 0.001;
        // Señal real + Múltiples armónicos de ruido + picos impredecibles
        let real_motion = 5.0 * (2.0 * PI * 2.0 * t).sin();
        let noise_harmonic_1 = 12.0 * (2.0 * PI * 180.0 * t).sin();
        let noise_harmonic_2 = 8.0 * (2.0 * PI * 450.0 * t).cos();
        let chaotic_spike = if i % 1000 == 0 { 25.0 } else { 0.0 };

        let raw = real_motion + noise_harmonic_1 + noise_harmonic_2 + chaotic_spike;
        dataset.push(ImuSample { raw_accel: raw });
    }

    println!("⚡ Ejecutando filtrado en masa a nivel de registros...");

    // 2. Medición de Rendimiento Extremo
    let mut last_clean = 0.0;
    let mut checksum: f64 = 0.0; // 👈 Acumulador para obligar a calcular cada paso

    let start_time = Instant::now();

    for sample in dataset.iter() {
        last_clean = tzanix_filter(sample.raw_accel, last_clean, 0.05);
        checksum += last_clean; // 👈 Cada muestra afecta la memoria
    }

    let duration = start_time.elapsed();
    let total_seconds = duration.as_secs_f64();
    let total_nanos = duration.as_nanos();

    // 3. Cálculo de Métricas de Rendimiento
    let samples_per_sec = (total_samples as f64) / total_seconds;
    let avg_latency_ns = (total_nanos as f64) / (total_samples as f64);
    let data_throughput_mb = ((total_samples * std::mem::size_of::<f64>()) as f64) / (1024.0 * 1024.0) / total_seconds;

    println!("\n======================================================");
    println!("📊 RESULTADOS DE LA PRUEBA DE ESTRÉS");
    println!("======================================================");
    println!(" Checksum de verificación: {:.4}", checksum);
    println!(" Muestras Procesadas : {}", total_samples);
    println!(" Tiempo Total         : {:.4} segundos ({:?})", total_seconds, duration);
    println!(" Latencia Promedio    : {:.2} nanosegundos (ns) por muestra", avg_latency_ns);
    println!(" Rendimiento (TPS)    : {:.2} Muestras / Segundo", samples_per_sec);
    println!(" Throughput de Datos  : {:.2} MB / segundo", data_throughput_mb);
    println!("======================================================");

    if avg_latency_ns < 1000.0 {
        println!("✅ PRUEBA APROBADA: Latencia Sub-Microsegundo Confirmada");
    } else {
        println!("❌ ADVERTENCIA: La latencia superó el umbral recomendado");
    }
}
