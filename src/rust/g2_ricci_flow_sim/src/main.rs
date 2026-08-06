use std::fs::File;
use std::io::Write;

fn main() {
    println!("=== 7D G2 Ricci Flow & Torsion Simulation ===");

    let mut tau: f64 = 0.0;
    let mut a: f64 = 2.0;
    let d_tau: f64 = 0.0001;
    let steps: usize = 50000;

    let mut results: Vec<(f64, f64)> = Vec::with_capacity(steps);

    for step in 0..steps {
        let ricci_term = -0.5 / (a * a * a);
        let l_planck_pow6: f64 = 1.0e-6; 
        let torsion_pressure = 0.002 * l_planck_pow6 / (a.powi(6) + 1.0e-12);

        let da_dtau = ricci_term + torsion_pressure;

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

    let mut file = File::create("ricci_flow_trajectory.csv").expect("Kunde inte skapa fil");
    writeln!(file, "tau,scale_factor_a").unwrap();
    for (t, scale) in results {
        writeln!(file, "{},{}", t, scale).unwrap();
    }
    println!("\nSimulering klar! Trajektoria sparad till 'ricci_flow_trajectory.csv'.");
}
