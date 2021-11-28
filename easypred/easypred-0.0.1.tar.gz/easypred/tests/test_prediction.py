from unittest import TestCase

import numpy as np
import pandas as pd
from easypred import BinaryPrediction, Prediction


class TestPrediction(TestCase):
    """Check the correct functioning of the prediction class."""

    l1 = [1, 2, 3]
    l2 = [1, 2, 3]
    l3 = [1, 2, 4]
    l4 = [1, 2, 4, 5]
    l5 = ["a", "b"]
    pred_l1l2 = Prediction(l2, l1)
    pred_l1l3 = Prediction(l3, l1)

    s1 = pd.Series(l1)
    s2 = pd.Series(l2)
    s3 = pd.Series(l3)
    s4 = pd.Series(l4)
    pred_s1s2 = Prediction(s2, s1)
    pred_s1s3 = Prediction(s3, s1)

    a1 = np.array(l1)
    a2 = np.array(l2)
    a3 = np.array(l3)
    a4 = np.array(l4)
    pred_a1a2 = Prediction(a2, a1)
    pred_a1a3 = Prediction(a3, a1)

    def test_input_check(self):
        """Check that initiation happens correctly"""
        # Check exception if length mismatch
        self.assertRaises(ValueError, Prediction, self.l4, self.l1)
        self.assertRaises(ValueError, Prediction, self.s4, self.s1)
        self.assertRaises(ValueError, Prediction, self.a4, self.a1)

        # Check no exception if no length mismatch
        for fit, real in zip([self.l1, self.s1, self.a1], [self.l2, self.s2, self.a2]):
            try:
                Prediction(fit, real)
            except Exception as e:
                self.fail(f"Prediction(fit, real) raised {e} unexpectedly!")

        # Check that list is transformed to np.array
        np.testing.assert_array_equal(self.pred_l1l2.fitted_values, self.a1)
        np.testing.assert_array_equal(self.pred_l1l2.real_values, self.a2)

        # Check that being numeric is correctly detected
        self.assertTrue(self.pred_l1l2.is_numeric)
        self.assertTrue(self.pred_s1s2.is_numeric)
        self.assertTrue(Prediction([0.1, 0.2], [0.1, 0.2]).is_numeric)

        self.assertFalse(Prediction(np.array(self.l5), np.array(self.l5)).is_numeric)

    def test_is_correct(self):
        """Test if correctness check happens in the right way."""
        res1 = np.array([True, True, True])
        np.testing.assert_array_equal(self.pred_l1l2.matches(), res1)
        np.testing.assert_array_equal(self.pred_a1a2.matches(), res1)
        pd.testing.assert_series_equal(self.pred_s1s2.matches(), pd.Series(res1))

        res2 = np.array([True, True, False])
        np.testing.assert_array_equal(self.pred_l1l3.matches(), res2)
        np.testing.assert_array_equal(self.pred_a1a3.matches(), res2)
        pd.testing.assert_series_equal(self.pred_s1s3.matches(), pd.Series(res2))

    def test_accuracy(self):
        """Test if accuracy is computed correctly."""
        self.assertEqual(self.pred_l1l2.percentage_correctly_classified, 1)
        self.assertEqual(self.pred_a1a2.percentage_correctly_classified, 1)
        self.assertEqual(self.pred_s1s2.percentage_correctly_classified, 1)

        self.assertEqual(self.pred_l1l3.percentage_correctly_classified, 2 / 3)
        self.assertEqual(self.pred_a1a3.percentage_correctly_classified, 2 / 3)
        self.assertEqual(self.pred_s1s3.percentage_correctly_classified, 2 / 3)

        # Test alias
        self.assertEqual(self.pred_l1l3.pcc, 2 / 3)
        self.assertEqual(self.pred_a1a3.pcc, 2 / 3)
        self.assertEqual(self.pred_s1s3.pcc, 2 / 3)

    def test_makebinary(self):
        """Test if binary prediction is created correctly."""
        p1 = Prediction([0, 0, 1], [1, 0, 0])
        p1 = p1.to_binary(value_positive=1)
        self.assertIsInstance(p1, BinaryPrediction)
        self.assertEqual(p1.value_positive, 1)

    def test_dataframe(self):
        """Test if dataframe is created correctly."""
        p1 = Prediction([0, 0, 1], [1, 0, 0])
        exp = pd.DataFrame(
            {
                "Real Values": [0, 0, 1],
                "Fitted Values": [1, 0, 0],
                "Prediction Matches": [False, True, False],
            }
        )
        pd.testing.assert_frame_equal(p1.as_dataframe(), exp, check_dtype=False)

    def test_describe(self):
        """Test if description info is returned correctly."""
        exp = pd.DataFrame(
            {"N": [3], "Matches": [3], "Errors": [0], "PCC": [1]}, index=["Value"]
        ).transpose()
        pd.testing.assert_frame_equal(self.pred_l1l2.describe(), exp, check_dtype=False)
