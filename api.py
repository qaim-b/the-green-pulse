"""
FastAPI backend for Building CO2 Predictor
Provides REST API endpoints for predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import pandas as pd
import pickle
import uvicorn
from datetime import datetime

# initialize FastAPI
app = FastAPI(
    title="Building CO2 Predictor API",
    description="Predict building carbon emissions from design parameters",
    version="1.0.0"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load model artifacts
try:
    with open('best_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('preprocessors.pkl', 'rb') as f:
        prep = pickle.load(f)
    with open('model_metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    prep = None
    metadata = None

# request/response models
class BuildingInput(BaseModel):
    floor_area_sqft: float = Field(..., ge=500, le=500000, description="Floor area in square feet")
    num_floors: int = Field(..., ge=1, le=60, description="Number of floors")
    building_age_years: int = Field(..., ge=0, le=120, description="Age of building in years")
    occupancy_count: int = Field(..., ge=1, le=10000, description="Number of occupants")
    hvac_type: str = Field(..., description="HVAC system type")
    insulation_rating: str = Field(..., description="Insulation quality rating")
    climate_zone: str = Field(..., description="Climate zone")
    building_type: str = Field(..., description="Building type")
    window_wall_ratio: float = Field(..., ge=0.0, le=0.5, description="Window to wall ratio")
    renewable_pct: float = Field(..., ge=0, le=100, description="Renewable energy percentage")
    led_lighting_pct: float = Field(..., ge=0, le=100, description="LED lighting percentage")
    
    @validator('hvac_type')
    def validate_hvac(cls, v):
        valid = ['Gas Furnace', 'Heat Pump', 'Electric Baseboard', 'Geothermal', 'District Steam', 'Packaged Rooftop']
        if v not in valid:
            raise ValueError(f'hvac_type must be one of {valid}')
        return v
    
    @validator('insulation_rating')
    def validate_insulation(cls, v):
        valid = ['Poor', 'Fair', 'Good', 'Excellent']
        if v not in valid:
            raise ValueError(f'insulation_rating must be one of {valid}')
        return v
    
    @validator('climate_zone')
    def validate_climate(cls, v):
        valid = ['Hot-Humid', 'Hot-Dry', 'Mixed-Humid', 'Cold', 'Very Cold', 'Marine']
        if v not in valid:
            raise ValueError(f'climate_zone must be one of {valid}')
        return v
    
    @validator('building_type')
    def validate_building_type(cls, v):
        valid = ['Office', 'Retail', 'Healthcare', 'Educational', 'Warehouse', 'Multi-Family', 'Hotel']
        if v not in valid:
            raise ValueError(f'building_type must be one of {valid}')
        return v

class PredictionOutput(BaseModel):
    co2_emissions_tons_year: float
    co2_emissions_per_sqft_kg: float
    car_equivalent: float
    confidence_interval: Optional[Dict[str, float]] = None
    benchmark_status: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: Optional[str] = None
    model_accuracy: Optional[float] = None

# endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "message": "Building CO2 Predictor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_type=metadata['best_model'] if metadata else None,
        model_accuracy=metadata['test_r2'] if metadata else None
    )

@app.post("/predict", response_model=PredictionOutput)
async def predict(building: BuildingInput):
    """
    Predict CO2 emissions for a building
    """
    if model is None or prep is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # prepare input
        input_df = pd.DataFrame([building.dict()])
        
        # encode categoricals
        for col in prep['categorical_cols']:
            if col in input_df.columns:
                le = prep['label_encoders'][col]
                input_df[col] = le.transform(input_df[col])
        
        # make prediction
        prediction = model.predict(input_df)[0]
        
        # calculate metrics
        emissions_per_sqft = (prediction * 1000) / building.floor_area_sqft
        car_equiv = prediction / 4.6
        
        # benchmark comparison
        benchmark_ranges = {
            'Office': (3, 8),
            'Retail': (3, 7),
            'Healthcare': (10, 20),
            'Educational': (4, 9),
            'Warehouse': (1.5, 4),
            'Multi-Family': (3, 6),
            'Hotel': (5, 11)
        }
        
        min_bench, max_bench = benchmark_ranges[building.building_type]
        
        if emissions_per_sqft < min_bench:
            status = "excellent"
        elif emissions_per_sqft <= max_bench:
            status = "typical"
        else:
            status = "high"
        
        return PredictionOutput(
            co2_emissions_tons_year=round(prediction, 2),
            co2_emissions_per_sqft_kg=round(emissions_per_sqft, 2),
            car_equivalent=round(car_equiv, 1),
            benchmark_status=status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(buildings: List[BuildingInput]):
    """
    Predict CO2 emissions for multiple buildings
    """
    if model is None or prep is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for building in buildings:
        try:
            result = await predict(building)
            results.append(result.dict())
        except Exception as e:
            results.append({"error": str(e)})
    
    return {"predictions": results, "count": len(results)}

@app.get("/model/info")
async def model_info():
    """Get model metadata and performance metrics"""
    if metadata is None:
        raise HTTPException(status_code=503, detail="Model metadata not loaded")
    
    return {
        "model_type": metadata['best_model'],
        "test_r2": metadata['test_r2'],
        "test_mae": metadata['test_mae'],
        "features": metadata['features'],
        "training_samples": metadata['n_train'],
        "test_samples": metadata['n_test']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
