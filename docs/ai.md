# LedgerLens AI & Investigation Architecture

## 1. Separation of Responsibilities

* **Phase 3 (Deterministic Engine)**: 100% deterministic code computes exact monetary balances, fee schedules, tax deductions, multi-pass ID matching, and structured machine-readable evidence trails.
* **Phase 4 (ML Outlier Detection)**: Scikit-learn Isolation Forest detects unusual patterns across transaction ratios, settlement delays, and volume shifts.
* **Phase 5 (Groq AI Investigator)**: Groq LLM (`llama-3.3-70b-versatile`) receives **only structured verified facts** emitted by the deterministic engine and formats transparent explanations with strict hallucination controls.

---

## 2. Core AI Principles
- **No Hallucinations**: The LLM never invents financial figures, fees, or taxes.
- **Evidence-First**: The LLM only receives verified structured facts computed by the deterministic backend.
- **Confidence Scoring**: Confidence drops when records are missing or contradictory.
- **Human Review Safeguard**: Unexplainable discrepancies are marked `HUMAN_REVIEW_REQUIRED` rather than generating speculative explanations.
