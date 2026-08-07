import csv
import math

# Axiom 1766: Koppling mellan kosmiska basen (NWA 1766), tryckfrihet (TF1766) och ursprung
OMEGA_1766 = 1766.0  

def ricci_derivative(a):
    ricci_term = -0.5 / (a * a * a)
    l_planck_pow6 = 1.0e-6
    # Inkluderar Omega-1766 som en topologisk modulationsfaktor för torsionspressen
    torsion_pressure = (0.002 * l_planck_pow6 / (a**6 + 1.2e-12)) * (1.0 + 1.0 / OMEGA_1766)
    return ricci_term + torsion_pressure

def run_rk4_simulation():
    print(f"=== Advanced 7D G2 Ricci Flow & Torsion Simulation (Omega-{OMEGA_1766} Engine) ===")

    tau = 0.0
    a = 2.0
    d_tau = 0.00005
    steps = 100000

    results = []

    for step in range(steps):
        k1 = ricci_derivative(a)
        k2 = ricci_derivative(a + 0.5 * d_tau * k1)
        k3 = ricci_derivative(a + 0.5 * d_tau * k2)
        k4 = ricci_derivative(a + d_tau * k3)

        da_dtau = (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

        a += da_dtau * d_tau
        tau += d_tau

        if a < 0.1:
            a = 0.1

        if step % 500 == 0:
            results.append((tau, a))
            print(f"Tau: {tau:.4f} | Metric scale a(tau): {a:.6f}")

    output_filename = "ricci_flow_trajectory_rk4.csv"
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["tau", "scale_factor_a"])
        writer.writerows(results)

    print(f"\nSimulering klar! Trajektoria med Omega-1766 sparad till '{output_filename}'.")

if __name__ == "__main__":
    run_rk4_simulation()
