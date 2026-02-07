"""
SHAP-based model explainability
Shows why the model made specific predictions
"""

import shap
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class ModelExplainer:
    def __init__(self, model_path='best_model.pkl', preprocessor_path='preprocessors.pkl'):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(preprocessor_path, 'rb') as f:
            self.prep = pickle.load(f)
        
        # load some background data for SHAP
        df = pd.read_csv('building_emissions.csv')
        
        # prepare background dataset (sample 100 for speed)
        background = df.sample(min(100, len(df)), random_state=42)
        background = background[self.prep['feature_names']]
        
        # encode categoricals
        for col in self.prep['categorical_cols']:
            le = self.prep['label_encoders'][col]
            background[col] = le.transform(background[col])
        
        # create SHAP explainer
        self.explainer = shap.TreeExplainer(self.model, background)
        
    def explain_prediction(self, input_df, feature_names=None):
        """
        Get SHAP values for a prediction
        Returns: dict with feature contributions
        """
        shap_values = self.explainer.shap_values(input_df)
        
        if feature_names is None:
            feature_names = self.prep['feature_names']
        
        # get base value (average prediction)
        base_value = self.explainer.expected_value
        
        # create explanation dict
        contributions = {}
        for i, feature in enumerate(feature_names):
            contributions[feature] = {
                'value': input_df.iloc[0, i],
                'impact': shap_values[0, i],
                'impact_pct': abs(shap_values[0, i]) / (abs(shap_values[0]).sum() + 1e-10) * 100
            }
        
        # sort by absolute impact
        sorted_contributions = dict(sorted(
            contributions.items(), 
            key=lambda x: abs(x[1]['impact']), 
            reverse=True
        ))
        
        return {
            'base_prediction': base_value,
            'contributions': sorted_contributions,
            'final_prediction': base_value + shap_values[0].sum()
        }
    
    def get_top_drivers(self, input_df, n=5):
        """
        Get top N features driving the prediction
        """
        explanation = self.explain_prediction(input_df)
        
        drivers = []
        for feature, data in list(explanation['contributions'].items())[:n]:
            # decode categorical values back
            value = data['value']
            if feature in self.prep['categorical_cols']:
                le = self.prep['label_encoders'][feature]
                value = le.inverse_transform([int(value)])[0]
            
            drivers.append({
                'feature': feature,
                'value': value,
                'impact': data['impact'],
                'direction': 'increases' if data['impact'] > 0 else 'decreases',
                'impact_pct': data['impact_pct']
            })
        
        return drivers

if __name__ == '__main__':
    # test the explainer
    explainer = ModelExplainer()
    
    # create test building
    test = pd.DataFrame({
        'floor_area_sqft': [50000],
        'num_floors': [15],
        'building_age_years': [25],
        'occupancy_count': [500],
        'hvac_type': [2],  # already encoded for testing
        'insulation_rating': [1],
        'climate_zone': [2],
        'building_type': [0],
        'window_wall_ratio': [0.35],
        'renewable_pct': [5],
        'led_lighting_pct': [40]
    })
    
    drivers = explainer.get_top_drivers(test)
    
    print("Top prediction drivers:")
    for i, driver in enumerate(drivers, 1):
        sign = '+' if driver['impact'] > 0 else ''
        print(f"{i}. {driver['feature']} = {driver['value']}")
        print(f"   Impact: {sign}{driver['impact']:.1f} tons ({driver['impact_pct']:.1f}%)")
        print(f"   {driver['direction'].capitalize()} emissions\n")
