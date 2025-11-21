"""
Core multi-armed bandit implementation.
"""

import random
from typing import List, Optional


class Bandit:
    """Represents a single bandit arm with reward probabilities."""
    
    def __init__(self, true_mean: float):
        """
        Initialize a bandit arm.
        
        Args:
            true_mean: The true mean reward for this arm (0-1)
        """
        self.true_mean = true_mean
        self.estimated_mean = 0.0
        self.num_pulls = 0
        
    def pull(self) -> float:
        """
        Pull the bandit arm and get a reward.
        
        Returns:
            Reward value (1 for success, 0 for failure)
        """
        return 1.0 if random.random() < self.true_mean else 0.0
    
    def update(self, reward: float):
        """
        Update the estimated mean based on observed reward.
        
        Args:
            reward: The observed reward
        """
        self.num_pulls += 1
        # Incremental average update
        self.estimated_mean += (reward - self.estimated_mean) / self.num_pulls


class MultiBandit:
    """
    Multi-armed bandit algorithm using epsilon-greedy strategy.
    """
    
    def __init__(self, bandits: List[Bandit], epsilon: float = 0.1):
        """
        Initialize the multi-armed bandit.
        
        Args:
            bandits: List of Bandit arms
            epsilon: Exploration rate (0-1), default 0.1
        """
        self.bandits = bandits
        self.epsilon = epsilon
        self.total_reward = 0.0
        self.num_iterations = 0
        self.history = []
        
    def select_arm(self) -> int:
        """
        Select an arm using epsilon-greedy strategy.
        
        Returns:
            Index of the selected arm
        """
        if random.random() < self.epsilon:
            # Explore: random arm
            return random.randint(0, len(self.bandits) - 1)
        else:
            # Exploit: best arm based on current estimates
            return max(range(len(self.bandits)), 
                      key=lambda i: self.bandits[i].estimated_mean)
    
    def run_iteration(self) -> dict:
        """
        Run one iteration of the bandit algorithm.
        
        Returns:
            Dictionary with iteration results
        """
        arm_index = self.select_arm()
        reward = self.bandits[arm_index].pull()
        self.bandits[arm_index].update(reward)
        
        self.total_reward += reward
        self.num_iterations += 1
        
        # Record history
        result = {
            'iteration': self.num_iterations,
            'arm': arm_index,
            'reward': reward,
            'cumulative_reward': self.total_reward,
            'avg_reward': self.total_reward / self.num_iterations,
            'arm_estimates': [b.estimated_mean for b in self.bandits],
            'arm_pulls': [b.num_pulls for b in self.bandits]
        }
        self.history.append(result)
        
        return result
    
    def run(self, num_iterations: int) -> List[dict]:
        """
        Run the bandit algorithm for multiple iterations.
        
        Args:
            num_iterations: Number of iterations to run
            
        Returns:
            List of iteration results
        """
        for _ in range(num_iterations):
            self.run_iteration()
        
        return self.history
    
    def get_best_arm(self) -> int:
        """
        Get the index of the best arm based on current estimates.
        
        Returns:
            Index of the best arm
        """
        return max(range(len(self.bandits)), 
                  key=lambda i: self.bandits[i].estimated_mean)
