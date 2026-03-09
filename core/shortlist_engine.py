class ShortlistEngine:

    # ── score thresholds ───────────────────────────────────────────────────────
    STRONG_COMPOSITE   = 75
    STRONG_MIN_SCORE   = 70   # every individual metric must be at least this
    MODERATE_COMPOSITE = 65

    @staticmethod
    def _score_status(value, good=75, ok=60):
        """Return 'Good', 'Moderate', or 'Low' for a numeric score."""
        if value >= good:
            return "Good"
        elif value >= ok:
            return "Moderate"
        return "Low"

    @staticmethod
    def calculate(ats_score, jd_match, skill_match):
        """
        Comparison-based shortlist engine.

        1. Computes composite score: 0.40*JD + 0.35*ATS + 0.25*Skills
        2. Identifies the single weakest metric.
        3. Derives the recommendation label from a combination of composite
           threshold AND which metric is dragging the profile down.

        Returns:
            shortlist_score  – float, composite score 0-100
            shortlist_label  – str, human-readable recommendation
            weakest_metric   – str, name of the worst-performing metric
            weakest_score    – float, its value
            score_statuses   – dict {metric: 'Good'|'Moderate'|'Low'}
        """
        composite = round(
            (0.40 * jd_match) + (0.35 * ats_score) + (0.25 * skill_match), 1
        )

        score_map = {
            "JD Match":    jd_match,
            "ATS Score":   ats_score,
            "Skills Match": skill_match,
        }

        weakest_metric = min(score_map, key=score_map.get)
        weakest_score  = score_map[weakest_metric]

        score_statuses = {
            "JD Match":     ShortlistEngine._score_status(jd_match,  good=75, ok=60),
            "ATS Score":    ShortlistEngine._score_status(ats_score, good=75, ok=60),
            "Skills Match": ShortlistEngine._score_status(skill_match, good=70, ok=55),
            "Composite":    ShortlistEngine._score_status(composite, good=75, ok=65),
        }

        # ── Recommendation label ──────────────────────────────────────────────
        # Case 1 – ALL metrics are genuinely strong
        if composite >= ShortlistEngine.STRONG_COMPOSITE and \
           min(score_map.values()) >= ShortlistEngine.STRONG_MIN_SCORE:
            label = "Strong Shortlist"

        # Case 2–4 – composite is moderate/weak → let the weakest metric decide
        elif composite >= ShortlistEngine.MODERATE_COMPOSITE:
            if weakest_metric == "ATS Score" and weakest_score < 70:
                label = "Needs ATS Improvement"
            elif weakest_metric == "JD Match" and weakest_score < 70:
                label = "Needs Better Job Alignment"
            elif weakest_metric == "Skills Match" and weakest_score < 65:
                label = "Needs Skill Alignment"
            else:
                label = "Moderate Match"

        # Case 5 – composite is too low regardless
        else:
            label = "Low Shortlist Chance"

        return composite, label, weakest_metric, weakest_score, score_statuses
