import pandas as pd
import matplotlib.pyplot as plt

def plot_trajectory():
    # Läs in RK4-data
    df = pd.read_csv('ricci_flow_trajectory_rk4.csv')

    # Skapa plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['tau'], df['scale_factor_a'], color='orange', linewidth=2, label='a(tau)')
    
    plt.title('7D G2 Ricci Flow: Metric Scale Evolution (RK4)', fontsize=14)
    plt.xlabel('Proper Time (tau)', fontsize=12)
    plt.ylabel('Metric Scale Factor a(tau)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.style.use('dark_background')

    # Spara
    output_path = 'src/python/ricci_flow_trajectory_rk4.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f'Visualisering sparad till {output_path}')

if __name__ == '__main__':
    plot_trajectory()
