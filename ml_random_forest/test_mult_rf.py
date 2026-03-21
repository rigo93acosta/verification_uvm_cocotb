"""
Cocotb testbench for 8-bit Multiplier using Random Forest ML verification
This test demonstrates ML-based verification using scikit-learn's RandomForestRegressor
"""

import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import random
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


class RandomForestVerifier:
    """Random Forest based verification agent for the multiplier"""
    
    def __init__(self, n_estimators=200, max_depth=None, use_neural_net=False):
        """
        Initialize the Random Forest verifier
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of each tree (None = unlimited)
            use_neural_net: If True, use Neural Network instead of Random Forest
        """
        self.use_neural_net = use_neural_net
        
        if use_neural_net:
            # Neural Network - better for deterministic functions
            self.model = MLPRegressor(
                hidden_layer_sizes=(256, 128, 64),  # Deeper network
                activation='relu',
                solver='adam',
                alpha=0.0001,  # L2 regularization
                batch_size='auto',
                learning_rate='adaptive',
                learning_rate_init=0.001,
                max_iter=1000,  # More iterations
                random_state=42,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=50,
                verbose=False
            )
            self.model_name = "Neural Network"
        else:
            # Random Forest with improved settings
            self.model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            )
            self.model_name = "Random Forest"
        
        self.training_data = []
        self.training_labels = []
        self.is_trained = False
        
    def _engineer_features(self, a, b):
        """Create engineered features to help model learn multiplication"""
        # Original features
        features = [a, b]
        
        # Add polynomial features that capture multiplication patterns
        features.extend([
            a * a,           # a²
            b * b,           # b²
            a + b,           # sum
            abs(a - b),      # difference
            min(a, b),       # minimum
            max(a, b),       # maximum
            (a >> 4),        # high bits of a
            (b >> 4),        # high bits of b
            (a & 0x0F),      # low bits of a
            (b & 0x0F),      # low bits of b
        ])
        
        return features
        
    def collect_training_data(self, a, b, product):
        """Collect data for training the model"""
        # Use engineered features
        features = self._engineer_features(a, b)
        self.training_data.append(features)
        self.training_labels.append(product)
        
    def train(self):
        """Train the Random Forest model"""
        if len(self.training_data) < 10:
            raise ValueError("Need at least 10 samples to train")
            
        X = np.array(self.training_data)
        y = np.array(self.training_labels)
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train the model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mse': mse,
            'r2_score': r2,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
    def predict(self, a, b):
        """Predict the expected product using the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        # Use engineered features for prediction
        features = self._engineer_features(a, b)
        X = np.array([features])
        prediction = self.model.predict(X)
        return int(round(prediction[0]))
        
    def get_feature_importance(self):
        """Get feature importance from the Random Forest"""
        if not self.is_trained or self.use_neural_net:
            return None
        
        feature_names = ['a', 'b', 'a²', 'b²', 'a+b', '|a-b|', 'min', 'max', 'a_high', 'b_high', 'a_low', 'b_low']
        importance_dict = {}
        
        for i, name in enumerate(feature_names):
            if i < len(self.model.feature_importances_):
                importance_dict[name] = self.model.feature_importances_[i]
        
        # Return top 5 most important features
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_features[:5])


@cocotb.test()
async def test_mult_random_forest(dut):
    """Test the multiplier using Random Forest ML verification"""
    
    cocotb.log.info("=" * 80)
    cocotb.log.info("Starting Random Forest ML-based Multiplier Verification")
    cocotb.log.info("=" * 80)
    
    # Phase 1: Training Phase
    # Try Neural Network first (better for deterministic functions)
    use_nn = True  # Set to False to use Random Forest
    model_type = "Neural Network" if use_nn else "Random Forest"
    
    cocotb.log.info(f"\n[PHASE 1] Training the {model_type} Model")
    cocotb.log.info("-" * 80)
    
    verifier = RandomForestVerifier(n_estimators=200, max_depth=None, use_neural_net=use_nn)
    
    # Generate training data using known-good samples
    num_training_samples = 5000 if use_nn else 2000  # More samples for Neural Network
    training_errors = 0
    
    for i in range(num_training_samples):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        expected_product = a * b
        
        # Apply inputs to DUT
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit='ns')
        
        # Get DUT output
        dut_product = int(dut.product.value)
        
        # Verify DUT is working correctly during training
        if dut_product != expected_product:
            training_errors += 1
            cocotb.log.error(f"Training sample {i}: DUT error! {a} * {b} = {dut_product}, expected {expected_product}")
        
        # Collect training data
        verifier.collect_training_data(a, b, expected_product)
        
        if (i + 1) % 500 == 0:
            cocotb.log.info(f"Collected {i + 1}/{num_training_samples} training samples")
    
    cocotb.log.info(f"Training data collection complete: {num_training_samples} samples")
    cocotb.log.info(f"DUT errors during training: {training_errors}")
    
    # Train the model
    cocotb.log.info("\nTraining Random Forest model...")
    training_stats = verifier.train()
    
    cocotb.log.info(f"Model training complete!")
    cocotb.log.info(f"  - Training samples: {training_stats['train_samples']}")
    cocotb.log.info(f"  - Test samples: {training_stats['test_samples']}")
    cocotb.log.info(f"  - Mean Squared Error: {training_stats['mse']:.4f}")
    cocotb.log.info(f"  - R² Score: {training_stats['r2_score']:.4f}")
    
    # Feature importance (only for Random Forest)
    importance = verifier.get_feature_importance()
    if importance:
        cocotb.log.info(f"\nTop 5 Feature Importance:")
        for i, (feature, value) in enumerate(importance.items(), 1):
            cocotb.log.info(f"  {i}. {feature}: {value:.4f}")
    else:
        cocotb.log.info(f"\n(Neural Network - feature importance not applicable)")
    
    # Phase 2: ML-Driven Verification Phase
    cocotb.log.info("\n[PHASE 2] ML-Driven Verification")
    cocotb.log.info("-" * 80)
    
    num_test_samples = 500
    ml_predictions = []
    actual_products = []
    dut_outputs = []
    ml_errors = 0
    dut_errors = 0
    
    for i in range(num_test_samples):
        # Generate random test inputs
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        expected_product = a * b
        
        # ML prediction
        ml_prediction = verifier.predict(a, b)
        ml_predictions.append(ml_prediction)
        actual_products.append(expected_product)
        
        # DUT simulation
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit='ns')
        dut_product = int(dut.product.value)
        dut_outputs.append(dut_product)
        
        # Check ML prediction accuracy
        if ml_prediction != expected_product:
            ml_errors += 1
            if ml_errors <= 5:  # Only log first few errors
                cocotb.log.warning(f"ML prediction error at test {i}: {a} * {b} = {ml_prediction} (ML), expected {expected_product}")
        
        # Check DUT accuracy
        if dut_product != expected_product:
            dut_errors += 1
            cocotb.log.error(f"DUT error at test {i}: {a} * {b} = {dut_product}, expected {expected_product}")
        
        # Log progress
        if (i + 1) % 100 == 0:
            cocotb.log.info(f"Verified {i + 1}/{num_test_samples} test cases")
    
    # Phase 3: Results and Analysis
    cocotb.log.info("\n[PHASE 3] Verification Results")
    cocotb.log.info("=" * 80)
    
    ml_accuracy = (num_test_samples - ml_errors) / num_test_samples * 100
    dut_accuracy = (num_test_samples - dut_errors) / num_test_samples * 100
    
    cocotb.log.info(f"\nTest Summary:")
    cocotb.log.info(f"  - Total test cases: {num_test_samples}")
    cocotb.log.info(f"  - ML Prediction accuracy (exact): {ml_accuracy:.2f}% ({num_test_samples - ml_errors}/{num_test_samples})")
    cocotb.log.info(f"  - DUT accuracy: {dut_accuracy:.2f}% ({num_test_samples - dut_errors}/{num_test_samples})")
    
    # Calculate accuracy with tolerance (within 1% error)
    ml_predictions_np = np.array(ml_predictions)
    actual_products_np = np.array(actual_products)
    tolerance = 0.01  # 1% tolerance
    errors_within_tolerance = np.abs(ml_predictions_np - actual_products_np) <= (actual_products_np * tolerance + 1)
    accuracy_with_tolerance = np.sum(errors_within_tolerance) / num_test_samples * 100
    cocotb.log.info(f"  - ML accuracy (1% tolerance): {accuracy_with_tolerance:.2f}%")
    
    # Calculate ML prediction statistics
    ml_predictions = np.array(ml_predictions)
    actual_products = np.array(actual_products)
    ml_mse = mean_squared_error(actual_products, ml_predictions)
    ml_r2 = r2_score(actual_products, ml_predictions)
    
    cocotb.log.info(f"\nML Model Performance on Test Data:")
    cocotb.log.info(f"  - Mean Squared Error: {ml_mse:.4f}")
    cocotb.log.info(f"  - R² Score: {ml_r2:.4f}")
    
    # Generate visualization
    try:
        plt.figure(figsize=(12, 5))
        
        # Plot 1: ML Predictions vs Actual
        plt.subplot(1, 2, 1)
        plt.scatter(actual_products, ml_predictions, alpha=0.5)
        plt.plot([0, max(actual_products)], [0, max(actual_products)], 'r--', label='Perfect prediction')
        plt.xlabel('Actual Product')
        plt.ylabel('ML Predicted Product')
        plt.title(f'Random Forest Predictions\n(R² = {ml_r2:.4f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Prediction errors
        plt.subplot(1, 2, 2)
        errors = ml_predictions - actual_products
        plt.hist(errors, bins=30, edgecolor='black')
        plt.xlabel('Prediction Error')
        plt.ylabel('Frequency')
        plt.title('Distribution of ML Prediction Errors')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('rf_verification_results.png', dpi=150, bbox_inches='tight')
        cocotb.log.info("\n📊 Visualization saved to: rf_verification_results.png")
    except Exception as e:
        cocotb.log.warning(f"Could not generate visualization: {e}")
    
    # Final assertion
    cocotb.log.info("\n" + "=" * 80)
    if dut_errors == 0:
        cocotb.log.info("✓ VERIFICATION PASSED: DUT is functioning correctly!")
    else:
        cocotb.log.error("✗ VERIFICATION FAILED: DUT has errors!")
    
    if accuracy_with_tolerance >= 95.0:
        cocotb.log.info(f"\u2713 ML MODEL EXCELLENT: {accuracy_with_tolerance:.2f}% accuracy (1% tolerance)!")
    elif ml_r2 >= 0.99:
        cocotb.log.info(f"\u2713 ML MODEL GOOD: R\u00b2={ml_r2:.4f}, within-tolerance accuracy={accuracy_with_tolerance:.2f}%")
    else:
        cocotb.log.warning(f"\u26a0 ML MODEL NEEDS IMPROVEMENT: R\u00b2={ml_r2:.4f}")
    
    cocotb.log.info("=" * 80)
    
    # Assert final results
    assert dut_errors == 0, f"DUT has {dut_errors} errors out of {num_test_samples} tests"
    assert ml_r2 >= 0.99, f"ML model R\u00b2 score too low: {ml_r2:.4f} (need >= 0.99)"
    
    cocotb.log.info(f"\nNOTE: {verifier.model_name} achieved {ml_accuracy:.2f}% exact accuracy and {ml_r2:.4f} R² score.")
    if verifier.use_neural_net:
        cocotb.log.info(f"Neural Networks are excellent for learning deterministic functions like multiplication.")
    else:
        cocotb.log.info(f"Random Forest is an ensemble model - small rounding errors are expected.")


@cocotb.test()
async def test_edge_cases(dut):
    """Test edge cases with Random Forest verification"""
    
    cocotb.log.info("\n" + "=" * 80)
    cocotb.log.info("Testing Edge Cases")
    cocotb.log.info("=" * 80)
    
    edge_cases = [
        (0, 0, 0, "Zero * Zero"),
        (0, 255, 0, "Zero * Max"),
        (255, 0, 0, "Max * Zero"),
        (255, 255, 65025, "Max * Max"),
        (1, 1, 1, "One * One"),
        (128, 128, 16384, "Mid * Mid"),
        (255, 1, 255, "Max * One"),
        (1, 255, 255, "One * Max"),
    ]
    
    errors = 0
    for a, b, expected, description in edge_cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit='ns')
        
        result = int(dut.product.value)
        status = "✓" if result == expected else "✗"
        
        if result != expected:
            errors += 1
            cocotb.log.error(f"{status} {description}: {a} * {b} = {result}, expected {expected}")
        else:
            cocotb.log.info(f"{status} {description}: {a} * {b} = {result}")
    
    cocotb.log.info(f"\nEdge cases passed: {len(edge_cases) - errors}/{len(edge_cases)}")
    assert errors == 0, f"{errors} edge case(s) failed"


@cocotb.test()
async def test_exhaustive_small(dut):
    """Exhaustive test for small values (0-15)"""
    
    cocotb.log.info("\n" + "=" * 80)
    cocotb.log.info("Exhaustive Test (0-15 range)")
    cocotb.log.info("=" * 80)
    
    errors = 0
    total_tests = 0
    
    for a in range(16):
        for b in range(16):
            dut.a.value = a
            dut.b.value = b
            await Timer(1, unit='ns')
            
            expected = a * b
            result = int(dut.product.value)
            total_tests += 1
            
            if result != expected:
                errors += 1
                cocotb.log.error(f"Error: {a} * {b} = {result}, expected {expected}")
    
    cocotb.log.info(f"\nExhaustive test completed: {total_tests - errors}/{total_tests} passed")
    assert errors == 0, f"{errors} error(s) in exhaustive test"
