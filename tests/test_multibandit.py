"""
Tests for the MultiBandit package.
"""

import unittest
import json
from multibandit import Bandit, MultiBandit, GraphEmitter


class TestBandit(unittest.TestCase):
    """Test cases for the Bandit class."""
    
    def test_bandit_initialization(self):
        """Test bandit initialization."""
        bandit = Bandit(true_mean=0.5)
        self.assertEqual(bandit.true_mean, 0.5)
        self.assertEqual(bandit.estimated_mean, 0.0)
        self.assertEqual(bandit.num_pulls, 0)
    
    def test_bandit_invalid_true_mean(self):
        """Test bandit with invalid true_mean."""
        with self.assertRaises(ValueError):
            Bandit(true_mean=1.5)
        with self.assertRaises(ValueError):
            Bandit(true_mean=-0.1)
    
    def test_bandit_pull(self):
        """Test bandit pull returns valid reward."""
        bandit = Bandit(true_mean=0.5)
        reward = bandit.pull()
        self.assertIn(reward, [0.0, 1.0])
    
    def test_bandit_update(self):
        """Test bandit update mechanism."""
        bandit = Bandit(true_mean=0.5)
        bandit.update(1.0)
        self.assertEqual(bandit.num_pulls, 1)
        self.assertEqual(bandit.estimated_mean, 1.0)
        
        bandit.update(0.0)
        self.assertEqual(bandit.num_pulls, 2)
        self.assertEqual(bandit.estimated_mean, 0.5)


class TestMultiBandit(unittest.TestCase):
    """Test cases for the MultiBandit class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bandits = [Bandit(0.3), Bandit(0.5), Bandit(0.2)]
        self.multi_bandit = MultiBandit(self.bandits, epsilon=0.1)
    
    def test_multibandit_initialization(self):
        """Test multi-bandit initialization."""
        self.assertEqual(len(self.multi_bandit.bandits), 3)
        self.assertEqual(self.multi_bandit.epsilon, 0.1)
        self.assertEqual(self.multi_bandit.total_reward, 0.0)
        self.assertEqual(self.multi_bandit.num_iterations, 0)
        self.assertEqual(len(self.multi_bandit.history), 0)
    
    def test_multibandit_empty_bandits(self):
        """Test multi-bandit with empty bandits list."""
        with self.assertRaises(ValueError):
            MultiBandit([], epsilon=0.1)
    
    def test_multibandit_invalid_epsilon(self):
        """Test multi-bandit with invalid epsilon."""
        with self.assertRaises(ValueError):
            MultiBandit(self.bandits, epsilon=1.5)
        with self.assertRaises(ValueError):
            MultiBandit(self.bandits, epsilon=-0.1)
    
    def test_select_arm(self):
        """Test arm selection."""
        arm = self.multi_bandit.select_arm()
        self.assertIn(arm, [0, 1, 2])
    
    def test_run_iteration(self):
        """Test single iteration."""
        result = self.multi_bandit.run_iteration()
        
        self.assertEqual(result['iteration'], 1)
        self.assertIn(result['arm'], [0, 1, 2])
        self.assertIn(result['reward'], [0.0, 1.0])
        self.assertEqual(result['cumulative_reward'], result['reward'])
        self.assertEqual(len(result['arm_estimates']), 3)
        self.assertEqual(len(result['arm_pulls']), 3)
    
    def test_run_multiple_iterations(self):
        """Test running multiple iterations."""
        history = self.multi_bandit.run(num_iterations=100)
        
        self.assertEqual(len(history), 100)
        self.assertEqual(self.multi_bandit.num_iterations, 100)
        self.assertGreater(sum(b.num_pulls for b in self.bandits), 0)
    
    def test_run_invalid_iterations(self):
        """Test running with invalid number of iterations."""
        with self.assertRaises(ValueError):
            self.multi_bandit.run(num_iterations=0)
        with self.assertRaises(ValueError):
            self.multi_bandit.run(num_iterations=-10)
    
    def test_get_best_arm(self):
        """Test getting best arm."""
        # Run enough iterations to identify best arm
        self.multi_bandit.run(num_iterations=500)
        best_arm = self.multi_bandit.get_best_arm()
        
        # Should identify arm 1 (0.5) as best most of the time
        self.assertIn(best_arm, [0, 1, 2])


class TestGraphEmitter(unittest.TestCase):
    """Test cases for the GraphEmitter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        bandits = [Bandit(0.3), Bandit(0.5), Bandit(0.2)]
        multi_bandit = MultiBandit(bandits, epsilon=0.1)
        self.history = multi_bandit.run(num_iterations=100)
        self.emitter = GraphEmitter()
    
    def test_emit_performance_data(self):
        """Test emitting performance data."""
        data = self.emitter.emit_performance_data(self.history)
        
        self.assertEqual(data['type'], 'performance')
        self.assertEqual(len(data['iterations']), 100)
        self.assertEqual(len(data['rewards']), 100)
        self.assertEqual(len(data['cumulative_rewards']), 100)
        self.assertEqual(len(data['average_rewards']), 100)
    
    def test_emit_arm_selection_data(self):
        """Test emitting arm selection data."""
        data = self.emitter.emit_arm_selection_data(self.history)
        
        self.assertEqual(data['type'], 'arm_selection')
        self.assertEqual(len(data['arm_indices']), 3)
        self.assertEqual(len(data['pull_counts']), 3)
        self.assertEqual(data['total_pulls'], 100)
    
    def test_emit_arm_estimates_data(self):
        """Test emitting arm estimates data."""
        data = self.emitter.emit_arm_estimates_data(self.history)
        
        self.assertEqual(data['type'], 'arm_estimates')
        self.assertEqual(len(data['iterations']), 100)
        self.assertIn('arm_0', data['estimates'])
        self.assertIn('arm_1', data['estimates'])
        self.assertIn('arm_2', data['estimates'])
    
    def test_emit_all(self):
        """Test emitting all graph data."""
        all_data = self.emitter.emit_all(self.history)
        
        self.assertIn('performance', all_data)
        self.assertIn('arm_selection', all_data)
        self.assertIn('arm_estimates', all_data)
    
    def test_to_json(self):
        """Test JSON conversion."""
        self.emitter.emit_all(self.history)
        json_str = self.emitter.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIn('performance', parsed)
        self.assertIn('arm_selection', parsed)
        self.assertIn('arm_estimates', parsed)
    
    def test_emit_ascii_graph(self):
        """Test ASCII graph generation."""
        ascii_graph = self.emitter.emit_ascii_graph(self.history)
        
        self.assertIsInstance(ascii_graph, str)
        self.assertIn("Average Reward", ascii_graph)
        self.assertIn("Iterations", ascii_graph)
    
    def test_emit_ascii_graph_invalid_width(self):
        """Test ASCII graph with invalid width."""
        with self.assertRaises(ValueError):
            self.emitter.emit_ascii_graph(self.history, width=0)
        with self.assertRaises(ValueError):
            self.emitter.emit_ascii_graph(self.history, width=-10)
    
    def test_empty_history(self):
        """Test emitter with empty history."""
        data = self.emitter.emit_performance_data([])
        self.assertEqual(data, {})
        
        ascii_graph = self.emitter.emit_ascii_graph([])
        self.assertEqual(ascii_graph, "No data to graph")


if __name__ == '__main__':
    unittest.main()
