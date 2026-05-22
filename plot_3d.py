import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from optimization_core import cost_function, check_feasibility


def plot_3d_surface(L_opt=None, S_opt=None, save_path=None):
    L_vals = np.linspace(1, 15, 80)
    S_vals = np.linspace(1, 12, 80)
    L_grid, S_grid = np.meshgrid(L_vals, S_vals)

    cost = np.zeros_like(L_grid)
    for i in range(L_grid.shape[0]):
        for j in range(L_grid.shape[1]):
            cost[i, j] = cost_function([L_grid[i, j], S_grid[i, j]])

    feasible = np.zeros_like(L_grid, dtype=bool)
    for i in range(L_grid.shape[0]):
        for j in range(L_grid.shape[1]):
            feasible[i, j] = check_feasibility(L_grid[i, j], S_grid[i, j])

    cost_masked = np.where(feasible, cost, np.nan)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(L_grid, S_grid, cost_masked,
                           cmap=cm.viridis,
                           alpha=0.85,
                           linewidth=0,
                           antialiased=True,
                           rstride=2,
                           cstride=2)

    if L_opt is not None and S_opt is not None:
        cost_opt = cost_function([L_opt, S_opt])
        ax.scatter(L_opt, S_opt, cost_opt,
                   color='red',
                   s=200,
                   marker='*',
                   edgecolors='black',
                   linewidth=2,
                   label=f'Минимум: ({L_opt:.2f}, {S_opt:.2f}, {cost_opt:.0f})')

        ax.plot([L_opt, L_opt], [S_opt, S_opt], [0, cost_opt],
                color='red', linestyle='--', alpha=0.7)
        ax.plot([L_opt, L_opt], [1, S_opt], [cost_opt, cost_opt],
                color='red', linestyle='--', alpha=0.5)
        ax.plot([1, L_opt], [S_opt, S_opt], [cost_opt, cost_opt],
                color='red', linestyle='--', alpha=0.5)

    ax.set_xlabel('Длина L (м)', fontsize=12, labelpad=12)
    ax.set_ylabel('Ширина S (м)', fontsize=12, labelpad=12)
    ax.set_zlabel('Затраты (у.е.)', fontsize=12, labelpad=12)

    ax.set_title('Поверхность отклика целевой функции с ограничениями',
                 fontsize=14, fontweight='bold', pad=20)

    fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, pad=0.1,
                 label='Затраты (у.е.)')

    ax.view_init(elev=25, azim=45)

    if L_opt is not None:
        ax.legend(loc='upper left', fontsize=10)

    ax.grid(True, alpha=0.3)

    ax.set_xlim([1, 15])
    ax.set_ylim([1, 12])

    xx = np.linspace(1, 15, 50)
    yy = np.maximum(1, 12 - xx)
    yy = np.minimum(12, yy)
    ax.plot(xx, yy, 0, color='darkblue', linewidth=2, alpha=0.7,
            label='L + S = 12')

    zz = np.linspace(0, np.nanmax(cost_masked), 10)
    for z in zz:
        ax.plot(xx, yy, z, color='darkblue', alpha=0.1, linewidth=0.5)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"3D график сохранен: {save_path}")

    return fig