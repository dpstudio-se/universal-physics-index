//! Toy RK4 demo (software only).
//!
//! Status: SYM illustration — NOT validated G₂ Ricci-flow physics,
//! NOT Omega-1766, NOT a Theory of Everything claim.
//! verification_type when tested: software_test.

use std::fs::File;
use std::io::{BufWriter, Write};

const DEMO_ALPHA: f64 = 1.0e-3;
const DEMO_BETA: f64 = 1.0e-3;
const DEMO_GAMMA: f64 = 1.0e-6;

fn rhs(a: f64, t: f64) -> (f64, f64) {
    let da = -DEMO_ALPHA * a.powi(3) * t.powi(2);
    let dt = -DEMO_BETA * a.powi(2) * t + DEMO_GAMMA * a * t.powi(3);
    (da, dt)
}

fn rk4_step(a: f64, t: f64, d_tau: f64) -> (f64, f64) {
    let (k1_a, k1_t) = rhs(a, t);
    let (k2_a, k2_t) = rhs(a + 0.5 * d_tau * k1_a, t + 0.5 * d_tau * k1_t);
    let (k3_a, k3_t) = rhs(a + 0.5 * d_tau * k2_a, t + 0.5 * d_tau * k2_t);
    let (k4_a, k4_t) = rhs(a + d_tau * k3_a, t + d_tau * k3_t);
    let a_next = a + (d_tau / 6.0) * (k1_a + 2.0 * k2_a + 2.0 * k3_a + k4_a);
    let t_next = t + (d_tau / 6.0) * (k1_t + 2.0 * k2_t + 2.0 * k3_t + k4_t);
    (a_next, t_next)
}

fn main() -> std::io::Result<()> {
    let mut a = 2.0_f64;
    let mut t = 0.5_f64;
    let d_tau = 1.0e-4_f64;
    let steps = 5_000_usize;
    let sample_every = 50_usize;

    let file = File::create("ricci_flow_trajectory_rk4.csv")?;
    let mut w = BufWriter::new(file);
    writeln!(
        w,
        "# SYM toy RK4 demo — not physical Ricci flow / not Omega-1766"
    )?;
    writeln!(w, "tau,scale_factor_a,torsion_T")?;
    writeln!(w, "0.0,{a},{t}")?;

    for i in 1..=steps {
        let (a_next, t_next) = rk4_step(a, t, d_tau);
        a = a_next;
        t = t_next;
        if !a.is_finite() || !t.is_finite() {
            eprintln!("non-finite state at step {i}");
            std::process::exit(1);
        }
        if i % sample_every == 0 || i == steps {
            let tau = i as f64 * d_tau;
            writeln!(w, "{tau},{a},{t}")?;
        }
    }

    println!(
        "Wrote ricci_flow_trajectory_rk4.csv (toy RK4 demo only; not physical G2 Ricci flow)."
    );
    Ok(())
}
