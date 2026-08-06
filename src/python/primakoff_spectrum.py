import numpy as np
import matplotlib.pyplot as plt

def generate_primakoff_spectrum():
    # Fysiska konstanter
    nu_0 = 1700.0  # Centralfrekvens i Hz (1.7 kHz)
    v_0_c = 7.3e-4 # Hastighetsdispersion v0/c (220 km/s)
    
    # Beräkna Doppler-breddning (Delta nu_D)
    delta_nu_D = 0.5 * nu_0 * (v_0_c**2)
    print(f"Doppler broadening scale: {delta_nu_D * 1000:.3f} mHz")
    
    # Skapa frekvensvektor (från nu_0 och 3 mHz uppåt)
    nu = np.linspace(nu_0, nu_0 + 0.003, 1000)
    
    # Beräkna spektral flödesdensitet S_nu
    # Asymmetrisk linjeprofil pga Maxwellian hastighetsdispersion
    S_nu = (2 / np.sqrt(np.pi)) * np.sqrt((nu - nu_0) / delta_nu_D) * np.exp(-(nu - nu_0) / delta_nu_D)
    
    # Visualisering
    plt.figure(figsize=(10, 6))
    plt.plot((nu - nu_0) * 1000, S_nu, color='cyan', linewidth=2)
    plt.fill_between((nu - nu_0) * 1000, S_nu, color='cyan', alpha=0.2)
    
    plt.title("Torstone-to-Photon Primakoff Conversion Spectrum (1.7 kHz)", fontsize=14)
    plt.xlabel("Frequency Shift from Resonance $\\nu - \\nu_0$ (mHz)", fontsize=12)
    plt.ylabel("Normalized Spectral Flux Density $S_\\nu$", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.style.use('dark_background')
    
    # Spara grafen
    output_path = "primakoff_1700Hz_signal.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Spektrum genererat och sparat som {output_path}")
    plt.show()

if __name__ == "__main__":
    generate_primakoff_spectrum()
