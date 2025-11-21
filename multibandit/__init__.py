"""
MultiBandit: A multi-armed bandit algorithm implementation with graph emitter.
"""

from .bandit import Bandit, MultiBandit
from .graph_emitter import GraphEmitter

__version__ = "0.1.0"
__all__ = ["Bandit", "MultiBandit", "GraphEmitter"]
