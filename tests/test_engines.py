import pytest
from core.shortlist_engine import ShortlistEngine
from core.skill_matcher import SkillMatcher
from core.jd_matcher import JDMatcher

def test_shortlist_engine_strong():
    """Test Case: All metrics strong should return Strong Shortlist."""
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(85, 88, 82)
    assert label == "Strong Shortlist"
    assert composite >= 75
    assert statuses["Composite"] == "Good"

def test_shortlist_engine_ats_problem():
    """Test Case: Low ATS but others high should flag ATS improvement."""
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(45, 80, 75)
    assert label == "Needs ATS Improvement"
    assert weakest == "ATS Score"

def test_shortlist_engine_jd_match_problem():
    """Test Case: Low JD Match should flag alignment needed."""
    # Composite: 0.35*80 + 0.4*50 + 0.25*75 = 28 + 20 + 18.75 = 66.75 (Moderate)
    composite, label, weakest, score, statuses = ShortlistEngine.calculate(80, 50, 75)
    assert label == "Needs Better Job Alignment"
    assert weakest == "JD Match"

def test_skill_matcher_alias():
    """Test Case: Skill matcher should normalize aliases (sklearn -> Scikit-Learn)."""
    matcher = SkillMatcher()
    resume_text = "I have experience with sklearn and tf."
    jd_text = "Required: Scikit-Learn and TensorFlow."
    
    # Manually check normalization/extraction logic
    # Note: SkillMatcher needs role_skills.json to exist
    pct, matched, missing = matcher.match(resume_text, jd_text, "Data Scientist")
    
    # Both "sklearn" and "tf" should be normalized and matched
    assert any("Scikit-Learn" in s for s in matched)
    assert any("TensorFlow" in s for s in matched)

def test_jd_matcher_similarity():
    """Test Case: JD Matcher should return higher score for similar text."""
    from core.preprocess import Preprocessor
    prep = Preprocessor()
    matcher = JDMatcher()
    
    resume = prep.clean_text("I am a Python Developer with Flask and Django experience.")
    jd_similar = prep.clean_text("Looking for a Python Developer who knows Flask and web frameworks like Django.")
    jd_different = prep.clean_text("Hiring a Marketing Manager specialized in social media and SEO.")
    
    score_similar = matcher.calculate_match(resume, jd_similar)
    score_different = matcher.calculate_match(resume, jd_different)
    
    assert score_similar > score_different
    assert score_similar > 0
