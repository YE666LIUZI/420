# A-share "龙回头" Strategy Research Pipeline

This repository provides a reproducible, config-driven research and backtest framework for evaluating the A-share **龙回头** setup.

## Included capabilities

- Daily panel loading and preprocessing
- Feature engineering (MAs, rolling returns, volume signals)
- Deterministic pattern detection for impulse-pullback-breakout
- Swing + optional T-trading signal generation
- T+1 compliant portfolio simulation with lot tracking
- Performance metrics + attribution
- Plots and markdown report generation
- Unit tests for pattern logic, T+1 enforcement, backtest accounting, metrics

## Project structure

See `PLAN.md` for milestone mapping and implementation notes.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py --config config/strategy.yaml --generate-sample-data
python src/main.py --config config/strategy.yaml
```

## Tests

```bash
pytest -q
```

## Output

Generated artifacts are placed in `reports/output/`:

- equity curves
- drawdown plot
- return distribution
- metrics CSVs
- summary markdown report
