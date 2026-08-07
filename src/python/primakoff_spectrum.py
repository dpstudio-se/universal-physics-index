import numpy as np
import matplotlib.pyplot as plt

def generate_primakoff_spectrum():
    print("=== Genererar Torstone Primakoff Radiospektrum (1.7 kHz) ===")
    
    # Fysiska parametrar från teorin
    nu_0 = 1700.0  # Centralfrekvens i Hz (1.7 kHz)
    v_0_c = 7.3e-4 # Hastighetsdispersion v0/c (220 km/s)[cite: 1]
    
    # Doppler-breddningskala
    delta_nu_D = 0.5 * nu_0 * (v_0_c ** 2)
    print(f"Beräknad Doppler-bredd (Delta nu_D): {delta_nu_D * 1000:.3f} mHz")
    
    # Frekvensvektor över resonansen
    nu = np.linspace(nu_0, nu_0 + 0.003, 1000)
    
    # Asymmetrisk linjeprofil baserad på Maxwellian hastighetsdispersion[cite: 1]
    shift = (nu - nu_0)
    S_nu = np.zeros_like(nu)
    valid = shift >= 0
    S_nu[valid] = (2 / np.sqrt(np.pi)) * np.sqrt(shift[valid] / delta_nu_D) * np.exp(-shift[valid] / delta_nu_D)
    
    # Visualisering
    plt.figure(figsize=(10, 6))
    plt.plot((nu[valid] - nu_0) * 1000, S_nu[valid], color='cyan', linewidth=2)
    plt.fill_between((nu[valid] - nu_0) * 1000, S_nu[valid], color='cyan', alpha=0.2)
    plt.title("Torstone-to-Photon Primakoff Conversion Spectrum (1.7 kHz)", fontsize=14)
    plt.xlabel("Frequency Shift from Resonance $\\nu - \\nu_0$ (mHz)", fontsize=12)
    plt.ylabel("Normalized Spectral Flux Density \\nu$", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.style.use('dark_background')
    
    output_path = "src/python/primakoff_1700Hz_signal.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Spektrum sparat till '{output_path}'.")

if __name__ == "__main__":
    generate_primakoff_spectrum()
