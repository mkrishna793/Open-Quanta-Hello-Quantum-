use pyo3::prelude::*;
use pyo3::types::PyDict;
use num_complex::Complex64;
use rand::Rng;
use std::collections::HashMap;

/// A simple Rust-based statevector simulator
#[pyclass]
struct RustStatevectorSim {
    state: Vec<Complex64>,
    n_qubits: usize,
}

#[pymethods]
impl RustStatevectorSim {
    #[new]
    fn new(n_qubits: usize) -> Self {
        let size = 1_usize << n_qubits;
        let mut state = vec![Complex64::new(0.0, 0.0); size];
        if size > 0 {
            state[0] = Complex64::new(1.0, 0.0);
        }
        RustStatevectorSim { state, n_qubits }
    }

    /// Apply a single qubit gate (given as a 2x2 flat array of real/imag pairs)
    fn apply_single_qubit_gate(&mut self, target: usize, matrix: Vec<(f64, f64)>) {
        let mat = [
            Complex64::new(matrix[0].0, matrix[0].1),
            Complex64::new(matrix[1].0, matrix[1].1),
            Complex64::new(matrix[2].0, matrix[2].1),
            Complex64::new(matrix[3].0, matrix[3].1),
        ];

        let gap = 1_usize << target;
        let mut i = 0;

        // Parallelization opportunity here, but simple sequential for now
        while i < self.state.len() {
            if (i & gap) == 0 {
                let j = i | gap;
                let a = self.state[i];
                let b = self.state[j];

                self.state[i] = mat[0] * a + mat[1] * b;
                self.state[j] = mat[2] * a + mat[3] * b;
            }
            i += 1;
        }
    }

    /// Apply CNOT gate
    fn apply_cnot(&mut self, control: usize, target: usize) {
        let gap_c = 1_usize << control;
        let gap_t = 1_usize << target;

        let mut i = 0;
        while i < self.state.len() {
            if (i & gap_c) != 0 && (i & gap_t) == 0 {
                let j = i | gap_t;
                // Swap amplitudes
                let temp = self.state[i];
                self.state[i] = self.state[j];
                self.state[j] = temp;
            }
            i += 1;
        }
    }

    /// Get probability distribution and sample
    fn measure_and_sample<'py>(&self, py: Python<'py>, shots: usize, measure_map: HashMap<usize, usize>) -> PyResult<Bound<'py, PyDict>> {
        let mut probabilities = vec![0.0; self.state.len()];
        let mut total_prob = 0.0;
        for i in 0..self.state.len() {
            let prob = self.state[i].norm_sqr();
            probabilities[i] = prob;
            total_prob += prob;
        }

        // Normalize
        if total_prob > 0.0 {
            for p in &mut probabilities {
                *p /= total_prob;
            }
        }

        // Sample
        let mut counts: HashMap<String, usize> = HashMap::new();
        let mut rng = rand::thread_rng();

        let num_bits = match measure_map.values().max() {
            Some(&m) => m + 1,
            None => 0,
        };

        for _ in 0..shots {
            let r: f64 = rng.r#gen::<f64>();
            let mut accum = 0.0;
            let mut outcome = 0;

            for (i, &p) in probabilities.iter().enumerate() {
                accum += p;
                if r <= accum {
                    outcome = i;
                    break;
                }
            }
            // Fallback for precision issues
            if accum < r { outcome = probabilities.len() - 1; }

            // Map to classical string
            let mut bits = vec!['0'; num_bits];
            for (q_idx, c_idx) in &measure_map {
                if (outcome & (1 << q_idx)) != 0 {
                    bits[*c_idx] = '1';
                }
            }

            // Reverse so c0 is on the right (Qiskit standard)
            bits.reverse();
            let bit_str: String = bits.into_iter().collect();

            *counts.entry(bit_str).or_insert(0) += 1;
        }

        let py_dict = PyDict::new(py);
        for (k, v) in counts {
            py_dict.set_item(k, v)?;
        }

        Ok(py_dict)
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn openquanta_rust_sim(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustStatevectorSim>()?;
    Ok(())
}
