import numpy as np
from sklearn.linear_model import LinearRegression
import data_prep_module # Assuming this is in the same directory
import sys

def train_linear_regression_and_get_residuals(X_train, y_train):
    """Trains a Linear Regression model and calculates residuals."""
    if X_train.size == 0 or y_train.size == 0:
        print("Error: Training data is empty. Cannot train Linear Regression.", file=sys.stderr)
        return None, np.array([]) # Return None for model, empty array for residuals

    lr_model = LinearRegression()
    try:
        lr_model.fit(X_train, y_train)
        predictions = lr_model.predict(X_train)
        residuals = y_train - predictions
        # print(f"Linear Regression model trained. Coefficients: {lr_model.coef_}, Intercept: {lr_model.intercept_}", file=sys.stderr)
        return lr_model, residuals
    except Exception as e:
        print(f"Error during Linear Regression training or prediction: {e}", file=sys.stderr)
        return None, np.array([])

def predict_linear_regression(model, X_input):
    """Makes predictions using the trained Linear Regression model."""
    if model is None:
        print("Error: Linear Regression model is None. Cannot make predictions.", file=sys.stderr)
        # Return a default or error-indicating value, e.g., an array of zeros or handle upstream
        # For this problem, if LR fails, the whole prediction might be compromised.
        # Let's return an empty array and let the calling code decide how to handle it.
        # Or, more simply, if X_input is (1, n_features), return array of shape (1,)
        if X_input.ndim == 2:
            return np.zeros(X_input.shape[0])
        else: # Should not happen if input is single sample correctly shaped
            return np.array([0.0]) # Default for a single prediction failure

    try:
        # Ensure X_input is 2D for scikit-learn prediction (even for a single sample)
        if X_input.ndim == 1:
            X_input_reshaped = X_input.reshape(1, -1)
        else:
            X_input_reshaped = X_input
        return model.predict(X_input_reshaped)
    except Exception as e:
        print(f"Error during Linear Regression prediction: {e}", file=sys.stderr)
        if X_input.ndim == 2:
            return np.zeros(X_input.shape[0])
        else:
            return np.array([0.0])

if __name__ == '__main__':
    print("Directly testing linear_regression_module.py...")
    # Load data using the existing data_prep_module
    X_all_data, y_all_data = data_prep_module.load_and_prepare_data()

    if X_all_data.size > 0 and y_all_data.size > 0:
        print(f"Data loaded: {X_all_data.shape[0]} samples.")
        lr_model_trained, train_residuals = train_linear_regression_and_get_residuals(X_all_data, y_all_data)

        if lr_model_trained is not None:
            print(f"Linear Regression model trained. Residuals count: {train_residuals.size}")
            if train_residuals.size > 0:
                print(f"First 5 residuals: {train_residuals[:5]}")

            # Test prediction on the first sample from the loaded data
            if X_all_data.shape[0] > 0:
                first_sample_features = X_all_data[0]
                # print(f"Predicting for first sample features: {first_sample_features}")
                prediction = predict_linear_regression(lr_model_trained, first_sample_features)
                print(f"Prediction for first sample: {prediction[0]}")
                print(f"Actual for first sample: {y_all_data[0]}")
                print(f"Calculated residual for first sample (manual): {y_all_data[0] - prediction[0]}")
                print(f"Stored residual for first sample (from training): {train_residuals[0]}")
        else:
            print("Failed to train Linear Regression model in test.")
    else:
        print("Data loading failed, cannot test Linear Regression module.")
