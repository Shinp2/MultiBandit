#!/usr/bin/env python3
"""
Run MultiBandit for different time values, aggregate results, and plot time vs accumulated reward (AR).

Usage: run with system python if graph-tool is installed in system site-packages.
"""
import os
import sys
import statistics
import math
import argparse

import numpy as np
import matplotlib.pyplot as plt
import importlib.util
from ci_utils import ci_halfwidth


def import_multibandit_module():
    """Locate and import the MultiBandit module.

    This function first tries to directly load a file named
    MultiBandit.py / Multibandit.py / multibandit.py from the same
    directory as this script.
    """
    script_dir = os.path.dirname(__file__)

    # 1) Try direct file-based import from the same directory
    last_exc = None
    attempted = []
    for fname in ("MultiBandit.py", "Multibandit.py", "multibandit.py"):
        path = os.path.join(script_dir, fname)
        if os.path.isfile(path):
            try:
                spec = importlib.util.spec_from_file_location("multibandit_local", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            except Exception as e:
                last_exc = e
        attempted.append(path)
    
    msg = f"Failed to import MultiBandit module from script directory. Tried paths:\n" + "\n".join(attempted)
    if last_exc is not None:
        raise ImportError(msg) from last_exc
    else:
        raise ImportError(msg)


def run_experiment(times, repeats, epsilon, theta, python_exe=None, ci_conf=0.95):
    mb = import_multibandit_module()

    means = []
    stds = []
    all_vals = []

    for t in times:
        vals = []
        for _ in range(repeats):
            # Each run may return (AR, arms) or just AR; normalize to numeric AR
            out = mb.MultiBandit(epsilon, theta, time=int(t))
            if isinstance(out, tuple):
                ar = out[0]
            else:
                ar = out
            vals.append(float(ar))
        all_vals.append(vals)
        means.append(statistics.mean(vals))
        # keep population std dev for compatibility but CI will be computed below
        stds.append(statistics.pstdev(vals))
    # Normalize by time to get "per-step" values
    per_step_means = np.array([m / t for m, t in zip(means, times)])
    # compute 95% CI half-widths (in raw AR units) then normalize by time
    cis = [ci_halfwidth(v, conf=ci_conf) for v in all_vals]
    per_step_cis = np.array([c / t for c, t in zip(cis, times)])
    # Return per_step_cis in place of per_step_stds so plotting uses CI half-widths
    return times, per_step_means, per_step_cis, all_vals


def run_experiment_over_epsilons(fixed_time, repeats, epsilons, theta, ci_conf=0.95):
    """Run experiments for a fixed time value while varying epsilon.

    Returns: (epsilons, per_step_means, per_step_stds, all_vals)
    where per_step_means/stds are normalized by fixed_time.
    """
    mb = import_multibandit_module()

    means = []
    stds = []
    all_vals = []

    for eps in epsilons:
        vals = []
        for _ in range(repeats):
            out = mb.MultiBandit(eps, theta, time=int(fixed_time))
            if isinstance(out, tuple):
                ar = out[0]
            else:
                ar = out
            vals.append(float(ar))
        all_vals.append(vals)
        means.append(statistics.mean(vals))
        stds.append(statistics.pstdev(vals))

    per_step_means = np.array([m / fixed_time for m in means])
    cis = [ci_halfwidth(v, conf=ci_conf) for v in all_vals]
    per_step_cis = np.array([c / fixed_time for c in cis])
    return epsilons, per_step_means, per_step_cis, all_vals


def plot_and_save(times, means, cis, out_path="time_vs_ar.png", ci_threshold=0.01, enable_converge=True):
    plt.figure(figsize=(8, 5))
    # errorbars: cis are half-widths
    plt.errorbar(times, means, yerr=cis, fmt='none', ecolor='gray', capsize=4)
    times = np.array(times)
    means = np.array(means)
    if enable_converge:
        # color points by convergence: blue = converged, red = not converged
        converged = np.array(cis) <= ci_threshold
        plt.scatter(times[converged], means[converged], color='blue', label='converged')
        plt.scatter(times[~converged], means[~converged], color='red', label='not converged')
        # connect points for visibility
        plt.plot(times, means, color='black', linewidth=0.8, alpha=0.6)
    else:
        # single color plot when convergence coloring disabled
        plt.scatter(times, means, color='tab:blue')
        plt.plot(times, means, color='tab:blue', linewidth=0.8, alpha=0.6)
    plt.xscale('log') if max(times) / min(times) >= 10 else None
    plt.xlabel('time (number of steps)')
    plt.ylabel('avg reward per step (AR / time)')
    plt.title('Time vs Avg Reward per Step')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"wrote {out_path}")


def plot_x_vs_ar(x_vals, means, cis, xlabel='epsilon', out_path='epsilon_vs_ar.png', ci_threshold=0.01, enable_converge=True):
    plt.figure(figsize=(8, 5))
    plt.errorbar(x_vals, means, yerr=cis, fmt='none', ecolor='gray', capsize=4)
    x_vals = np.array(x_vals)
    means = np.array(means)
    if enable_converge:
        converged = np.array(cis) <= ci_threshold
        plt.scatter(x_vals[converged], means[converged], color='blue', label='converged')
        plt.scatter(x_vals[~converged], means[~converged], color='red', label='not converged')
    else:
        plt.scatter(x_vals, means, color='tab:blue')
    plt.xlabel(xlabel)
    plt.ylabel('avg reward per step (AR / time)')
    plt.title(f'{xlabel} vs Avg Reward per Step')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"wrote {out_path}")


def run_experiment_over_Ks(Ks, repeats, fixed_time, epsilon, mean, std, samples, seed=None, ci_conf=0.95):
    """For each K in Ks, sample `samples` different theta vectors of length K
    from Normal(mean,std) (clipped to [0,1]), run `repeats` per sample,
    and return (Ks, per_step_means, per_step_stds, all_vals).
    all_vals contains raw AR values (not normalized) per K.
    """
    mb = import_multibandit_module()
    rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()

    means = []
    stds = []
    all_vals = []

    for K in Ks:
        vals = []
        for s in range(samples):
            sampled = rng.normal(loc=mean, scale=std, size=K)
            sampled = np.clip(sampled, 0.0, 1.0)
            theta_list = sampled.tolist()
            for _ in range(repeats):
                out = mb.MultiBandit(epsilon, theta_list, time=int(fixed_time))
                ar = out[0] if isinstance(out, tuple) else out
                vals.append(float(ar))
        all_vals.append(vals)
        means.append(statistics.mean(vals))
        stds.append(statistics.pstdev(vals) if len(vals) > 1 else 0.0)

    per_step_means = np.array([m / fixed_time for m in means])
    cis = [ci_halfwidth(v, conf=ci_conf) for v in all_vals]
    per_step_cis = np.array([c / fixed_time for c in cis])
    return Ks, per_step_means, per_step_cis, all_vals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--times', nargs='+', type=int,
                        default=[10, 50, 100, 500, 1000],
                        help='list of time values to evaluate')
    parser.add_argument('--repeats', type=int, default=30, help='repeats per time')
    parser.add_argument('--epsilon', type=float, default=0.1)
    parser.add_argument('--theta', nargs='+', type=float, default=[0.3, 0.7],
                        help='explicit list of theta values for each arm (overrides --K if provided)')
    parser.add_argument('--K', type=int, default=2,
                        help='number of arms (default 500); used when sampling theta')
    parser.add_argument('--theta-normal', nargs=2, type=float, metavar=('MEAN', 'STD'),
                        help='sample K theta values from Normal(MEAN,STD) and clip to [0,1]; requires --K')
    parser.add_argument('--seed', type=int, default=None, help='random seed for theta sampling')
    parser.add_argument('--out', type=str, default=os.path.join(os.path.dirname(__file__), 'time_vs_ar.png'))
    parser.add_argument('--epsilons', nargs='+', type=float,
                        help='list of epsilon values to evaluate; if provided, time is fixed (see --fixed-time)')
    parser.add_argument('--fixed-time', type=int, default=6500,
                        help='when varying epsilon, use this fixed time value (default: 6500)')
    parser.add_argument('--Ks', nargs='+', type=int,
                        help='list of K (number of arms) values to sweep')
    parser.add_argument('--theta-mean', type=float, default=0.5,
                        help='mean for theta normal sampler when sweeping K')
    parser.add_argument('--theta-std', type=float, default=0.1,
                        help='stddev for theta normal sampler when sweeping K')
    parser.add_argument('--theta-samples', type=int, default=1,
                        help='number of random theta draws per K (averaged)')
    parser.add_argument('--ci-conf', type=float, default=0.95,
                        help='confidence level for CI (e.g. 0.95)')
    parser.add_argument('--ci-threshold', type=float, default=0.01,
                        help='threshold for CI half-width (per-step) to consider converged')
    # enable/disable coloring by convergence
    if hasattr(argparse, 'BooleanOptionalAction'):
        parser.add_argument('--converge', action=argparse.BooleanOptionalAction, default=True,
                            help='enable/disable convergence coloring (default: enabled)')
    else:
        parser.add_argument('--converge', action='store_true', default=True,
                            help='enable convergence coloring (default: enabled)')
    args = parser.parse_args()

    # Decide how to obtain theta (per-arm probabilities).
    # Priority:
    # 1) explicit --theta passed on command line
    # 2) explicit --theta-normal passed on command line
    # 3) default behavior: sample args.K theta values from Normal(theta-mean, theta-std)
    def arg_present(name):
        return any(a == name or a.startswith(name + "=") for a in sys.argv)

    if arg_present('--theta'):
        # user provided explicit theta list; if K was specified, validate length
        if args.K is not None and len(args.theta) != args.K:
            parser.error(f'--K={args.K} but provided --theta has length {len(args.theta)}')
    elif args.theta_normal:
        # user requested theta sampling via --theta-normal
        mean, std = args.theta_normal
        rng = np.random.default_rng(args.seed) if args.seed is not None else np.random.default_rng()
        sampled = rng.normal(loc=mean, scale=std, size=args.K)
        sampled = np.clip(sampled, 0.0, 1.0)
        args.theta = sampled.tolist()
    else:
        # default: sample args.K theta values from Normal(theta-mean, theta-std)
        rng = np.random.default_rng(args.seed) if args.seed is not None else np.random.default_rng()
        sampled = rng.normal(loc=args.theta_mean, scale=args.theta_std, size=args.K)
        sampled = np.clip(sampled, 0.0, 1.0)
        args.theta = sampled.tolist()

    if args.epsilons:
        # Vary epsilon on x-axis, keep time fixed
        epsilons, means, cis, all_vals = run_experiment_over_epsilons(
            args.fixed_time, args.repeats, args.epsilons, args.theta, ci_conf=args.ci_conf)
        out_path = args.out
        # if default out was time_vs_ar.png, prefer epsilon filename
        if out_path.endswith('time_vs_ar.png'):
            out_path = os.path.join(os.path.dirname(__file__), 'epsilon_vs_ar.png')
        plot_x_vs_ar(epsilons, means, cis, xlabel='epsilon', out_path=out_path,
                     ci_threshold=args.ci_threshold, enable_converge=args.converge)
        return

    # Sweep over K (number of arms) with theta sampled from Normal(mean,std)
    if args.Ks:
        Ks, means_k, cis_k, all_vals_k = run_experiment_over_Ks(
            args.Ks, args.repeats, args.fixed_time,
            args.epsilon, args.theta_mean, args.theta_std,
            args.theta_samples, args.seed, ci_conf=args.ci_conf)
        out_path = args.out
        if out_path.endswith('time_vs_ar.png'):
            out_path = os.path.join(os.path.dirname(__file__), 'Ks_vs_ar.png')
        plot_x_vs_ar(Ks, means_k, cis_k, xlabel='K (number of arms)', out_path=out_path,
                     ci_threshold=args.ci_threshold, enable_converge=args.converge)
        return
    else:
        times, means, cis, all_vals = run_experiment(
            args.times, args.repeats, args.epsilon, args.theta, ci_conf=args.ci_conf)
        plot_and_save(times, means, cis, out_path=args.out, ci_threshold=args.ci_threshold,
                      enable_converge=args.converge)


if __name__ == '__main__':
    main()
