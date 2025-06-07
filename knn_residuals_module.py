import numpy as np
from sklearn.neighbors import KNeighborsRegressor
import data_prep_module # For testing block
import linear_regression_module # For testing block
import sys

def train_knn_on_residuals(X_train, residuals_train, n_neighbors=5):
    """Trains a KNeighborsRegressor model on the given features and residuals."""
    if X_train.size == 0 or residuals_train.size == 0:
        print("Error: Training data or residuals are empty. Cannot train kNN model.", file=sys.stderr)
        return None
    if X_train.shape[0] != residuals_train.shape[0]:
        print("Error: Mismatch in number of samples between X_train and residuals_train.", file=sys.stderr)
        return None

    knn_model = KNeighborsRegressor(n_neighbors=n_neighbors)
    try:
        # Ensure residuals_train is 1D array
        if residuals_train.ndim > 1 and residuals_train.shape[1] == 1:
             residuals_train = residuals_train.ravel()
        elif residuals_train.ndim > 1:
             print(f"Error: residuals_train has unexpected shape {residuals_train.shape}", file=sys.stderr)
             return None

        knn_model.fit(X_train, residuals_train)
        # print(f"kNN model trained with n_neighbors={n_neighbors}.", file=sys.stderr)
        return knn_model
    except Exception as e:
        print(f"Error during kNN model training: {e}", file=sys.stderr)
        return None

def predict_residual_knn(model, X_input):
    """Predicts a residual using the trained kNN model."""
    if model is None:
        print("Error: kNN model is None. Cannot predict residual.", file=sys.stderr)
        # Return a default residual, e.g., 0.0, or handle upstream
        return np.array([0.0]) # Default for a single prediction failure

    try:
        # Ensure X_input is 2D for scikit-learn prediction
        if X_input.ndim == 1:
            X_input_reshaped = X_input.reshape(1, -1)
        else:
            X_input_reshaped = X_input
        return model.predict(X_input_reshaped)
    except Exception as e:
        print(f"Error during kNN residual prediction: {e}", file=sys.stderr)
        return np.array([0.0])

if __name__ == '__main__':
    print("Directly testing knn_residuals_module.py...")
    X_all, y_all = data_prep_module.load_and_prepare_data()

    if X_all.size > 0 and y_all.size > 0:
        print(f"Data loaded: {X_all.shape[0]} samples.")
        lr_model, residuals = linear_regression_module.train_linear_regression_and_get_residuals(X_all, y_all)

        if lr_model is not None and residuals.size > 0:
            # Use a small k for testing if dataset is small, else default (5)
            k_val = min(5, X_all.shape[0]) # Ensure k is not more than number of samples
            if k_val == 0: k_val = 1 # k must be at least 1
            print(f"Training kNN on residuals with k={k_val}...")
            knn_r_model = train_knn_on_residuals(X_all, residuals, n_neighbors=k_val)

            if knn_r_model is not None:
                print("kNN on residuals model trained.")
                if X_all.shape[0] > 0:
                    first_sample_features = X_all[0]
                    # print(f"Predicting residual for first sample features: {first_sample_features}")
                    predicted_residual = predict_residual_knn(knn_r_model, first_sample_features)
                    print(f"Predicted residual for first sample: {predicted_residual[0]}")
                    print(f"Actual residual for first sample (from LR training): {residuals[0]}")
            else:
                print("Failed to train kNN on residuals model in test.")
        else:
            print("Failed to train Linear Regression or get residuals, cannot test kNN module.")
    else:
        print("Data loading failed, cannot test kNN module.")
