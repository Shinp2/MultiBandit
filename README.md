# MultiBandit

A Python implementation of Multi-Armed Bandit algorithms for exploration-exploitation tradeoffs in reinforcement learning.

## Features

- **Multiple Selection Strategies:**
  - Epsilon-Greedy: Balance exploration and exploitation with a tunable epsilon parameter
  - UCB (Upper Confidence Bound): Systematic exploration based on uncertainty
  - Thompson Sampling: Bayesian approach to arm selection

- **Easy to Use API:** Simple interface for running bandit simulations
- **Comprehensive Statistics:** Track arm pulls, estimated values, and performance

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from multibandit import MultiBandit, simulate_bandit

# Create a bandit with 5 arms
n_arms = 5
true_rewards = [1.0, 2.0, 3.0, 2.5, 1.5]

# Run simulation with epsilon-greedy strategy
bandit = simulate_bandit(
    n_arms=n_arms,
    true_rewards=true_rewards,
    n_iterations=1000,
    strategy='epsilon_greedy',
    epsilon=0.1
)

# Get statistics
stats = bandit.get_statistics()
print(f"Best arm: {stats['best_arm']}")
print(f"Estimated values: {stats['values']}")
```

### Running the Demo

```bash
python multibandit.py
```

## Strategies

### Epsilon-Greedy
Explores randomly with probability ε, exploits the best known arm otherwise.

```python
arm = bandit.select_arm_epsilon_greedy(epsilon=0.1)
```

### UCB (Upper Confidence Bound)
Balances exploration and exploitation by considering both estimated value and uncertainty.

```python
arm = bandit.select_arm_ucb(t=current_timestep, c=2.0)
```

### Thompson Sampling
Uses Bayesian inference to select arms based on probability of being optimal.

```python
arm = bandit.select_arm_thompson_sampling(alpha=1.0, beta=1.0)
```

## License

This project is open source and available for use.