# Scanner Foundation

Scanner is open for Phase 4 foundation contract work.

Current scope:

- universe identity and membership contracts
- universe definition and membership snapshot validation helpers
- declarative FeatureHub input references
- filter specification contracts
- deterministic in-memory filter matching primitives
- deterministic in-memory scan runner primitives over caller-supplied inputs
- scan candidate and run metadata containers
- local candidate-list JSONL and manifest persistence

Non-goals for this phase slice:

- ranking or scoring
- strategy, backtest, signal, or portfolio logic
- live data access
- persistence orchestration beyond explicit local artifact writes

Runner behavior in the current phase slice:

- consumes only in-memory universe snapshots, filters, and per-symbol feature values
- emits validated `ScanCandidateList` objects only
- candidate rows use a stable `(symbol, market)` sort order
- no ranking, scoring, orchestration, refresh, or external reads
