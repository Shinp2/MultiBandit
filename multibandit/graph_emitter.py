"""
Graph emitter for visualizing multi-armed bandit performance.
"""

from typing import List, Dict, Optional
import json


class GraphEmitter:
    """
    Emits graph data from MultiBandit results for visualization.
    """
    
    def __init__(self):
        """Initialize the graph emitter."""
        self.data = {}
        
    def emit_performance_data(self, history: List[dict]) -> dict:
        """
        Emit performance data suitable for graphing.
        
        Args:
            history: List of iteration results from MultiBandit
            
        Returns:
            Dictionary with graph data
        """
        if not history:
            return {}
        
        iterations = [h['iteration'] for h in history]
        rewards = [h['reward'] for h in history]
        cumulative_rewards = [h['cumulative_reward'] for h in history]
        avg_rewards = [h['avg_reward'] for h in history]
        
        graph_data = {
            'type': 'performance',
            'iterations': iterations,
            'rewards': rewards,
            'cumulative_rewards': cumulative_rewards,
            'average_rewards': avg_rewards
        }
        
        self.data['performance'] = graph_data
        return graph_data
    
    def emit_arm_selection_data(self, history: List[dict]) -> dict:
        """
        Emit arm selection frequency data.
        
        Args:
            history: List of iteration results from MultiBandit
            
        Returns:
            Dictionary with arm selection graph data
        """
        if not history:
            return {}
        
        # Get the final arm pulls count
        final_state = history[-1]
        arm_pulls = final_state['arm_pulls']
        
        graph_data = {
            'type': 'arm_selection',
            'arm_indices': list(range(len(arm_pulls))),
            'pull_counts': arm_pulls,
            'total_pulls': sum(arm_pulls)
        }
        
        self.data['arm_selection'] = graph_data
        return graph_data
    
    def emit_arm_estimates_data(self, history: List[dict]) -> dict:
        """
        Emit arm estimate evolution data.
        
        Args:
            history: List of iteration results from MultiBandit
            
        Returns:
            Dictionary with arm estimates graph data
        """
        if not history:
            return {}
        
        num_arms = len(history[0]['arm_estimates'])
        iterations = [h['iteration'] for h in history]
        
        # Transpose the estimates for each arm
        arm_estimates = {
            f'arm_{i}': [h['arm_estimates'][i] for h in history]
            for i in range(num_arms)
        }
        
        graph_data = {
            'type': 'arm_estimates',
            'iterations': iterations,
            'estimates': arm_estimates
        }
        
        self.data['arm_estimates'] = graph_data
        return graph_data
    
    def emit_all(self, history: List[dict]) -> dict:
        """
        Emit all graph data types.
        
        Args:
            history: List of iteration results from MultiBandit
            
        Returns:
            Dictionary with all graph data
        """
        self.emit_performance_data(history)
        self.emit_arm_selection_data(history)
        self.emit_arm_estimates_data(history)
        
        return self.data
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert graph data to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.data, indent=indent)
    
    def save_json(self, filename: str, indent: Optional[int] = 2):
        """
        Save graph data to a JSON file.
        
        Args:
            filename: Output filename
            indent: JSON indentation level
        """
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=indent)
    
    def emit_ascii_graph(self, history: List[dict], width: int = 60) -> str:
        """
        Emit a simple ASCII graph of average rewards over time.
        
        Args:
            history: List of iteration results from MultiBandit
            width: Width of the graph in characters
            
        Returns:
            ASCII graph string
        """
        if not history:
            return "No data to graph"
        
        avg_rewards = [h['avg_reward'] for h in history]
        iterations = [h['iteration'] for h in history]
        
        # Sample points if there are too many
        step = max(1, len(avg_rewards) // width)
        sampled_rewards = avg_rewards[::step]
        sampled_iterations = iterations[::step]
        
        # Normalize to graph height
        height = 20
        max_reward = max(sampled_rewards) if sampled_rewards else 1.0
        min_reward = min(sampled_rewards) if sampled_rewards else 0.0
        reward_range = max_reward - min_reward or 1.0
        
        # Build graph
        lines = []
        lines.append(f"Average Reward Over Time (max: {max_reward:.3f})")
        lines.append("=" * (width + 10))
        
        for i in range(height, -1, -1):
            threshold = min_reward + (reward_range * i / height)
            line = f"{threshold:5.2f} |"
            
            for reward in sampled_rewards:
                if reward >= threshold:
                    line += "█"
                else:
                    line += " "
            
            lines.append(line)
        
        lines.append("      +" + "-" * len(sampled_rewards))
        lines.append(f"      Iterations: 1 to {iterations[-1]}")
        
        return "\n".join(lines)
