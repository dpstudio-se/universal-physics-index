use std::fs::File;
use std::io::Write;

/// Beräknar tidsderivatan da/d(tau) för 7D G2 Ricci-flödet med torsion[cite: 1]
fn ricci_derivative(a: f64) -> f64 {
    let ricci_term = -0.5 / (a * a * a);
    let l_planck_pow6: f64 = 1.0e-6;
    let torsion_pressure = 0.002 * l_planck_pow6 / (a.powi(6) + 1.0e-12);
    ricci_term + torsion_pressure
}

fn main() {
    println!("=== Advanced 7D G2 Ricci Flow & Torsion Simulation (RK4 Engine) ===");

    let mut tau: f64 = 0.0;
    let mut a: f64 = 2.0;
    let d_tau: f64 = 0.00005; // Finare steglängd för RK4
    let steps: usize = 100000;

    let mut results: Vec<(f64, f64)> = Vec::with_capacity(steps / 500);

    for step in 0..steps {
        // Runge-Kutta 4 (RK4) steg
        let k1 = ricci_derivative(a);
        let k2 = ricci_derivative(a + 0.5 * d_tau * k1);
        let k3 = ricci_derivative(a + 0.5 * d_tau * k2);
        let k4 = ricci_derivative(a + d_tau * k3);

        let da_dtau = (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0;

        a += da_dtau * d_tau;
        tau += d_tau;

        if a < 0.1 {
            a = 0.1;
        }

        if step % 500 == 0 {
            results.push((tau, a));
            println!("Tau: {:.4} | Metric scale a(tau): {:.6}", tau, a);
        }
    }

    let mut file = File::create("ricci_flow_trajectory_rk4.csv").expect("Kunde inte skapa fil");
    writeln!(file, "tau,scale_factor_a").unwrap();
    for (t, scale) in results {
        writeln!(file, "{},{}", t, scale).unwrap();
    }
    println!("\nSimulering klar! RK4-trajektoria sparad till 'ricci_flow_trajectory_rk4.csv'.");
}
