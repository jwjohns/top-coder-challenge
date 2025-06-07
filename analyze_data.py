import json
import pandas as pd

# Load the JSON data
try:
    with open("public_cases.json", 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: public_cases.json not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Could not decode JSON from public_cases.json.")
    exit(1)

# Extract inputs and outputs into a list of dictionaries for easier DataFrame creation
processed_data = []
for item in data:
    record = {
        'duration': item['input']['trip_duration_days'],
        'miles': float(item['input']['miles_traveled']), # Ensure miles are float
        'receipts': item['input']['total_receipts_amount'],
        'reimbursement': item['expected_output']
    }
    processed_data.append(record)

df = pd.DataFrame(processed_data)

print("\n--- Descriptive Statistics ---")
print(df.describe())

print("\n--- Median Values ---")
print(df.median())

print("\n--- Correlation Matrix ---")
print(df.corr())

# Analyze per diem roughly - reimbursement / duration
# This is a very rough estimate and doesn't account for other factors
df['reimbursement_per_day'] = df['reimbursement'] / df['duration']
print("\n--- Reimbursement Per Day (Rough Estimate) ---")
print(df['reimbursement_per_day'].describe())
# Filter out cases where duration might be zero or cause issues, or where RPD is abnormally high
# df_filtered_rpd = df[df['duration'] > 0]
# df_filtered_rpd['reimbursement_per_day'] = df_filtered_rpd['reimbursement'] / df_filtered_rpd['duration']
# print(df_filtered_rpd['reimbursement_per_day'].describe())


# Analyze mileage rate roughly - (reimbursement - receipts) / miles
# This is also very rough and makes many assumptions
# To avoid division by zero or skewed results, filter out zero miles and low/high receipt cases
# df_filtered_miles = df[(df['miles'] > 0) & (df['receipts'] < df['reimbursement'])]
# df_filtered_miles['mileage_rate_estimate'] = (df_filtered_miles['reimbursement'] - df_filtered_miles['receipts']) / df_filtered_miles['miles']
# print("\n--- Mileage Rate Estimate (Very Rough) ---")
# print(df_filtered_miles['mileage_rate_estimate'].describe())

print("\n--- Analysis of cases with 5-day duration (mentioned in interviews) ---")
five_day_trips = df[df['duration'] == 5]
print(f"Number of 5-day trips: {len(five_day_trips)}")
if not five_day_trips.empty:
    print(five_day_trips.describe())
    # Compare average reimbursement per day for 5-day trips vs all trips
    avg_rpd_5_day = (five_day_trips['reimbursement'] / five_day_trips['duration']).mean()
    avg_rpd_all = (df[df['duration'] > 0]['reimbursement'] / df[df['duration'] > 0]['duration']).mean()
    print(f"Avg. Reimbursement Per Day (5-day trips): {avg_rpd_5_day}")
    print(f"Avg. Reimbursement Per Day (All trips with duration > 0): {avg_rpd_all}")

print("\n--- Analysis of cases with very low receipt amounts (mentioned in interviews) ---")
# Example: receipts < $10
low_receipt_trips = df[df['receipts'] < 10]
print(f"Number of trips with receipts < $10: {len(low_receipt_trips)}")
if not low_receipt_trips.empty:
    print(low_receipt_trips.describe())
    # Compare reimbursement vs (duration * 100) for these low receipt trips
    # This is a crude check for the $100/day per diem idea
    low_receipt_trips['base_per_diem_estimate'] = low_receipt_trips['duration'] * 100
    print(low_receipt_trips[['duration', 'receipts', 'reimbursement', 'base_per_diem_estimate']].head())

print("\n--- Analysis of receipt amounts ending in .49 or .99 (cents bug mentioned) ---")
receipts_ending_49_or_99 = df[df['receipts'].apply(lambda x: round(x * 100) % 100 == 49 or round(x * 100) % 100 == 99)]
print(f"Number of trips with receipts ending in .49 or .99: {len(receipts_ending_49_or_99)}")
if not receipts_ending_49_or_99.empty:
    # It's hard to quantify the "bonus" without a baseline model,
    # but we can look at their general stats
    print(receipts_ending_49_or_99.describe())


print("\nScript finished.")
