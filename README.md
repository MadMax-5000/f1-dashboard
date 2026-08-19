# F1 Predictions

Machine learning predictions for Formula 1 — race winners, qualifying, championship outcomes, lap times, and strategy — plus live standings and race results.

## Project Structure

```
src/
├── data/         # Data collection (FastF1, Ergast API) + synthetic data generator
├── features/     # Feature engineering pipeline
├── models/       # ML models (XGBoost, LightGBM, Monte Carlo)
├── predict/      # Unified prediction interface
└── api/          # FastAPI server
frontend/         # Next.js dashboard (predictions + F1 stats)
data/             # Raw & processed data (parquet files)
notebooks/        # Jupyter exploration
```

## Models

| Model | Task | Method |
|-------|------|--------|
| Race Winner | Win/podium probability | XGBoost classifier |
| Qualifying | Predicted grid position | LightGBM regressor |
| Championship | Season outcome probability | Monte Carlo simulation (10k runs) |
| Lap Times | Expected lap time | XGBoost regressor |
| Strategy | Pit stops & compounds | Heuristic + historical patterns |

## Frontend Pages

- **Predictions** — Race winner & podium probability bars, predicted qualifying order
- **Championship** — Interactive Monte Carlo simulation with adjustable remaining races
- **Races** — Full race results with podium highlights and classifications
- **Drivers** — Driver cards with team colors, points, and wins
- **Standings** — WDC & WCC tables (driver and constructor tabs)
- **Model Performance** — Accuracy, log loss, MAE metrics for trained models

## Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Collect historical data (2018-2026) from Ergast API
python -m src.data.collect

# Or generate synthetic data if offline
python -m src.data.generate_synthetic

# Build feature matrix
python -m src.features.engineering

# Train models
python -m src.models.race_winner
python -m src.models.qualifying

# Start prediction API
uvicorn src.api.app:app --reload --port 8000

# Start frontend (separate terminal)
cd frontend && npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/predictions/next-race` | Winner & podium probabilities for latest race |
| POST | `/predictions/championship` | Monte Carlo championship simulation |
| POST | `/predictions/strategy` | Race strategy prediction (pit windows, compounds) |
| GET | `/models/performance` | Model accuracy metrics |
| GET | `/health` | API health check |

## Data Sources

- **FastF1** — Lap times, telemetry, tire data, weather
- **Ergast/Jolpica API** — Historical results, standings, qualifying, schedules

## Tech Stack

- **Python** — pandas, scikit-learn, XGBoost, LightGBM, FastAPI
- **Frontend** — Next.js 15, React, Tailwind CSS
- **Data** — Parquet files (columnar, fast reads)
