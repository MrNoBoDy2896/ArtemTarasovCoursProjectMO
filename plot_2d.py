"""
Модуль для построения 2D визуализаций
"""

import numpy as np
import matplotlib.pyplot as plt
from optimization_core import cost_function, check_feasibility


def create_grid(resolution=200):
    L_vals = np.linspace(0.5, 16, resolution)
    S_vals = np.linspace(0.5, 13, resolution)
    L_grid, S_grid = np.meshgrid(L_vals, S_vals)
    return L_grid, S_grid, L_vals, S_vals


def plot_contour(L_opt=None, S_opt=None, save_path=None):

    L_grid, S_grid, L_vals, S_vals = create_grid()

    cost = np.zeros_like(L_grid)
    for i in range(L_grid.shape[0]):
        for j in range(L_grid.shape[1]):
            cost[i, j] = cost_function([L_grid[i, j], S_grid[i, j]])

    feasible = np.zeros_like(L_grid, dtype=bool)
    for i in range(L_grid.shape[0]):
        for j in range(L_grid.shape[1]):
            feasible[i, j] = check_feasibility(L_grid[i, j], S_grid[i, j])

    fig, ax = plt.subplots(figsize=(12, 10))

    cmap = plt.cm.viridis

    levels = np.linspace(0, 5000, 25)
    contour = ax.contour(L_grid, S_grid, cost,
                         levels=levels,
                         cmap=cmap,
                         linewidths=0.8,
                         alpha=0.7)
    plt.clabel(contour, inline=True, fontsize=8, fmt='%.0f')

    ax.contourf(L_grid, S_grid, feasible,
                levels=[0.5, 1.5],
                colors=['lightgreen'],
                alpha=0.2)

    S_boundary = np.maximum(1, 12 - L_vals)
    S_boundary = np.minimum(12, S_boundary)
    ax.fill_between(L_vals, S_boundary, 12,
                    where=(L_vals >= 1) & (L_vals <= 15),
                    color='lightblue', alpha=0.3,
                    label='Допустимая область')

    if L_opt is not None and S_opt is not None:
        ax.plot(L_opt, S_opt, 'r*',
                markersize=15,
                markeredgewidth=2,
                markeredgecolor='black',
                label=f'Оптимум: L={L_opt:.2f} м, S={S_opt:.2f} м')

    # Настройка осей и заголовка
    ax.set_xlabel('Длина L (м)', fontsize=12)
    ax.set_ylabel('Ширина S (м)', fontsize=12)
    ax.set_title('Линии равного значения целевой функции (затраты, у.е.)',
                 fontsize=14, fontweight='bold')

    ax.grid(True, alpha=0.3, linestyle='--')

    ax.legend(loc='upper right', fontsize=10)

    ax.set_xlim([0.5, 16])
    ax.set_ylim([0.5, 13])

    ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y=12, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=1, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=15, color='red', linestyle='--', alpha=0.5, linewidth=1)

    ax.text(16, 1.2, 'S ≥ 1', fontsize=9, color='red')
    ax.text(16, 11.8, 'S ≤ 12', fontsize=9, color='red')
    ax.text(0.7, 12.5, 'L ≥ 1', fontsize=9, color='red')
    ax.text(14.8, 12.5, 'L ≤ 15', fontsize=9, color='red')
    ax.text(8, 5, 'L + S ≥ 12', fontsize=10,
            color='darkblue', fontweight='bold')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")

    return fig