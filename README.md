# The Green Pulse

ML-powered carbon analytics tool for buildings. Predicts emissions, scores sustainability, simulates retrofit scenarios, and estimates ROI.

Built with Streamlit, XGBoost, and Plotly.

## Features

- **Single Building Analysis** — Predict annual CO2 emissions, get a LEED-inspired sustainability score, and receive actionable retrofit recommendations
- **Portfolio View** — Compare multiple buildings side-by-side with aggregate metrics and exportable data
- **ROI Calculator** — Model payback timelines for solar, heat pumps, insulation, LED, and envelope upgrades
- **Analytics Dashboard** — Model performance metrics, feature importance, and industry benchmarks

## Quick Start

```bash
pip install -r requirements.txt
python generate_data.py
python train_models.py
streamlit run app.py
```

## Tech Stack

Python, Streamlit, XGBoost, Plotly, FPDF2, FastAPI, SHAP
