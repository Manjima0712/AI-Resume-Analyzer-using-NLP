"""
test_engines.py — Unit tests for core NLP and ML engines.
Run with: python -m pytest tests/ -v
"""
import pytest
from core.shortlist_engine import ShortlistEngine
from core.skill_matcher import SkillMatcher

# ── ShortlistEngine tests ─────────────────────────────────────────────────────

def test_shortlist_engine_strong():
    """All metrics strong → Strong Shortlist."""
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(85, 88, 82)
    assert label == "Strong Shortlist"
    assert composite >= 75
    assert statuses["Composite"] == "Good"

def test_shortlist_engine_ats_problem():
    """Low ATS score → Needs ATS Improvement."""
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(45, 80, 75)
    assert label == "Needs ATS Improvement"
    assert weakest == "ATS Score"

def test_shortlist_engine_jd_match_problem():
    """Low JD Match → Needs Better Job Alignment."""
    # composite = 0.40*50 + 0.35*80 + 0.25*75 = 20 + 28 + 18.75 = 66.75 — Moderate range
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(80, 50, 75)
    assert label == "Needs Better Job Alignment"
    assert weakest == "JD Match"

def test_shortlist_engine_skills_problem():
    """Low Skills Match → Needs Skill Alignment."""
    # composite = 0.40*78 + 0.35*80 + 0.25*50 = 31.2 + 28 + 12.5 = 71.7 — Moderate range
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(80, 78, 50)
    assert label == "Needs Skill Alignment"
    assert weakest == "Skills Match"

def test_shortlist_engine_all_weak():
    """All weak scores → Low Shortlist Chance."""
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(55, 50, 45)
    assert label == "Low Shortlist Chance"
    assert composite < 65

def test_shortlist_engine_returns_five_values():
    """calculate() must always return exactly 5 values."""
    result = ShortlistEngine.calculate(70, 65, 60)
    assert len(result) == 5

def test_shortlist_score_statuses_keys():
    """score_statuses dict must contain expected keys."""
    _, _, _, _, statuses = ShortlistEngine.calculate(70, 65, 60)
    assert set(statuses.keys()) == {"JD Match", "ATS Score", "Skills Match", "Composite"}

def test_shortlist_score_capped():
    """Composite score must never exceed 100."""
    composite, _, _, _, _ = ShortlistEngine.calculate(100, 100, 100)
    assert composite <= 100

# ── SkillMatcher alias tests ──────────────────────────────────────────────────

def test_skill_matcher_alias_sklearn():
    """'sklearn' in resume should match 'Scikit-Learn' canonical name."""
    matcher = SkillMatcher()
    pct, matched, _ = matcher.match(
        "Experienced with sklearn for classification tasks.",
        "Must know Scikit-Learn and Python.",
        "Data Scientist"
    )
    assert any("Scikit-Learn" in s for s in matched)

def test_skill_matcher_alias_tf():
    """'tf' in resume should resolve to TensorFlow."""
    matcher = SkillMatcher()
    pct, matched, _ = matcher.match(
        "Built neural networks using tf and keras.",
        "Experience with TensorFlow required.",
        "ML Engineer"
    )
    assert any("TensorFlow" in s for s in matched)

def test_skill_matcher_alias_k8s():
    """'k8s' in resume should resolve to Kubernetes."""
    matcher = SkillMatcher()
    pct, matched, _ = matcher.match(
        "Deployed containers on k8s clusters.",
        "Kubernetes experience required.",
        "DevOps Engineer"
    )
    assert any("Kubernetes" in s for s in matched)

def test_skill_matcher_returns_three_values():
    """match() must always return (pct, matched, missing)."""
    matcher = SkillMatcher()
    result = matcher.match("Some resume", "Some JD", "Python Developer")
    assert len(result) == 3

def test_skill_matcher_score_in_range():
    """Score must be between 0 and 100."""
    matcher = SkillMatcher()
    pct, _, _ = matcher.match("Python Flask Django REST API", "Python developer needed", "Python Developer")
    assert 0.0 <= pct <= 100.0

# ── DB Model tests ────────────────────────────────────────────────────────────

def test_analysis_result_insert(db_session):
    """AnalysisResult should be insertable and retrievable."""
    from models import AnalysisResult
    from sqlalchemy import select
    r = AnalysisResult(
        filename="test.pdf",
        target_role="Data Scientist",
        job_description="Build ML models.",
        ats_score=78.0,
        jd_match=65.5,
        skill_match=60.0,
        composite_score=69.0,
        recommendation="Moderate Match",
        weakest_metric="Skills Match",
    )
    r.set_missing_skills(["PyTorch", "Spark"])
    r.set_missing_keywords(["neural network"])
    db_session.session.add(r)
    db_session.session.commit()

    fetched = db_session.session.execute(select(AnalysisResult)).scalars().first()
    assert fetched is not None
    assert fetched.recommendation == "Moderate Match"
    assert "PyTorch" in fetched.get_missing_skills()

def test_ranking_batch_and_results_insert(db_session):
    """RankingBatch with RankingResult rows should save and relate correctly."""
    from models import RankingBatch, RankingResult
    from sqlalchemy import select
    batch = RankingBatch(target_role="ML Engineer", job_description="ML JD")
    db_session.session.add(batch)
    db_session.session.flush()

    for i in range(3):
        row = RankingResult(
            batch_id=batch.id,
            rank=i + 1,
            filename=f"candidate_{i+1}.pdf",
            ats_score=80.0 - i * 5,
            jd_match=75.0,
            skill_match=70.0,
            composite_score=76.0 - i * 3,
            recommendation="Moderate Match",
            weakest_metric="Skills Match",
        )
        db_session.session.add(row)
    db_session.session.commit()

    saved = db_session.session.get(RankingBatch, batch.id)
    assert saved is not None
    assert len(saved.results) == 3
    assert saved.results[0].rank == 1
