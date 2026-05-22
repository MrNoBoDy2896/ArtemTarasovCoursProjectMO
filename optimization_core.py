import json
import os
from math import cos

import numpy as np
from scipy.optimize import minimize, differential_evolution, dual_annealing

alpha = 1.0
beta = 1.0
gamma = 1.0
T1 = 9
T2 = 10
price_per_kg = 100
optimization_method = 'SLSQP'

SETTINGS_FILE = 'settings.txt'


def load_settings():
    global alpha, beta, gamma, T1, T2, price_per_kg, optimization_method

    default_settings = {
        'alpha': 1.0,
        'beta': 1.0,
        'gamma': 3.14,
        'T1': 9,
        'T2': 10,
        "p1": 1,
        "p2": 1,
        'price_per_kg': 100,
        'optimization_method': 'SLSQP'
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                alpha = settings.get('alpha', default_settings['alpha'])
                beta = settings.get('beta', default_settings['beta'])
                gamma = settings.get('gamma', default_settings['gamma'])
                T1 = settings.get('T1', default_settings['T1'])
                T2 = settings.get('T2', default_settings['T2'])
                price_per_kg = settings.get('price_per_kg', default_settings['price_per_kg'])
                optimization_method = settings.get('optimization_method', default_settings['optimization_method'])
        except:
            set_default_settings(default_settings)
    else:
        save_settings(default_settings)
        set_default_settings(default_settings)


def set_default_settings(settings):
    global alpha, beta, gamma, T1, T2, p1, p2, price_per_kg, optimization_method
    alpha = settings['alpha']
    beta = settings['beta']
    gamma = settings['gamma']
    T1 = settings['T1']
    T2 = settings['T2']
    p1 = settings["p1"]
    p2 = settings["p2"]

    price_per_kg = settings['price_per_kg']
    optimization_method = settings.get('optimization_method', 'SLSQP')


def save_settings(settings=None):
    if settings is None:
        settings = {
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma,
            'T1': 9,
            'T2': 10,
            "p1": 1,
            "p2": 1,
            'price_per_kg': price_per_kg,
            'optimization_method': optimization_method
        }

    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except:
        pass


def set_parameters(new_alpha, new_beta, new_gamma, new_T1, new_T2, new_p1, new_p2, new_price):
    global alpha, beta, gamma, T1, T2, price_per_kg
    alpha = new_alpha
    beta = new_beta
    gamma = new_gamma
    T1 = new_T1
    T2 = new_T2

    price_per_kg = new_price

    settings = {
        'alpha': alpha,
        'beta': beta,
        'gamma': gamma,
        'T1': new_T1,
        'T2': new_T2,
        "p1": new_p1,
        "p2": new_p2,
        'price_per_kg': price_per_kg,
        'optimization_method': optimization_method
    }
    save_settings(settings)


def set_optimization_method(method):
    global optimization_method
    optimization_method = method
    save_settings()


def get_parameters():
    return {
        'alpha': alpha,
        'beta': beta,
        'gamma': gamma,
        'T1': T1,
        'T2': T2,
        "p1": p1,
        "p2": p2,
        'price_per_kg': price_per_kg,
        'optimization_method': optimization_method
    }


def weight_function(x):
    [T1, T2, p1, p2] = x[0], x[1], x[2], x[3]
    return  alpha * (T1 - beta * p1) * cos(gamma * p2 * (T1^2 + T2^2)**2)


def cost_function(x):
    return weight_function(x) * price_per_kg


def cost_function_with_args(T1, T2, p1, p2):
    return cost_function(T1, T2, p1, p2)


def get_constraints():
    constraints = [
        {'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 12},
        {'type': 'ineq', 'fun': lambda x: x[0] - 1},
        {'type': 'ineq', 'fun': lambda x: 15 - x[0]},
        {'type': 'ineq', 'fun': lambda x: x[1] - 1},
        {'type': 'ineq', 'fun': lambda x: 12 - x[1]}
    ]
    return constraints


def get_bounds():
    return [(1, 15), (1, 12)]


def check_feasibility(T1, T2):
    return (T1 >= -3) & (T1 <= 0) & (T2 >= -0.5) & (T2 <= 3) & (T1 + T2 <= 3)


"""def objective_function(x):

    return cost_function(x)"""

#TODO: целиком переписать методы. [T1, T2, p1, p2] -> x!!!!! ******
def optimize_with_method(method, x0=None):
    bounds = get_bounds()
    constraints = get_constraints()

    if method == 'SLSQP':
        if x0 is None:
            x0 = [8, 6]
        result = minimize(cost_function, x0,
                          constraints=constraints,
                          method='SLSQP',
                          bounds=bounds,
                          tol=0.01)
        return result

    elif method == 'Дифференциальная эволюция':

        def penalized_cost(x):
            c = cost_function(x)
            L, S = x
            penalty = 0
            if L + S < 12:
                penalty += 1e6 * (12 - (L + S)) ** 2
            if L < 1:
                penalty += 1e6 * (1 - L) ** 2
            if L > 15:
                penalty += 1e6 * (L - 15) ** 2
            if S < 1:
                penalty += 1e6 * (1 - S) ** 2
            if S > 12:
                penalty += 1e6 * (S - 12) ** 2
            return c + penalty
        result = differential_evolution(penalized_cost,
                                        bounds=bounds,
                                        tol=0.01,
                                        popsize=15,
                                        maxiter=1000,
                                        seed=42)
        return result

    elif method == 'Имитация отжига':
        result = dual_annealing(cost_function,
                                bounds=bounds,
                                maxiter=1000,
                                initial_temp=5230,
                                visit=2.62,
                                accept=-5.0)
        if result.success:
            L, S = result.x
            if L + S >= 12 and 1 <= L <= 15 and 1 <= S <= 12:
                return result
            else:
                corrected = minimize(cost_function, result.x,
                                     constraints=constraints,
                                     method='SLSQP',
                                     bounds=bounds)
                if corrected.success and corrected.fun < result.fun:
                    return corrected
        return result

    return None


def get_available_methods():
    return ['SLSQP', 'Дифференциальная эволюция', 'Имитация отжига']


load_settings()

print(1245)