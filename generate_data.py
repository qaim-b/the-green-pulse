"""
Building CO2 Emission Dataset Generator
Using real emission factors from research papers and energy databases
"""

import pandas as pd
import numpy as np

# set seed for reproducibility but make it less obvious
np.random.seed(2024)

def generate_building_data(num_samples=3500):
    """
    Generate synthetic but realistic building emission data
    Based on research: avg commercial building is ~4-5 kg CO2/sqft/year
    """
    
    # Building characteristics
    # floor area follows lognormal distribution - most buildings are small, some huge
    floor_areas = np.random.lognormal(mean=8.5, sigma=1.2, size=num_samples)
    floor_areas = np.clip(floor_areas, 800, 500000)  # 800 sqft to 500k sqft range
    
    num_floors = []
    for area in floor_areas:
        # larger buildings tend to have more floors
        if area < 5000:
            floors = np.random.randint(1, 4)
        elif area < 20000:
            floors = np.random.randint(1, 8)
        elif area < 100000:
            floors = np.random.randint(3, 25)
        else:
            floors = np.random.randint(10, 60)
        num_floors.append(floors)
    
    # other features
    building_ages = np.random.exponential(scale=22, size=num_samples)
    building_ages = np.clip(building_ages, 0, 120)
    
    # occupancy density varies by building type
    occupancy_per_sqft = np.random.uniform(0.002, 0.05, num_samples)  # people per sqft
    occupancy = (floor_areas * occupancy_per_sqft).astype(int)
    
    # categorical features with realistic distributions
    hvac_options = ['Gas Furnace', 'Heat Pump', 'Electric Baseboard', 
                    'Geothermal', 'District Steam', 'Packaged Rooftop']
    hvac_probs = [0.35, 0.25, 0.10, 0.05, 0.15, 0.10]
    
    insulation = ['Poor', 'Fair', 'Good', 'Excellent']
    insul_probs = [0.20, 0.35, 0.30, 0.15]
    
    climate_zones = ['Hot-Humid', 'Hot-Dry', 'Mixed-Humid', 'Cold', 'Very Cold', 'Marine']
    climate_probs = [0.15, 0.12, 0.25, 0.25, 0.15, 0.08]
    
    building_types = ['Office', 'Retail', 'Healthcare', 'Educational', 
                      'Warehouse', 'Multi-Family', 'Hotel']
    type_probs = [0.22, 0.18, 0.08, 0.12, 0.15, 0.15, 0.10]
    
    df = pd.DataFrame({
        'floor_area_sqft': floor_areas,
        'num_floors': num_floors,
        'building_age_years': building_ages,
        'occupancy_count': occupancy,
        'hvac_type': np.random.choice(hvac_options, num_samples, p=hvac_probs),
        'insulation_rating': np.random.choice(insulation, num_samples, p=insul_probs),
        'climate_zone': np.random.choice(climate_zones, num_samples, p=climate_probs),
        'building_type': np.random.choice(building_types, num_samples, p=type_probs),
        'window_wall_ratio': np.random.beta(2, 3, num_samples) * 0.5,  # typically 0.15-0.40
        'renewable_pct': np.random.beta(2, 5, num_samples) * 100,  # most have little renewable
        'led_lighting_pct': np.random.beta(3, 2, num_samples) * 100,
    })
    
    return df

def calculate_emissions(df):
    """
    Calculate CO2 emissions using physics-based approach
    Target: ~4-5 kg CO2/sqft/year for baseline
    """
    
    # base energy intensity (kBtu/sqft/year) - from CBECS 2012 data
    # adjusted down slightly to match typical 2024 buildings
    base_eui = {
        'Office': 52,
        'Retail': 48,
        'Healthcare': 195,  # hospitals are energy intensive
        'Educational': 65,
        'Warehouse': 28,
        'Multi-Family': 42,
        'Hotel': 82
    }
    df['eui_base'] = df['building_type'].map(base_eui)
    
    # HVAC efficiency factors (relative to baseline)
    hvac_eff = {
        'Gas Furnace': 1.15,      # less efficient
        'Heat Pump': 0.75,         # good COP
        'Electric Baseboard': 1.30,
        'Geothermal': 0.60,        # best efficiency
        'District Steam': 0.85,
        'Packaged Rooftop': 1.00   # baseline
    }
    df['hvac_factor'] = df['hvac_type'].map(hvac_eff)
    
    # insulation impact
    insul_mult = {'Excellent': 0.75, 'Good': 0.90, 'Fair': 1.05, 'Poor': 1.25}
    df['insul_factor'] = df['insulation_rating'].map(insul_mult)
    
    # climate heating/cooling loads
    climate_mult = {'Hot-Humid': 1.15, 'Hot-Dry': 1.10, 'Mixed-Humid': 1.00,
                    'Cold': 1.30, 'Very Cold': 1.50, 'Marine': 0.95}
    df['climate_factor'] = df['climate_zone'].map(climate_mult)
    
    # age degradation - older = less efficient
    df['age_factor'] = 1.0 + (df['building_age_years'] / 150)
    
    # window to wall ratio impact (more windows = more heat loss/gain)
    df['window_factor'] = 1.0 + (df['window_wall_ratio'] * 0.4)
    
    # occupancy load (more people = more heating/cooling needed)
    df['occupancy_factor'] = 1.0 + (df['occupancy_count'] / df['floor_area_sqft']) * 2.0
    
    # renewable energy offset
    df['renewable_factor'] = (100 - df['renewable_pct']) / 100
    
    # LED lighting reduces cooling load
    df['lighting_factor'] = 1.0 - (df['led_lighting_pct'] / 400)  # small but real effect
    
    # calculate total energy use
    df['annual_eui'] = (df['eui_base'] * 
                        df['hvac_factor'] * 
                        df['insul_factor'] * 
                        df['climate_factor'] *
                        df['age_factor'] *
                        df['window_factor'] *
                        df['occupancy_factor'] *
                        df['lighting_factor'])
    
    # convert to total energy (kBtu/year)
    df['total_energy_kbtu'] = df['annual_eui'] * df['floor_area_sqft']
    
    # CO2 conversion - US average grid
    # Electricity: ~0.92 lb CO2/kWh = 0.417 kg/kWh
    # 1 kBtu = 0.293 kWh → 0.122 kg CO2/kBtu for electric
    # Natural gas: 0.18 kg CO2/kBtu
    # Most buildings ~60% electric, 40% gas
    # Blended: 0.6*0.122 + 0.4*0.18 = 0.145 kg CO2/kBtu
    df['co2_kg_year'] = df['total_energy_kbtu'] * 0.145
    
    # add renewable offset
    df['co2_kg_year'] = df['co2_kg_year'] * df['renewable_factor']
    
    # add noise to make it realistic (buildings aren't perfectly predictable)
    noise = np.random.normal(1.0, 0.055, len(df))
    df['co2_kg_year'] = df['co2_kg_year'] * noise
    
    # convert to tons
    df['co2_tons_year'] = df['co2_kg_year'] / 1000
    
    # drop intermediate calculation columns
    calc_cols = [c for c in df.columns if c.endswith('_factor') or c in ['eui_base', 'annual_eui', 'total_energy_kbtu']]
    df = df.drop(columns=calc_cols)
    
    return df

if __name__ == '__main__':
    print("Generating building dataset...")
    df = generate_building_data(3500)
    df = calculate_emissions(df)
    
    print(f"\nDataset: {len(df)} buildings")
    print(f"\nCO2 emissions (tons/year):")
    print(df['co2_tons_year'].describe())
    
    print(f"\nEmissions per sqft:")
    df['co2_per_sqft'] = df['co2_kg_year'] / df['floor_area_sqft']
    print(df['co2_per_sqft'].describe())  # should be ~4-5 kg/sqft
    
    # check correlations
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove('co2_kg_year')
    correlations = df[numeric_cols].corrwith(df['co2_tons_year']).sort_values(ascending=False)
    print(f"\nTop correlations with CO2:")
    print(correlations.head(8))
    
    # save
    df.to_csv('building_emissions.csv', index=False)
    print("\n✓ Saved to building_emissions.csv")
