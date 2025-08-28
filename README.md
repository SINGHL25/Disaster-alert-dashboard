# Disaster-alert-dashboard
<img width="683" height="677" alt="image" src="https://github.com/user-attachments/assets/a4442b68-2c0d-4239-94c3-f6a8a859a774" />

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
