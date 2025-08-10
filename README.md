# Disaster-alert-dashboard

# Global Disaster & Emergency Alert System

Streamlit dashboard that fetches alerts from:
- USGS (earthquakes)
- NWS (US weather alerts)
- BOM (Australia) — sample/stub included; see notes
- IMD (India) — sample/stub included; see notes

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
