// Compilando con std temporalmente para compatibilidad rápida en PC

/// Filtro adaptativo rápido de Rust exportado para C/C++
///
/// # Argumentos
/// * `raw_sample` - La muestra ruidosa entrante del sensor IMU.
/// * `prev_clean` - El último valor limpio calculado por el filtro.
/// * `alpha` - El coeficiente de filtrado (ej. 0.05).
#[no_mangle]
pub extern "C" fn tzanix_filter_c(raw_sample: f64, prev_clean: f64, alpha: f64) -> f64 {
    prev_clean + alpha * (raw_sample - prev_clean)
}

/// Procesamiento por lotes (batch) exportado para C/C++
/// Permite procesar un array completo de muestras directamente en la memoria
#[no_mangle]
pub extern "C" fn tzanix_filter_batch_c(
    raw_samples: *const f64,
    clean_samples: *mut f64,
    length: usize,
    mut initial_clean: f64,
    alpha: f64,
) {
    if raw_samples.is_null() || clean_samples.is_null() || length == 0 {
        return;
    }

    unsafe {
        let raw_slice = core::slice::from_raw_parts(raw_samples, length);
        let clean_slice = core::slice::from_raw_parts_mut(clean_samples, length);

        for i in 0..length {
            initial_clean = initial_clean + alpha * (raw_slice[i] - initial_clean);
            clean_slice[i] = initial_clean;
        }
    }
}

use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct TzanixEngine {
    prev_clean: f64,
    alpha: f64,
}

#[wasm_bindgen]
impl TzanixEngine {
    #[wasm_bindgen(constructor)]
    pub fn new(alpha: f64) -> TzanixEngine {
        TzanixEngine {
            prev_clean: 0.0,
            alpha,
        }
    }

    pub fn filter_sample(&mut self, raw_sample: f64) -> f64 {
        self.prev_clean = self.prev_clean + self.alpha * (raw_sample - self.prev_clean);
        self.prev_clean
    }
}
