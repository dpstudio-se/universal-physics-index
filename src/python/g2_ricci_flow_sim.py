import csv

def run_simulation():
    print("=== 7D G2 Ricci Flow & Torsion Simulation (Python Engine) ===")

    tau = 0.0
    a = 2.0
    d_tau = 0.0001
    steps = 50000

    results = []

    for step in range(steps):
        # Ricci-krökningsbidrag (drar ihop mångfalden)
        ricci_term = -0.5 / (a * a * a)

        # Repulsiv torsionspress vid Planck-skalan
        l_planck_pow6 = 1.0e-6
        torsion_pressure = 0.002 * l_planck_pow6 / (a**6 + 1.2e-12)

        # Nettoändring av metrikens skala
        da_dtau = ricci_term + torsion_pressure

        a += da_dtau * d_tau
        tau += d_tau

        if a < 0.1:
            a = 0.1

        if step % 500 == 0:
            results.append((tau, a))
            print(f"Tau: {tau:.4f} | Metric scale a(tau): {a:.6f}")

    # Spara resultatet till en CSV-fil
    output_filename = "ricci_flow_trajectory.csv"
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["tau", "scale_factor_a"])
        writer.writerows(results)

    print(f"\nSimulering klar! Trajektoria sparad till '{output_filename}'.")

if __name__ == "__main__":
    run_simulation()
