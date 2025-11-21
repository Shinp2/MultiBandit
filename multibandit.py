"""
Multi-Armed Bandit Algorithm Implementation

This module implements various multi-armed bandit algorithms for
exploration-exploitation tradeoffs in reinforcement learning.
"""

import numpy as np
from typing import List, Optional


class MultiBandit:
    """
    Multi-Armed Bandit implementation with various selection strategies.
    
    This class implements a multi-armed bandit problem solver with support
    for different arm selection strategies including epsilon-greedy,
    UCB (Upper Confidence Bound), and Thompson Sampling.
    
    Attributes:
        n_arms (int): Number of arms (actions) available
        counts (np.ndarray): Number of times each arm has been pulled
        values (np.ndarray): Estimated value (mean reward) for each arm
        rewards (List[List[float]]): History of rewards for each arm
    """
    
    def __init__(self, n_arms: int):
        """
        Initialize the Multi-Armed Bandit.
        
        Args:
            n_arms (int): Number of arms in the bandit
        """
        if n_arms <= 0:
            raise ValueError("Number of arms must be positive")
        
        self.n_arms = n_arms
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)
        self.rewards = [[] for _ in range(n_arms)]
    
    def select_arm_epsilon_greedy(self, epsilon: float = 0.1) -> int:
        """
        Select an arm using epsilon-greedy strategy.
        
        With probability epsilon, explore by choosing a random arm.
        With probability (1-epsilon), exploit by choosing the best arm.
        
        Args:
            epsilon (float): Exploration probability (default: 0.1)
            
        Returns:
            int: Index of the selected arm
        """
        if np.random.random() < epsilon:
            return np.random.randint(0, self.n_arms)
        else:
            return int(np.argmax(self.values))
    
    def select_arm_ucb(self, t: int, c: float = 2.0) -> int:
        """
        Select an arm using Upper Confidence Bound (UCB) strategy.
        
        UCB balances exploration and exploitation by considering both
        the estimated value and the uncertainty (confidence interval).
        
        Args:
            t (int): Current time step (total number of pulls)
            c (float): Exploration parameter (default: 2.0)
            
        Returns:
            int: Index of the selected arm
        """
        # If any arm hasn't been pulled yet, pull it first
        for arm in range(self.n_arms):
            if self.counts[arm] == 0:
                return arm
        
        # Calculate UCB values for each arm
        ucb_values = self.values + c * np.sqrt(
            np.log(t + 1) / (self.counts + 1e-5)
        )
        return int(np.argmax(ucb_values))
    
    def select_arm_thompson_sampling(self, alpha: float = 1.0, beta: float = 1.0) -> int:
        """
        Select an arm using Thompson Sampling (Bayesian approach).
        
        Assumes Beta prior for Bernoulli rewards. For continuous rewards,
        this serves as an approximation.
        
        Args:
            alpha (float): Alpha parameter for Beta prior (default: 1.0)
            beta (float): Beta parameter for Beta prior (default: 1.0)
            
        Returns:
            int: Index of the selected arm
        """
        samples = np.random.beta(
            alpha + self.counts,
            beta + (np.sum(self.counts) - self.counts + 1)
        )
        return int(np.argmax(samples))
    
    def update(self, arm: int, reward: float) -> None:
        """
        Update the bandit's statistics after pulling an arm.
        
        Args:
            arm (int): Index of the arm that was pulled
            reward (float): Reward received from pulling the arm
        """
        if arm < 0 or arm >= self.n_arms:
            raise ValueError(f"Invalid arm index: {arm}")
        
        self.counts[arm] += 1
        self.rewards[arm].append(reward)
        
        # Update the estimated value using incremental mean
        n = self.counts[arm]
        value = self.values[arm]
        self.values[arm] = ((n - 1) / n) * value + (1 / n) * reward
    
    def get_best_arm(self) -> int:
        """
        Get the arm with the highest estimated value.
        
        Returns:
            int: Index of the best arm
        """
        return int(np.argmax(self.values))
    
    def get_statistics(self) -> dict:
        """
        Get current statistics of the bandit.
        
        Returns:
            dict: Dictionary containing counts, values, and total pulls
        """
        return {
            'counts': self.counts.tolist(),
            'values': self.values.tolist(),
            'total_pulls': int(np.sum(self.counts)),
            'best_arm': self.get_best_arm()
        }
    
    def reset(self) -> None:
        """Reset the bandit to initial state."""
        self.counts = np.zeros(self.n_arms)
        self.values = np.zeros(self.n_arms)
        self.rewards = [[] for _ in range(self.n_arms)]


def simulate_bandit(
    n_arms: int,
    true_rewards: List[float],
    n_iterations: int,
    strategy: str = 'epsilon_greedy',
    **strategy_params
) -> MultiBandit:
    """
    Simulate a multi-armed bandit experiment.
    
    Args:
        n_arms (int): Number of arms
        true_rewards (List[float]): True mean reward for each arm
        n_iterations (int): Number of iterations to run
        strategy (str): Strategy to use ('epsilon_greedy', 'ucb', 'thompson')
        **strategy_params: Additional parameters for the strategy
        
    Returns:
        MultiBandit: The bandit after simulation
    """
    if len(true_rewards) != n_arms:
        raise ValueError("Length of true_rewards must match n_arms")
    
    bandit = MultiBandit(n_arms)
    
    for t in range(n_iterations):
        # Select arm based on strategy
        if strategy == 'epsilon_greedy':
            epsilon = strategy_params.get('epsilon', 0.1)
            arm = bandit.select_arm_epsilon_greedy(epsilon)
        elif strategy == 'ucb':
            c = strategy_params.get('c', 2.0)
            arm = bandit.select_arm_ucb(t, c)
        elif strategy == 'thompson':
            alpha = strategy_params.get('alpha', 1.0)
            beta = strategy_params.get('beta', 1.0)
            arm = bandit.select_arm_thompson_sampling(alpha, beta)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Generate reward (Gaussian noise around true reward)
        reward = np.random.normal(true_rewards[arm], 1.0)
        
        # Update bandit
        bandit.update(arm, reward)
    
    return bandit


if __name__ == '__main__':
    # Example usage
    print("Multi-Armed Bandit Simulation")
    print("=" * 50)
    
    # Define the problem
    n_arms = 5
    true_rewards = [1.0, 2.0, 3.0, 2.5, 1.5]
    n_iterations = 1000
    
    # Run simulation with epsilon-greedy
    print("\nRunning epsilon-greedy strategy...")
    bandit = simulate_bandit(
        n_arms, true_rewards, n_iterations,
        strategy='epsilon_greedy', epsilon=0.1
    )
    
    stats = bandit.get_statistics()
    print(f"Total pulls: {stats['total_pulls']}")
    print(f"Arm counts: {stats['counts']}")
    print(f"Estimated values: {[f'{v:.2f}' for v in stats['values']]}")
    print(f"True rewards: {true_rewards}")
    print(f"Best arm selected: {stats['best_arm']} (true best: {np.argmax(true_rewards)})")
    
    # Run simulation with UCB
    print("\n" + "=" * 50)
    print("Running UCB strategy...")
    bandit_ucb = simulate_bandit(
        n_arms, true_rewards, n_iterations,
        strategy='ucb', c=2.0
    )
    
    stats_ucb = bandit_ucb.get_statistics()
    print(f"Total pulls: {stats_ucb['total_pulls']}")
    print(f"Arm counts: {stats_ucb['counts']}")
    print(f"Estimated values: {[f'{v:.2f}' for v in stats_ucb['values']]}")
    print(f"Best arm selected: {stats_ucb['best_arm']} (true best: {np.argmax(true_rewards)})")
