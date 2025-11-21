"""
Example usage of MultiBandit with GraphEmitter.
"""

from multibandit import Bandit, MultiBandit, GraphEmitter


def main():
    """Run a simple multi-armed bandit experiment."""
    
    # Create bandits with different true means
    # Arm 0: 30% success rate
    # Arm 1: 50% success rate (best arm)
    # Arm 2: 20% success rate
    # Arm 3: 40% success rate
    bandits = [
        Bandit(true_mean=0.3),
        Bandit(true_mean=0.5),
        Bandit(true_mean=0.2),
        Bandit(true_mean=0.4)
    ]
    
    # Create multi-armed bandit with epsilon-greedy strategy
    multi_bandit = MultiBandit(bandits, epsilon=0.1)
    
    print("=" * 60)
    print("MultiBandit Algorithm with Graph Emitter")
    print("=" * 60)
    print(f"\nRunning experiment with {len(bandits)} arms")
    print("True means: [0.3, 0.5, 0.2, 0.4]")
    print("Best arm: Arm 1 (0.5 success rate)")
    print("Strategy: Epsilon-greedy (epsilon=0.1)")
    print("\nRunning 1000 iterations...\n")
    
    # Run the experiment
    history = multi_bandit.run(num_iterations=1000)
    
    # Print results
    print("Results:")
    print("-" * 60)
    print(f"Total reward: {multi_bandit.total_reward:.2f}")
    print(f"Average reward: {multi_bandit.total_reward / multi_bandit.num_iterations:.3f}")
    print(f"\nBest arm identified: Arm {multi_bandit.get_best_arm()}")
    print("\nArm Statistics:")
    for i, bandit in enumerate(bandits):
        print(f"  Arm {i}: pulls={bandit.num_pulls:4d}, "
              f"estimated_mean={bandit.estimated_mean:.3f}, "
              f"true_mean={bandit.true_mean:.3f}")
    
    # Create graph emitter and generate visualizations
    print("\n" + "=" * 60)
    print("Graph Emitter Output")
    print("=" * 60)
    
    emitter = GraphEmitter()
    
    # Emit all graph data
    graph_data = emitter.emit_all(history)
    
    # Save to JSON file
    emitter.save_json('multibandit_results.json')
    print("\n✓ Graph data saved to: multibandit_results.json")
    
    # Display ASCII graph
    print("\n" + emitter.emit_ascii_graph(history))
    
    # Print arm selection summary
    arm_selection = graph_data['arm_selection']
    print("\n" + "=" * 60)
    print("Arm Selection Distribution")
    print("=" * 60)
    for i, pulls in enumerate(arm_selection['pull_counts']):
        percentage = (pulls / arm_selection['total_pulls']) * 100
        bar = "█" * int(percentage / 2)
        print(f"Arm {i}: {bar} {pulls:4d} pulls ({percentage:5.1f}%)")
    
    print("\n" + "=" * 60)
    print("Experiment Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
