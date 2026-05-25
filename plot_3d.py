import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from optimization_core import cost_function, check_feasibility


def plot_3d_surface(T1_opt=None, T2_opt=None, save_path=None):
    T1_vals = np.linspace(-3.0, 0.0, 80)
    T2_vals = np.linspace(-0.5, 3.0, 80)
    T1_grid, T2_grid = np.meshgrid(T1_vals, T2_vals)

    cost = np.zeros_like(T1_grid, dtype=float)
    for i in range(T1_grid.shape[0]):
        for j in range(T1_grid.shape[1]):
            cost[i, j] = cost_function([T1_grid[i, j], T2_grid[i, j]])

    feasible = np.zeros_like(T1_grid, dtype=bool)
    for i in range(T1_grid.shape[0]):
        for j in range(T1_grid.shape[1]):
            feasible[i, j] = check_feasibility(T1_grid[i, j], T2_grid[i, j])

    cost_masked = np.where(feasible, cost, np.nan)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(
        T1_grid, T2_grid, cost_masked,
        cmap=cm.viridis,
        alpha=0.85,
        linewidth=0,
        antialiased=True,
        rstride=2,
        cstride=2
    )

    if T1_opt is not None and T2_opt is not None:
        cost_opt = cost_function([T1_opt, T2_opt])
        ax.scatter(
            T1_opt, T2_opt, cost_opt,
            color='red',
            s=200,
            marker='*',
            edgecolors='black',
            linewidth=2,
            label=f'Минимум: ({T1_opt:.2f}, {T2_opt:.2f}, {cost_opt:.2f})'
        )

        ax.plot([T1_opt, T1_opt], [T2_opt, T2_opt], [0, cost_opt],
                color='red', linestyle='--', alpha=0.7)

    ax.set_xlabel('Температура T1 (°C)', fontsize=12, labelpad=12)
    ax.set_ylabel('Температура T2 (°C)', fontsize=12, labelpad=12)
    ax.set_zlabel('Себестоимость (у.е.)', fontsize=12, labelpad=12)

    ax.set_title('Поверхность целевой функции с ограничениями',
                 fontsize=14, fontweight='bold', pad=20)

    fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, pad=0.1, label='Себестоимость (у.е.)')

    ax.view_init(elev=25, azim=45)

    if T1_opt is not None and T2_opt is not None:
        ax.legend(loc='upper left', fontsize=10)

    ax.grid(True, alpha=0.3)
    ax.set_xlim([-3.0, 0.0])
    ax.set_ylim([-0.5, 3.0])

    return fig