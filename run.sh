#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>"
    exit 1
fi

TRIP_DURATION_DAYS=$1
MILES_TRAVELED=$2
TOTAL_RECEIPTS_AMOUNT=$3

# Call the Python script to perform the calculation
python3 - "$TRIP_DURATION_DAYS" "$MILES_TRAVELED" "$TOTAL_RECEIPTS_AMOUNT" <<PY_SCRIPT
import sys
import math

trip_duration_days = int(sys.argv[1])
miles_traveled = float(sys.argv[2])
total_receipts_amount = float(sys.argv[3])

reimbursement = 0.00

# 1. Per Diem Calculation
per_diem_rate = 100.0
actual_per_diem_days = trip_duration_days
if trip_duration_days > 10: # Cap per diem days for calculation
    actual_per_diem_days = 10
reimbursement += actual_per_diem_days * per_diem_rate

# 5-Day Trip Bonus
five_day_trip_bonus = 50.0
if trip_duration_days == 5:
    reimbursement += five_day_trip_bonus

# Efficiency Bonus/Penalty (Miles per Day)
if trip_duration_days > 0:
    miles_per_day = miles_traveled / trip_duration_days
    efficiency_adjustment = 0.0
    if 180 <= miles_per_day <= 220:
        efficiency_adjustment = 75.0 # Bonus
    elif miles_per_day < 100 and miles_per_day > 0: # Low efficiency
        efficiency_adjustment = -50.0 # Penalty
    elif miles_per_day > 300: # Too high
        efficiency_adjustment = -50.0 # Penalty
    reimbursement += efficiency_adjustment

# 2. Tiered Mileage Calculation
mileage_rate_tier1 = 0.58
miles_tier1_threshold = 100.0
mileage_rate_tier2 = 0.40 # For 101-500 miles
miles_tier2_threshold = 500.0
mileage_rate_tier3 = 0.30 # For miles > 500

if miles_traveled <= miles_tier1_threshold:
    reimbursement += miles_traveled * mileage_rate_tier1
elif miles_traveled <= miles_tier2_threshold:
    reimbursement += (miles_tier1_threshold * mileage_rate_tier1) + \
                     ((miles_traveled - miles_tier1_threshold) * mileage_rate_tier2)
else:
    reimbursement += (miles_tier1_threshold * mileage_rate_tier1) + \
                     ((miles_tier2_threshold - miles_tier1_threshold) * mileage_rate_tier2) + \
                     ((miles_traveled - miles_tier2_threshold) * mileage_rate_tier3)

# 3. Receipt Processing Logic with new multi-tier diminishing returns
apply_receipt_logic = True
if total_receipts_amount < 20 and trip_duration_days > 1: # Low receipt skip
    apply_receipt_logic = False

receipt_reimbursement = 0.0
if apply_receipt_logic:
    receipt_tier1_threshold = 700.0
    receipt_tier1_rate = 0.80

    receipt_tier2_threshold = 1500.0
    receipt_tier2_rate = 0.30 # For portion between tier1 and tier2

    receipt_tier3_rate = 0.10 # For portion above tier2

    if total_receipts_amount <= receipt_tier1_threshold:
        receipt_reimbursement += total_receipts_amount * receipt_tier1_rate
    else:
        receipt_reimbursement += receipt_tier1_threshold * receipt_tier1_rate
        if total_receipts_amount <= receipt_tier2_threshold:
            receipt_reimbursement += (total_receipts_amount - receipt_tier1_threshold) * receipt_tier2_rate
        else:
            receipt_reimbursement += (receipt_tier2_threshold - receipt_tier1_threshold) * receipt_tier2_rate
            receipt_reimbursement += (total_receipts_amount - receipt_tier2_threshold) * receipt_tier3_rate

    # Cents Bug/Feature
    cents_value = round((total_receipts_amount * 100) % 100)
    cents_bug_bonus = 5.00
    if cents_value == 49 or cents_value == 99:
        receipt_reimbursement += cents_bug_bonus

reimbursement += receipt_reimbursement

# Kevin's Spending Tier Penalties are REMOVED for this iteration
# Overall Reimbursement Cap is REMOVED for this iteration

# Ensure reimbursement doesn't go below zero due to penalties
reimbursement = max(0, reimbursement)

# Final output
print(f"{reimbursement:.2f}")

PY_SCRIPT
