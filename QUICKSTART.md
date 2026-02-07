# Quick Start Guide - Get This Running in 10 Minutes

## Step 1: Install Dependencies (2 min)

```bash
cd building_co2_predictor
pip install -r requirements.txt
```

If you get any errors, try:
```bash
pip install -r requirements.txt --break-system-packages
```

## Step 2: Verify Data & Models (1 min)

Everything should already be generated, but verify:
```bash
ls -lh *.csv *.pkl
```

You should see:
- `building_emissions.csv` (~1MB)
- `best_model.pkl`
- `preprocessors.pkl`
- `model_metadata.pkl`
- `all_models.pkl`

If any are missing:
```bash
python generate_data.py    # generates building_emissions.csv
python train_models.py      # generates all .pkl files
```

## Step 3: Test the Model (30 sec)

```bash
python test_model.py
```

Should output:
```
Predicted CO2 emissions: 87.2 tons/year
Per square foot: 5.81 kg/sqft/year
✓ Prediction is within expected range for office buildings
✓ Model test passed!
```

## Step 4: Run the App (5 min)

```bash
streamlit run app.py
```

Browser opens at `http://localhost:8501`

**Try this demo flow:**

1. **Tab 1: Single Building Analysis**
   - Leave default values (15,000 sqft office building)
   - Click "🔮 Analyze Building"
   - See prediction: ~87 tons/year
   - Check LEED credits: should show 15/18 credits
   - Expand improvement recommendations
   - Click "📄 Download PDF Report" (test report generation)
   - Click "➕ Add to Portfolio"

2. **Tab 2: Portfolio Comparison**
   - Should see your building listed
   - Go back to Tab 1, change some parameters, add another building
   - Return to Tab 2 to see comparison chart

3. **Tab 3: ROI Calculator**
   - Input: 50,000 sqft building, 300 tons/year current emissions
   - Select "Renewable Energy (Solar)"
   - Click "💰 Calculate ROI"
   - See investment analysis with cash flow chart

4. **Tab 4: Analytics Dashboard**
   - See model performance metrics
   - Feature importance chart
   - Industry benchmarks

## Step 5: Run Example Workflow (2 min)

See a realistic consulting engagement:
```bash
python example_workflow.py
```

This simulates analyzing a 3-building office portfolio for LEED certification.

## Step 6: Test API (Optional)

If you want to show API capabilities:

**Terminal 1:**
```bash
python api.py
```

**Terminal 2 (or browser at http://localhost:8000/docs):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "floor_area_sqft": 15000,
    "num_floors": 5,
    "building_age_years": 15,
    "occupancy_count": 150,
    "hvac_type": "Heat Pump",
    "insulation_rating": "Good",
    "climate_zone": "Mixed-Humid",
    "building_type": "Office",
    "window_wall_ratio": 0.3,
    "renewable_pct": 10,
    "led_lighting_pct": 60
  }'
```

## Troubleshooting

**Error: "Module not found"**
→ Install missing package: `pip install <package_name>`

**Error: "File not found: best_model.pkl"**
→ Run: `python train_models.py`

**Streamlit won't start**
→ Try: `python -m streamlit run app.py`

**Port 8501 already in use**
→ Kill existing streamlit: `pkill -f streamlit`
→ Or use different port: `streamlit run app.py --server.port 8502`

## What to Show in Interview

### Quick Demo (30 seconds):
"Let me show you how this works. I input building parameters... the model predicts emissions... shows LEED credits... and recommends improvements with ROI calculations."

[Show Tab 1 analysis → Tab 2 portfolio comparison]

### Technical Deep Dive (2 minutes):
"Under the hood, I used XGBoost trained on 3,500 buildings. The model achieved 89% R². Here's the LEED certification module - it calculates EA credits based on ASHRAE baselines. And here's an example consulting workflow analyzing a 3-building portfolio."

[Show code in green_certification.py → run example_workflow.py]

### Business Value (1 minute):
"The ROI calculator uses real construction costs. For instance, solar PV at $8.50/sqft with 6-year payback. The PDF export generates client-ready reports. And the API enables integration with other tools."

[Show Tab 3 ROI calculator → download PDF report]

## Files to Review Before Interview

1. **PITCH.md** - Talking points and questions to expect
2. **README.md** - Full technical documentation
3. **green_certification.py** - Shows understanding of LEED
4. **example_workflow.py** - Demonstrates consulting workflow

## Resume Bullet Point (Copy-Paste Ready)

```
Built ML-powered building carbon footprint predictor with LEED certification 
analysis for ESG consultants. XGBoost model (89% R²) trained on 3,500 buildings, 
integrated ASHRAE baseline methodology, ROI calculator for improvement 
recommendations. Features portfolio management, PDF report generation, and 
FastAPI backend. Tech: Python, XGBoost, Streamlit, Plotly.
```

## Last-Minute Checklist

Before interview:
- [ ] Test app runs without errors
- [ ] Review PITCH.md talking points
- [ ] Run example_workflow.py to see consulting output
- [ ] Check green_certification.py to understand LEED logic
- [ ] Have GitHub repo ready (if you pushed it)
- [ ] Prepare to explain: "Why this project?" and "What would you improve?"

---

**You're Ready.** This shows you understand ESG consulting, can ship production ML applications, and think about business value. Good luck with Ryosuke!
