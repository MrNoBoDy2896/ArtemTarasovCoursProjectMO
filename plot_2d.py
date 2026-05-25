"""
Модуль для построения 2D визуализаций
"""

import numpy as np
import matplotlib.pyplot as plt
from optimization_core import cost_function, check_feasibility


def create_grid(resolution=200):
    T1_vals = np.linspace(-3.0, 0.0, resolution)
    T2_vals = np.linspace(-0.5, 3.0, resolution)
    T1_grid, T2_grid = np.meshgrid(T1_vals, T2_vals)
    return T1_grid, T2_grid, T1_vals, T2_vals


def plot_contour(T1_opt=None, T2_opt=None, save_path=None):
    T1_grid, T2_grid, T1_vals, T2_vals = create_grid()

    cost = np.zeros_like(T1_grid, dtype=float)
    for i in range(T1_grid.shape[0]):
        for j in range(T1_grid.shape[1]):
            cost[i, j] = cost_function([T1_grid[i, j], T2_grid[i, j]])

    feasible = np.zeros_like(T1_grid, dtype=bool)
    for i in range(T1_grid.shape[0]):
        for j in range(T1_grid.shape[1]):
            feasible[i, j] = check_feasibility(T1_grid[i, j], T2_grid[i, j])

    fig, ax = plt.subplots(figsize=(12, 10))

    levels = 25
    contour = ax.contour(T1_grid, T2_grid, cost, levels=levels, cmap=plt.cm.viridis, linewidths=0.8)
    plt.clabel(contour, inline=True, fontsize=8, fmt='%.0f')

    ax.contourf(T1_grid, T2_grid, feasible, levels=[0.5, 1.5], colors=['lightgreen'], alpha=0.2)

    # Граница T2 - T1 = 3  =>  T2 = T1 + 3
    boundary = T1_vals + 3.0
    ax.fill_between(T1_vals, -0.5, boundary, color='lightblue', alpha=0.25, label='Допустимая область')

    if T1_opt is not None and T2_opt is not None:
        ax.plot(T1_opt, T2_opt, 'r*', markersize=15, markeredgewidth=2,
                markeredgecolor='black', label=f'Оптимум: T1={T1_opt:.2f}°C, T2={T2_opt:.2f}°C')

    ax.set_xlabel('Температура T1 (°C)', fontsize=12)
    ax.set_ylabel('Температура T2 (°C)', fontsize=12)
    ax.set_title('Линии равного значения себестоимости фильтрата', fontsize=14, fontweight='bold')

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    ax.set_xlim([-3.0, 0.0])
    ax.set_ylim([-0.5, 3.0])

    ax.axhline(y=-0.5, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=-3.0, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=0.0, color='red', linestyle='--', alpha=0.5, linewidth=1)

    ax.text(-2.95, -0.35, 'T1 ≥ -3', fontsize=9, color='red')
    ax.text(-2.95, 2.85, 'T1 ≤ 0', fontsize=9, color='red')
    ax.text(-1.0, -0.45, 'T2 ≥ -0.5', fontsize=9, color='red')
    ax.text(-1.0, 2.8, 'T2 ≤ 3', fontsize=9, color='red')
    ax.text(-2.3, 1.3, 'T2 - T1 ≤ 3', fontsize=10, color='darkblue', fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig