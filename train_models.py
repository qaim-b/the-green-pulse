"""
Train models to predict building CO2 emissions
Trying multiple approaches to see what works best
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

# load data
df = pd.read_csv('building_emissions.csv')
print(f"Loaded {len(df)} buildings")

# target variable
target = 'co2_tons_year'

# drop co2_kg_year since it's just the target in different units
features = [c for c in df.columns if c not in [target, 'co2_kg_year', 'co2_per_sqft']]

print(f"\nFeatures: {features}")
print(f"Target: {target}")

# encode categorical variables
label_encoders = {}
categorical_cols = df[features].select_dtypes(include=['object']).columns.tolist()

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df[features]
y = df[target]

# tried different splits, 80/20 works well here
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# scale features - helps with tree models surprisingly
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# ========== Model Training ==========
print("\n" + "="*50)
print("Training models...")
print("="*50)

models = {}

# 1. Random Forest - solid baseline
print("\n[1/4] Random Forest...")
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
models['rf'] = rf

# 2. Gradient Boosting
print("[2/4] Gradient Boosting...")
gb = GradientBoostingRegressor(
    n_estimators=150,
    max_depth=8,
    learning_rate=0.1,
    min_samples_split=10,
    random_state=42
)
gb.fit(X_train, y_train)
models['gb'] = gb

# 3. XGBoost - usually performs well
print("[3/4] XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)
models['xgb'] = xgb_model

# 4. LightGBM - fast and accurate
print("[4/4] LightGBM...")
lgb_model = lgb.LGBMRegressor(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.08,
    num_leaves=50,
    random_state=42,
    verbose=-1
)
lgb_model.fit(X_train, y_train)
models['lgb'] = lgb_model

# ========== Evaluation ==========
print("\n" + "="*50)
print("Model Performance")
print("="*50)

results = {}
for name, model in models.items():
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_train, pred_train)
    test_mae = mean_absolute_error(y_test, pred_test)
    train_r2 = r2_score(y_train, pred_train)
    test_r2 = r2_score(y_test, pred_test)
    
    results[name] = {
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2
    }
    
    print(f"\n{name.upper()}:")
    print(f"  Train MAE: {train_mae:.2f} tons/year  |  R²: {train_r2:.4f}")
    print(f"  Test MAE:  {test_mae:.2f} tons/year  |  R²: {test_r2:.4f}")

# pick best model based on test MAE
best_model_name = min(results, key=lambda x: results[x]['test_mae'])
best_model = models[best_model_name]

print(f"\n{'='*50}")
print(f"Best model: {best_model_name.upper()}")
print(f"Test MAE: {results[best_model_name]['test_mae']:.2f} tons")
print(f"Test R²: {results[best_model_name]['test_r2']:.4f}")
print(f"{'='*50}")

# ========== Feature Importance ==========
if hasattr(best_model, 'feature_importances_'):
    importance = pd.DataFrame({
        'feature': features,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(importance.head(10).to_string(index=False))

# ========== Save Everything ==========
print("\nSaving models and preprocessors...")

# save best model
with open('best_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

# save all models for comparison
with open('all_models.pkl', 'wb') as f:
    pickle.dump(models, f)

# save preprocessing objects
with open('preprocessors.pkl', 'wb') as f:
    pickle.dump({
        'scaler': scaler,
        'label_encoders': label_encoders,
        'feature_names': features,
        'categorical_cols': categorical_cols
    }, f)

# save some metadata
metadata = {
    'best_model': best_model_name,
    'test_mae': results[best_model_name]['test_mae'],
    'test_r2': results[best_model_name]['test_r2'],
    'features': features,
    'n_train': len(X_train),
    'n_test': len(X_test)
}
with open('model_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

print("\n✓ All models saved successfully")
print("  - best_model.pkl")
print("  - all_models.pkl")
print("  - preprocessors.pkl")
print("  - model_metadata.pkl")
