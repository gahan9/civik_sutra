---
name: prysm-testing-quality
description: Run Prysm tests and evaluate LangGraph pipeline outputs against docs/quality_matrix.md (six dimensions, composite score, accuracy tracking). Use when running pytest, validating quality_node scores, comparing predicted vs gold labels, or assessing router/counselor/triage calibration.
---

# Prysm testing and quality evaluation

Use this skill whenever you need to **execute tests**, **validate the Quality Matrix implementation**, or **measure LangGraph / model accuracy** against product docs.

## Canonical spec

Read and follow **`docs/quality_matrix.md`**:

| Dimension | Weight |
|-----------|--------|
| Completeness | 0.20 |
| Reproducibility | 0.20 |
| Specificity | 0.15 |
| Context Richness | 0.15 |
| Historical Correlation | 0.15 |
| AI Confidence | 0.15 |

Each dimension is scored **0.0–1.0**. A composite quality score (when implemented) must use this weighted sum unless the doc is explicitly updated.

**Accuracy Tracking** (same doc): store AI-predicted classification and priority with engineer final disposition; compare predicted vs actual over time; track per-counselor accuracy.

## Run tests

From the repository root:

```bash
pytest tests/ -v --tb=short
```

If the project uses async tests:

```bash
pytest tests/ -v --tb=short -q
```

Narrow scope after localized changes:

```bash
pytest tests/test_quality.py tests/test_router.py -v --tb=short
```

Always run at least the tests that touch modified graph or quality code before claiming work is complete.

## Evaluate pipeline output vs Quality Matrix

1. Build or load a **fixture** `PipelineState` (or invoke `build_pipeline()` / nodes with mocked issue data).
2. After the **quality** node (`prysm/graph/quality.py`), assert:
   - Each of the six dimension keys exists when the implementation promises them (or document TODO if still scaffold).
   - Values are in `[0.0, 1.0]` where applicable.
   - `ai_confidence` aligns with the doc: weighted average from Router + Counselor + Triage confidences when that is the implemented formula.
3. **Composite check:**  
   `quality_score ≈ sum(weight_i * dimension_i)` with weights from the table above (allow small float tolerance, e.g. `1e-3`).

## LangGraph accuracy (offline)

1. **Router:** For each fixture, assert `intent`, `persona`, `source`, and `confidence` against expected labels derived from `docs/router_engine.md` rules where deterministic.
2. **Counselor:** Assert `domain` matches router `persona` mapping (qa / dev / devops) when dispatch is implemented.
3. **Triage:** Assert `classification` and `triage_confidence` against gold JSON for defect vs feature fixtures (`docs/triage_engine.md` layers as reference).
4. **Quality:** Cross-check six dimensions and composite against `docs/quality_matrix.md`.

Prefer **table-driven** tests (parametrize) for multiple tickets.

## Model performance (when LLM is in the path)

- Record: latency, token usage (if available), parse success rate for structured output.
- **Classification:** precision/recall or accuracy on a frozen eval set; stratify by persona/counselor for per-domain weakness analysis (per Accuracy Tracking).
- Do not log secrets or full internal ticket bodies in eval artifacts; redact as needed.

## Delegation

For day-to-day implementation work, the **test-quality-evaluator** subagent (`.cursor/agents/test-quality-evaluator.md`) carries the same priorities with a system-prompt focus; this skill is the **checklist and command reference**.
