# MultiBandit

A multi-armed bandit algorithm implementation with graph emitter for visualization and analysis.

## Overview

MultiBandit is a Python library that implements the classic multi-armed bandit problem using an epsilon-greedy strategy. It includes a powerful graph emitter component that can generate visualization data in various formats, including JSON and ASCII graphs.

## Features

- **Multi-Armed Bandit Algorithm**: Epsilon-greedy strategy for balancing exploration and exploitation
- **Graph Emitter**: Generate graph data for visualization
  - Performance metrics over time
  - Arm selection distribution
  - Arm estimate convergence
  - JSON export for external visualization tools
  - Built-in ASCII graph visualization
- **Comprehensive Testing**: Full test suite included
- **Zero Dependencies**: Uses only Python standard library

## Installation

```bash
# Clone the repository
git clone https://github.com/Shinp2/MultiBandit.git
cd MultiBandit

# Install the package
pip install -e .
```

## Quick Start

```python
from multibandit import Bandit, MultiBandit, GraphEmitter

# Create bandits with different reward probabilities
bandits = [
    Bandit(true_mean=0.3),
    Bandit(true_mean=0.5),  # Best arm
    Bandit(true_mean=0.2),
    Bandit(true_mean=0.4)
]

# Create multi-armed bandit with epsilon-greedy strategy
multi_bandit = MultiBandit(bandits, epsilon=0.1)

# Run the experiment
history = multi_bandit.run(num_iterations=1000)

# Create graph emitter and generate visualizations
emitter = GraphEmitter()
graph_data = emitter.emit_all(history)

# Save results to JSON
emitter.save_json('results.json')

# Display ASCII graph
print(emitter.emit_ascii_graph(history))

# Get the best arm
best_arm = multi_bandit.get_best_arm()
print(f"Best arm identified: {best_arm}")
```

## Usage

### Running the Example

```bash
python example.py
```

This will run a complete experiment demonstrating:
- Multi-armed bandit with 4 arms
- 1000 iterations of the epsilon-greedy algorithm
- Performance metrics and statistics
- ASCII graph visualization
- Arm selection distribution
- JSON export of results

### Running Tests

```bash
python -m pytest tests/
# Or using unittest
python -m unittest discover tests/
```

## How It Works

### Multi-Armed Bandit

The multi-armed bandit problem is a classic reinforcement learning scenario where an agent must choose between multiple options (arms) with unknown reward distributions. The goal is to maximize total reward over time by balancing:

- **Exploration**: Trying different arms to learn their true rewards
- **Exploitation**: Choosing the arm with the highest estimated reward

Our implementation uses the **epsilon-greedy** strategy:
- With probability ε (epsilon), select a random arm (explore)
- With probability 1-ε, select the arm with highest estimated mean (exploit)

### Graph Emitter

The `GraphEmitter` class processes the experiment history and generates various graph data:

1. **Performance Data**: Tracks rewards and cumulative performance over iterations
2. **Arm Selection Data**: Shows how often each arm was selected
3. **Arm Estimates Data**: Tracks the convergence of estimated means for each arm

All data can be exported as JSON for use with visualization libraries like matplotlib, plotly, or D3.js.

## API Reference

### Bandit

```python
Bandit(true_mean: float)
```

Represents a single bandit arm.

- `pull()`: Pull the arm and receive a reward
- `update(reward)`: Update the estimated mean based on observed reward

### MultiBandit

```python
MultiBandit(bandits: List[Bandit], epsilon: float = 0.1)
```

Multi-armed bandit using epsilon-greedy strategy.

- `run(num_iterations)`: Run the algorithm for specified iterations
- `run_iteration()`: Run a single iteration
- `select_arm()`: Select an arm using epsilon-greedy strategy
- `get_best_arm()`: Get the index of the best arm based on current estimates

### GraphEmitter

```python
GraphEmitter()
```

Emits graph data from MultiBandit results.

- `emit_performance_data(history)`: Generate performance graph data
- `emit_arm_selection_data(history)`: Generate arm selection frequency data
- `emit_arm_estimates_data(history)`: Generate arm estimate evolution data
- `emit_all(history)`: Generate all graph data types
- `to_json(indent)`: Convert graph data to JSON string
- `save_json(filename, indent)`: Save graph data to JSON file
- `emit_ascii_graph(history, width)`: Generate ASCII graph visualization

## Example Output

```
==============================================================
MultiBandit Algorithm with Graph Emitter
==============================================================

Running experiment with 4 arms
True means: [0.3, 0.5, 0.2, 0.4]
Best arm: Arm 1 (0.5 success rate)
Strategy: Epsilon-greedy (epsilon=0.1)

Running 1000 iterations...

Results:
--------------------------------------------------------------
Total reward: 467.00
Average reward: 0.467

Best arm identified: Arm 1

Arm Statistics:
  Arm 0: pulls= 105, estimated_mean=0.295, true_mean=0.300
  Arm 1: pulls= 803, estimated_mean=0.503, true_mean=0.500
  Arm 2: pulls=  39, estimated_mean=0.205, true_mean=0.200
  Arm 3: pulls=  53, estimated_mean=0.396, true_mean=0.400
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.