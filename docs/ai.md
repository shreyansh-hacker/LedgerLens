# LedgerLens AI & Investigation Architecture

## Core AI Principles
- **No Hallucinations**: The LLM never invents financial figures, fees, or taxes.
- **Evidence-First**: The LLM only receives verified structured facts computed by the deterministic backend.
- **Confidence Scoring**: Confidence drops when records are missing or contradictory.
- **Human Review Safeguard**: Unexplainable discrepancies are marked `HUMAN_REVIEW_REQUIRED` rather than generating speculative explanations.

*(Detailed prompt templates and guardrail specifications will be documented in Phase 5)*
