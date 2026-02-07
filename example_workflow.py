"""
Example Consulting Workflow
Demonstrates how to use the Building Carbon Predictor for a client engagement
"""

import pandas as pd
import pickle
from green_certification import GreenBuildingAssessor

# load model
with open('best_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('preprocessors.pkl', 'rb') as f:
    prep = pickle.load(f)

assessor = GreenBuildingAssessor()

# ==============================================================================
# SCENARIO: Client has 3 office buildings, wants LEED certification roadmap
# ==============================================================================

print("="*70)
print("CLIENT ENGAGEMENT: Downtown Office Portfolio LEED Certification")
print("="*70)
print()

# Client's building data
buildings = [
    {
        'name': 'Building A - Main Tower',
        'floor_area_sqft': 125000,
        'num_floors': 25,
        'building_age_years': 12,
        'occupancy_count': 1250,
        'hvac_type': 'Gas Furnace',
        'insulation_rating': 'Fair',
        'climate_zone': 'Cold',
        'building_type': 'Office',
        'window_wall_ratio': 0.40,
        'renewable_pct': 0,
        'led_lighting_pct': 35
    },
    {
        'name': 'Building B - North Wing',
        'floor_area_sqft': 85000,
        'num_floors': 18,
        'building_age_years': 8,
        'occupancy_count': 850,
        'hvac_type': 'Heat Pump',
        'insulation_rating': 'Good',
        'climate_zone': 'Cold',
        'building_type': 'Office',
        'window_wall_ratio': 0.30,
        'renewable_pct': 15,
        'led_lighting_pct': 75
    },
    {
        'name': 'Building C - Annex',
        'floor_area_sqft': 45000,
        'num_floors': 8,
        'building_age_years': 25,
        'occupancy_count': 400,
        'hvac_type': 'Packaged Rooftop',
        'insulation_rating': 'Poor',
        'climate_zone': 'Cold',
        'building_type': 'Office',
        'window_wall_ratio': 0.35,
        'renewable_pct': 0,
        'led_lighting_pct': 20
    }
]

# analyze each building
results = []

for building in buildings:
    # create input dataframe with only feature columns
    building_copy = building.copy()
    building_name = building_copy.pop('name')  # remove name before prediction
    
    input_df = pd.DataFrame([building_copy])
    
    # encode categoricals
    for col in prep['categorical_cols']:
        if col in input_df.columns:
            le = prep['label_encoders'][col]
            input_df[col] = le.transform(input_df[col])
    
    # predict
    prediction = model.predict(input_df)[0]
    emissions_per_sqft = (prediction * 1000) / building['floor_area_sqft']
    
    # LEED assessment
    leed = assessor.assess_building(
        prediction,
        building['floor_area_sqft'],
        building['building_type'],
        {
            'renewable_pct': building['renewable_pct'],
            'hvac_type': building['hvac_type'],
            'insulation_rating': building['insulation_rating'],
            'led_lighting_pct': building['led_lighting_pct']
        }
    )
    
    results.append({
        'building': building,
        'prediction': prediction,
        'emissions_per_sqft': emissions_per_sqft,
        'leed': leed
    })

# generate executive summary
print("EXECUTIVE SUMMARY")
print("-" * 70)
print()

total_emissions = sum([r['prediction'] for r in results])
total_area = sum([b['floor_area_sqft'] for b in buildings])
avg_intensity = (total_emissions * 1000) / total_area

print(f"Portfolio Total Emissions: {total_emissions:.0f} tons CO2/year")
print(f"Portfolio Total Area: {total_area:,} sq ft")
print(f"Average Intensity: {avg_intensity:.2f} kg CO2/sqft/year")
print()

# building-by-building breakdown
print("BUILDING-BY-BUILDING ANALYSIS")
print("-" * 70)
print()

for result in results:
    building = result['building']
    leed = result['leed']
    
    print(f"📍 {building['name']}")
    print(f"   Area: {building['floor_area_sqft']:,} sq ft | Age: {building['building_age_years']} years")
    print(f"   Annual CO2: {result['prediction']:.1f} tons/year")
    print(f"   Intensity: {result['emissions_per_sqft']:.2f} kg CO2/sqft/year")
    print(f"   LEED EA Credits: {leed['leed_assessment']['earned_credits']}/18")
    print(f"   Performance: {leed['performance_rating']}")
    print(f"   Improvement vs Baseline: {leed['leed_assessment']['current_improvement_pct']:.1f}%")
    print()

# prioritization recommendations
print("PRIORITIZATION RECOMMENDATIONS")
print("-" * 70)
print()

# sort by worst performers
sorted_results = sorted(results, key=lambda x: x['emissions_per_sqft'], reverse=True)

print("Priority 1: Highest Emissions Intensity")
worst = sorted_results[0]
print(f"   {worst['building']['name']}")
print(f"   Current: {worst['emissions_per_sqft']:.2f} kg CO2/sqft/year")
print(f"   Target: ~5.5 kg CO2/sqft/year (office average)")
print(f"   Reduction needed: {(worst['emissions_per_sqft'] - 5.5):.2f} kg/sqft")
print()

# identify lowest LEED credits
sorted_leed = sorted(results, key=lambda x: x['leed']['leed_assessment']['earned_credits'])
print("Priority 2: Lowest LEED EA Credits")
lowest_leed = sorted_leed[0]
print(f"   {lowest_leed['building']['name']}")
print(f"   Current credits: {lowest_leed['leed']['leed_assessment']['earned_credits']}/18")
print(f"   Needs {lowest_leed['leed']['leed_assessment']['emissions_reduction_needed_tons']:.0f} tons reduction for next level")
print()

# quick win opportunities
print("QUICK WIN OPPORTUNITIES (ROI < 3 years)")
print("-" * 70)
print()

for result in results:
    building = result['building']
    if building['led_lighting_pct'] < 80:
        payback = 2.0  # LED retrofit typically 2 years
        reduction = result['prediction'] * 0.08  # 8% reduction
        print(f"✅ {building['name']}: LED Retrofit")
        print(f"   Current LED coverage: {building['led_lighting_pct']}%")
        print(f"   Estimated cost: ${building['floor_area_sqft'] * 1.2:,.0f}")
        print(f"   CO2 reduction: {reduction:.1f} tons/year")
        print(f"   Payback: ~{payback} years")
        print()
    
    if building['insulation_rating'] == 'Poor':
        payback = 3.0  # insulation upgrade typically 3 years
        reduction = result['prediction'] * 0.15  # 15% reduction
        print(f"✅ {building['name']}: Insulation Upgrade")
        print(f"   Current: {building['insulation_rating']}")
        print(f"   Estimated cost: ${building['floor_area_sqft'] * 3.5:,.0f}")
        print(f"   CO2 reduction: {reduction:.1f} tons/year")
        print(f"   Payback: ~{payback} years")
        print()

# portfolio-wide recommendations
print("PORTFOLIO-WIDE STRATEGY")
print("-" * 70)
print()
print("Phase 1 (Year 1): Quick Wins")
print("   - LED retrofit all buildings")
print("   - Upgrade insulation in Building C")
print("   - Estimated total cost: $X,XXX,XXX")
print("   - Expected reduction: XX tons/year")
print()
print("Phase 2 (Years 2-3): Major Systems")
print("   - HVAC upgrade in Building A (gas → heat pump)")
print("   - Solar PV installation on all rooftops")
print("   - Estimated total cost: $X,XXX,XXX")
print("   - Expected reduction: XX tons/year")
print()
print("Phase 3 (Years 4-5): Optimization")
print("   - Building envelope improvements")
print("   - BMS/controls upgrades")
print("   - LEED certification for all buildings")
print()

print("="*70)
print("END OF ANALYSIS")
print("="*70)
print()
print("📊 Next Steps:")
print("   1. Review this analysis with client")
print("   2. Generate detailed PDF reports (use app.py)")
print("   3. Schedule site visits for verification")
print("   4. Prepare detailed cost estimates for Phase 1")
print("   5. Set up tracking dashboard for ongoing monitoring")
