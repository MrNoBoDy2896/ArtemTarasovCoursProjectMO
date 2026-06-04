import json
import os
import numpy as np
from scipy.optimize import minimize, differential_evolution, dual_annealing

alpha = 1.0
beta = 1.0
gamma = 3.14
price_per_m3 = 100.0
optimization_method = 'SLSQP'

SETTINGS_FILE = 'settings.txt'

SHIFT_HOURS = 8.0
DP1 = 1.0
DP2 = 1.0


def load_settings():
    global alpha, beta, gamma, price_per_m3, optimization_method

    default_settings = {
        'alpha': 1.0,
        'beta': 1.0,
        'gamma': 3.14,
        'price_per_m3': 100.0,
        'optimization_method': 'SLSQP'
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                alpha = settings.get('alpha', default_settings['alpha'])
                beta = settings.get('beta', default_settings['beta'])
                gamma = settings.get('gamma', default_settings['gamma'])
                price_per_m3 = settings.get('price_per_m3', default_settings['price_per_m3'])
                optimization_method = settings.get('optimization_method', default_settings['optimization_method'])
        except Exception:
            set_default_settings(default_settings)
            save_settings(default_settings)
    else:
        set_default_settings(default_settings)
        save_settings(default_settings)


def set_default_settings(settings):
    global alpha, beta, gamma, price_per_m3, optimization_method
    alpha = settings['alpha']
    beta = settings['beta']
    gamma = settings['gamma']
    price_per_m3 = settings['price_per_m3']
    optimization_method = settings.get('optimization_method', 'SLSQP')


def save_settings(settings=None):
    if settings is None:
        settings = {
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma,
            'price_per_m3': price_per_m3,
            'optimization_method': optimization_method
        }

    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def set_parameters(new_alpha, new_beta, new_gamma, new_price):
    global alpha, beta, gamma, price_per_m3
    alpha = new_alpha
    beta = new_beta
    gamma = new_gamma
    price_per_m3 = new_price

    save_settings()


def set_optimization_method(method):
    global optimization_method
    optimization_method = method
    save_settings()


def get_parameters():
    return {
        'alpha': alpha,
        'beta': beta,
        'gamma': gamma,
        'price_per_m3': price_per_m3,
        'optimization_method': optimization_method
    }


def raw_volume_function(x):
    T1, T2 = x
    return alpha * (T1 - beta * DP1) * np.cos(gamma * DP2 * np.sqrt(T1**2 + T2**2))


def volume_function(x):
    return max(abs(raw_volume_function(x)), 1e-9)


def cost_function(x):
    return SHIFT_HOURS * price_per_m3 * volume_function(x)


def get_constraints():
    return [
        {'type': 'ineq', 'fun': lambda x: x[0] + 3.0},        # T1 >= -3
        {'type': 'ineq', 'fun': lambda x: -x[0]},             # T1 <= 0
        {'type': 'ineq', 'fun': lambda x: x[1] + 0.5},        # T2 >= -0.5
        {'type': 'ineq', 'fun': lambda x: 3.0 - x[1]},        # T2 <= 3
        {'type': 'ineq', 'fun': lambda x: 3.0 - (x[1] - x[0])}  # T2 - T1 <= 3
    ]


def get_bounds():
    return [(-3.0, 0.0), (-0.5, 3.0)]


def check_feasibility(T1, T2):
    return (
        -3.0 <= T1 <= 0.0 and
        -0.5 <= T2 <= 3.0 and
        (T2 - T1) <= 3.0
    )


def optimize_with_method(method, x0=None):
    bounds = get_bounds()
    constraints = get_constraints()

    if x0 is None:
        x0 = [-1.0, 0.0]

    if method == 'SLSQP':
        return minimize(
            cost_function,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            tol=0.01
        )

    elif method == 'Дифференциальная эволюция':
        def penalized_cost(x):
            T1, T2 = x
            penalty = 0.0

            if T1 < -3.0:
                penalty += 1e6 * (-3.0 - T1) ** 2
            if T1 > 0.0:
                penalty += 1e6 * (T1 - 0.0) ** 2
            if T2 < -0.5:
                penalty += 1e6 * (-0.5 - T2) ** 2
            if T2 > 3.0:
                penalty += 1e6 * (T2 - 3.0) ** 2
            if T2 - T1 > 3.0:
                penalty += 1e6 * (T2 - T1 - 3.0) ** 2

            return cost_function(x) + penalty

        return differential_evolution(
            penalized_cost,
            bounds=bounds,
            tol=0.01,
            popsize=15,
            maxiter=1000,
            seed=42
        )

    elif method == 'Имитация отжига':
        def penalized_cost(x):
            T1, T2 = x
            penalty = 0.0

            if T1 < -3.0:
                penalty += 1e6 * (-3.0 - T1) ** 2
            if T1 > 0.0:
                penalty += 1e6 * (T1 - 0.0) ** 2
            if T2 < -0.5:
                penalty += 1e6 * (-0.5 - T2) ** 2
            if T2 > 3.0:
                penalty += 1e6 * (T2 - 3.0) ** 2
            if T2 - T1 > 3.0:
                penalty += 1e6 * (T2 - T1 - 3.0) ** 2

            return cost_function(x) + penalty

        result = dual_annealing(
            penalized_cost,
            bounds=bounds,
            maxiter=1000,
            initial_temp=5230,
            visit=2.62,
            accept=-5.0,
            seed=42
        )

        corrected = minimize(
            cost_function,
            result.x,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            tol=0.01
        )

        if corrected.success and check_feasibility(corrected.x[0], corrected.x[1]):
            return corrected

        return result

    return None


def get_available_methods():
    return ['SLSQP', 'Дифференциальная эволюция', 'Имитация отжига']


load_settings()