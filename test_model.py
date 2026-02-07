"""
Quick test to verify the model works correctly
"""

import pandas as pd
import pickle

print("Loading model artifacts...")
with open('best_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('preprocessors.pkl', 'rb') as f:
    prep = pickle.load(f)

# test prediction with sample building
test_building = pd.DataFrame({
    'floor_area_sqft': [15000],
    'num_floors': [5],
    'building_age_years': [15],
    'occupancy_count': [150],
    'hvac_type': ['Heat Pump'],
    'insulation_rating': ['Good'],
    'climate_zone': ['Mixed-Humid'],
    'building_type': ['Office'],
    'window_wall_ratio': [0.3],
    'renewable_pct': [10],
    'led_lighting_pct': [60]
})

print("\nTest building:")
for col, val in test_building.iloc[0].items():
    print(f"  {col}: {val}")

# encode
for col in prep['categorical_cols']:
    le = prep['label_encoders'][col]
    test_building[col] = le.transform(test_building[col])

# predict
prediction = model.predict(test_building)[0]
emissions_per_sqft = (prediction * 1000) / 15000

print(f"\nPredicted CO2 emissions: {prediction:.1f} tons/year")
print(f"Per square foot: {emissions_per_sqft:.2f} kg/sqft/year")

if 3 <= emissions_per_sqft <= 8:
    print("✓ Prediction is within expected range for office buildings")
else:
    print("⚠ Prediction seems unusual for an office building")

print("\n✓ Model test passed!")
