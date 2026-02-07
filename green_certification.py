"""
Green Building Certification Assessment
Analyzes how close a building is to LEED/BREEAM/WELL certification
and identifies specific improvements needed
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class GreenBuildingAssessor:
    """
    Assesses building against green certification standards
    Focuses on energy/carbon performance for LEED EA credits
    """
    
    def __init__(self):
        # LEED v4.1 EA (Energy & Atmosphere) credit thresholds
        # based on energy performance vs baseline
        self.leed_ea_points = {
            'points': [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 18],
            'improvement_pct': [2, 4, 6, 10, 14, 18, 22, 26, 30, 34, 36]
        }
        
        # BREEAM 2018 energy credits (simplified)
        self.breeam_thresholds = {
            'Outstanding': 85,  # points
            'Excellent': 70,
            'Very Good': 55,
            'Good': 45,
            'Pass': 30
        }
        
    def calculate_leed_ea_credits(self, predicted_emissions: float, 
                                   baseline_emissions: float) -> Dict:
        """
        Calculate LEED Energy & Atmosphere credits based on % improvement
        over baseline building performance
        
        Args:
            predicted_emissions: Building's predicted CO2 tons/year
            baseline_emissions: Baseline building CO2 tons/year (ASHRAE 90.1)
        
        Returns:
            Dict with LEED EA credits and improvement needed
        """
        improvement_pct = ((baseline_emissions - predicted_emissions) / baseline_emissions) * 100
        
        # find earned credits
        earned_credits = 0
        for i, threshold in enumerate(self.leed_ea_points['improvement_pct']):
            if improvement_pct >= threshold:
                earned_credits = self.leed_ea_points['points'][i]
        
        # calculate gap to next level
        next_level_pct = None
        next_level_credits = None
        emissions_reduction_needed = 0
        
        for i, threshold in enumerate(self.leed_ea_points['improvement_pct']):
            if improvement_pct < threshold:
                next_level_pct = threshold
                next_level_credits = self.leed_ea_points['points'][i]
                # calculate emissions reduction needed
                target_emissions = baseline_emissions * (1 - next_level_pct/100)
                emissions_reduction_needed = predicted_emissions - target_emissions
                break
        
        return {
            'current_improvement_pct': round(improvement_pct, 1),
            'earned_credits': earned_credits,
            'max_credits': 18,
            'next_level_credits': next_level_credits,
            'next_level_improvement_pct': next_level_pct,
            'emissions_reduction_needed_tons': round(emissions_reduction_needed, 1) if emissions_reduction_needed > 0 else 0,
            'certification_eligible': earned_credits >= self.leed_ea_points['points'][0]
        }
    
    def estimate_baseline_emissions(self, floor_area: float, 
                                    building_type: str) -> float:
        """
        Estimate baseline building emissions based on ASHRAE 90.1-2016
        Uses typical EUI (kBtu/sqft/year) for each building type
        
        These are conservative estimates for baseline compliance buildings
        """
        # ASHRAE 90.1-2016 baseline EUI by building type
        baseline_eui = {
            'Office': 58,
            'Retail': 52,
            'Healthcare': 215,
            'Educational': 70,
            'Warehouse': 32,
            'Multi-Family': 46,
            'Hotel': 88
        }
        
        eui = baseline_eui.get(building_type, 60)
        total_energy_kbtu = floor_area * eui
        
        # convert to CO2 using US average grid
        # 0.145 kg CO2/kBtu (60% electric, 40% gas blend)
        co2_kg = total_energy_kbtu * 0.145
        co2_tons = co2_kg / 1000
        
        return co2_tons
    
    def assess_building(self, predicted_emissions: float,
                       floor_area: float,
                       building_type: str,
                       current_features: Dict) -> Dict:
        """
        Complete assessment of building's green certification potential
        """
        # calculate baseline
        baseline = self.estimate_baseline_emissions(floor_area, building_type)
        
        # LEED assessment
        leed = self.calculate_leed_ea_credits(predicted_emissions, baseline)
        
        # emissions intensity
        emissions_per_sqft = (predicted_emissions * 1000) / floor_area
        
        # determine overall performance rating
        if leed['earned_credits'] >= 13:
            performance_rating = "Exceptional"
        elif leed['earned_credits'] >= 7:
            performance_rating = "High Performance"
        elif leed['earned_credits'] >= 3:
            performance_rating = "Above Average"
        elif leed['earned_credits'] >= 1:
            performance_rating = "Slightly Above Baseline"
        else:
            performance_rating = "Below Baseline"
        
        # specific recommendations for certification
        recommendations = self._generate_cert_recommendations(
            current_features, 
            leed['emissions_reduction_needed_tons']
        )
        
        return {
            'baseline_emissions_tons': round(baseline, 1),
            'predicted_emissions_tons': round(predicted_emissions, 1),
            'performance_rating': performance_rating,
            'leed_assessment': leed,
            'emissions_intensity_kg_sqft': round(emissions_per_sqft, 2),
            'recommendations': recommendations
        }
    
    def _generate_cert_recommendations(self, features: Dict, 
                                       target_reduction: float) -> List[Dict]:
        """
        Generate specific recommendations to achieve certification
        """
        recommendations = []
        
        # renewable energy
        if features.get('renewable_pct', 0) < 30:
            recommendations.append({
                'category': 'Renewable Energy',
                'action': 'Increase on-site renewable energy to 30%',
                'leed_credits': 'EA Credit: Renewable Energy Production',
                'estimated_impact_tons': target_reduction * 0.3,
                'cost_consideration': 'High initial investment, 5-7 year payback'
            })
        
        # HVAC upgrade
        if features.get('hvac_type') in ['Gas Furnace', 'Electric Baseboard']:
            recommendations.append({
                'category': 'HVAC Efficiency',
                'action': 'Upgrade to high-efficiency heat pump or geothermal',
                'leed_credits': 'EA Prerequisite: Minimum Energy Performance',
                'estimated_impact_tons': target_reduction * 0.25,
                'cost_consideration': 'Medium investment, 3-5 year payback'
            })
        
        # envelope improvements
        if features.get('insulation_rating') in ['Poor', 'Fair']:
            recommendations.append({
                'category': 'Building Envelope',
                'action': 'Upgrade insulation and air sealing',
                'leed_credits': 'EA Credit: Optimize Energy Performance',
                'estimated_impact_tons': target_reduction * 0.20,
                'cost_consideration': 'Low-medium investment, immediate impact'
            })
        
        # lighting
        if features.get('led_lighting_pct', 0) < 90:
            recommendations.append({
                'category': 'Lighting Systems',
                'action': 'Complete LED retrofit with occupancy sensors',
                'leed_credits': 'EA Credit: Optimize Energy Performance',
                'estimated_impact_tons': target_reduction * 0.10,
                'cost_consideration': 'Low investment, 2-3 year payback'
            })
        
        # sort by impact
        recommendations.sort(key=lambda x: x['estimated_impact_tons'], reverse=True)
        
        return recommendations

if __name__ == '__main__':
    # test the assessor
    assessor = GreenBuildingAssessor()
    
    # example building
    test_features = {
        'renewable_pct': 10,
        'hvac_type': 'Gas Furnace',
        'insulation_rating': 'Fair',
        'led_lighting_pct': 60
    }
    
    result = assessor.assess_building(
        predicted_emissions=87.2,
        floor_area=15000,
        building_type='Office',
        current_features=test_features
    )
    
    print("Green Building Assessment")
    print("=" * 50)
    print(f"Baseline: {result['baseline_emissions_tons']} tons/year")
    print(f"Predicted: {result['predicted_emissions_tons']} tons/year")
    print(f"Performance: {result['performance_rating']}")
    print(f"\nLEED EA Credits: {result['leed_assessment']['earned_credits']}/18")
    print(f"Energy Improvement: {result['leed_assessment']['current_improvement_pct']}%")
    
    if result['leed_assessment']['next_level_credits']:
        print(f"\nTo earn {result['leed_assessment']['next_level_credits']} credits:")
        print(f"  Reduce by {result['leed_assessment']['emissions_reduction_needed_tons']} tons")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. {rec['action']}")
        print(f"   Impact: ~{rec['estimated_impact_tons']:.1f} tons")
        print(f"   LEED: {rec['leed_credits']}")
