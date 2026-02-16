
import unittest
from src.optimization.fitness import calculate_fitness, SegmentMetrics
from src.optimization.param_space import get_default_param_space

class TestFitnessTrades(unittest.TestCase):
    def setUp(self):
        self.param_space = get_default_param_space()
        self.params = self.param_space.get_defaults()
        
        # Base metrics for SubTrain (not the focus, just need valid values)
        self.metrics_sub = SegmentMetrics(
            trades=20,
            return_pct=0.05,
            maxdd=0.10,
            sharpe=1.5,
            pf=2.0,
            gross_profit=1000,
            gross_loss=500
        )

    def test_fitness_hard_fail_under_10_trades(self):
        """
        Currently, this should return -inf.
        After fix, this should return a penalized but finite score.
        """
        metrics_val = SegmentMetrics(
            trades=5,  # < 10 implies penalty
            return_pct=0.10,
            maxdd=0.05,
            sharpe=2.0,
            pf=3.0,
            gross_profit=600,
            gross_loss=200
        )
        
        fitness = calculate_fitness(
            self.params,
            self.metrics_sub,
            metrics_val,
            self.param_space
        )
        
        # CURRENT BEHAVIOR: EXPECT -inf
        # Change this assertion to assertNotEqual(fitness, float('-inf')) after fix
        self.assertNotEqual(fitness, float('-inf'), "Should NOT return -inf for < 10 trades after fix")

    def test_fitness_zero_trades_is_inf(self):
        """
        Zero trades should ALWAYS be -inf.
        """
        metrics_val = SegmentMetrics(
            trades=0,
            return_pct=0.0,
            maxdd=0.0,
            sharpe=0.0,
            pf=0.0,
            gross_profit=0,
            gross_loss=0
        )
        
        fitness = calculate_fitness(
            self.params,
            self.metrics_sub,
            metrics_val,
            self.param_space
        )
        
        self.assertEqual(fitness, float('-inf'))

if __name__ == '__main__':
    unittest.main()
