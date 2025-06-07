import json
import numpy as np
import sys

def load_and_prepare_data(file_path="public_cases.json"):
    """
    Loads data from public_cases.json and prepares it for scikit-learn models.

    Returns:
        tuple: (features, target)
               features (np.array): An array of shape (n_samples, n_features)
                                    where features are [duration, miles, receipts].
               target (np.array): An array of shape (n_samples,) for reimbursement.
    """
    try:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"CRITICAL ERROR: {file_path} not found. Model training cannot proceed.", file=sys.stderr)
        return np.array([]), np.array([])
    except json.JSONDecodeError:
        print(f"CRITICAL ERROR: Could not decode JSON from {file_path}. Model training cannot proceed.", file=sys.stderr)
        return np.array([]), np.array([])

    features_list = []
    target_list = []

    for item in raw_data:
        try:
            miles = float(item['input']['miles_traveled'])
            duration = int(item['input']['trip_duration_days'])
            receipts = float(item['input']['total_receipts_amount'])

            features_list.append([duration, miles, receipts])
            target_list.append(float(item['expected_output']))
        except KeyError as e:
            print(f"Warning: Missing key {e} in an item: {item}", file=sys.stderr)
            continue
        except ValueError as e:
            print(f"Warning: Value error for item {item}: {e}", file=sys.stderr)
            continue

    if not features_list:
        print("CRITICAL ERROR: No valid data extracted from JSON (features_list is empty).", file=sys.stderr)
        return np.array([]), np.array([])

    return np.array(features_list), np.array(target_list)

if __name__ == '__main__':
    print("Directly testing data_prep_module.py (this message is from __main__ block)...")
    X_data_test, y_data_test = load_and_prepare_data()
    if X_data_test.size > 0 and y_data_test.size > 0:
        print(f"Successfully loaded {X_data_test.shape[0]} samples from public_cases.json.")
        print(f"Features array shape: {X_data_test.shape}")
        print(f"Target array shape: {y_data_test.shape}")
    else:
        print("Data loading or preparation failed during direct test of data_prep_module.py.")
