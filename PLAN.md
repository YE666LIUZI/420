# Implementation Plan Mapping

## Milestone coverage

1. **Scaffolding**: Directory structure, config, CLI, README complete.
2. **Data model**: `data_loader.py`, `preprocess.py`, `features.py`.
3. **Pattern quantification**: `pattern_rules.py` deterministic v1 rules.
4. **Signal engine**: `signal_engine.py` for swing and T-trading actions.
5. **Portfolio & execution**: `portfolio.py`, `backtest.py` with T+1 constraints.
6. **Metrics & attribution**: `metrics.py` and experiment runner in `main.py`.
7. **Ranking/scoring**: factor score + daily ranking in signal engine.
8. **Visualization/reporting**: `plots.py` + markdown report generation.
9. **Validation/tests**: tests under `tests/`.
