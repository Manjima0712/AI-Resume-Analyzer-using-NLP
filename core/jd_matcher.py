import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Extended stop words for missing keyword detection
_IGNORE_WORDS = {
    'this', 'that', 'with', 'from', 'have', 'your', 'will', 'they', 'what',
    'about', 'some', 'also', 'their', 'there', 'which', 'would', 'been',
    'such', 'more', 'like', 'than', 'each', 'work', 'team', 'join', 'must',
    'using', 'skills', 'role', 'year', 'years', 'experience', 'strong',
    'good', 'knowledge', 'looking', 'candidate', 'required', 'preferred',
    'including', 'ensure', 'need', 'should', 'make', 'across', 'other',
    'related', 'based', 'multiple', 'within', 'between', 'both', 'able',
    'various', 'plus', 'well', 'good', 'great', 'best', 'ideal'
}


class JDMatcher:
    def __init__(self, keywords_file='data/jd_keywords.json'):
        self.action_verbs = []
        self.role_keywords = {}
        self.tools_and_tech = []
        try:
            with open(keywords_file, 'r') as f:
                data = json.load(f)
                self.action_verbs   = [w.lower() for w in data.get('action_verbs', [])]
                self.tools_and_tech = [w.lower() for w in data.get('tools_and_tech', [])]
                self.role_keywords  = {
                    role: [kw.lower() for kw in kws]
                    for role, kws in data.get('role_keywords', {}).items()
                }
        except Exception as e:
            print(f"Could not load JD keywords: {e}")

    # ── Core TF-IDF match ──────────────────────────────────────────────────────
    def calculate_match(self, cleaned_resume: str, cleaned_jd: str) -> float:
        """TF-IDF + Cosine Similarity. Returns score 0–100."""
        if not cleaned_jd or not cleaned_resume:
            return 0.0
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))   # bigrams improve multi-word skill matching
        try:
            tfidf = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
            score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return round(min(score * 100, 100), 2)
        except Exception:
            return 0.0

    # ── Missing Keyword Detection ──────────────────────────────────────────────
    def find_missing_keywords(self, resume_lower: str, jd_lower: str,
                              target_role: str = None) -> list:
        """
        Identify important JD keywords absent from the resume.

        Priority order:
          1. Role-specific benchmark keywords (from role_keywords in JSON)
          2. Tech tools mentioned in the JD but not in the resume
          3. Action verbs from the JD missing from the resume
        """
        if not jd_lower:
            return []

        resume_words = set(re.findall(r'\b[a-z][a-z0-9+#./]{2,}\b', resume_lower))
        jd_words     = set(re.findall(r'\b[a-z][a-z0-9+#./]{2,}\b', jd_lower))
        jd_words    -= _IGNORE_WORDS
        missing_raw  = jd_words - resume_words

        # 1. Role benchmark keywords
        role_missing = []
        if target_role and target_role in self.role_keywords:
            role_kws = set(self.role_keywords[target_role])
            role_missing = sorted(role_kws - resume_words)

        # 2. Tech keywords found in JD but absent from resume
        tech_missing = sorted(w for w in missing_raw if w in self.tools_and_tech)

        # 3. Action verbs
        verb_missing = sorted(w for w in missing_raw if w in self.action_verbs)

        # 4. General important JD words (length ≥ 5, not stop words)
        general_missing = sorted(
            w for w in missing_raw
            if len(w) >= 5
            and w not in self.action_verbs
            and w not in self.tools_and_tech
        )[:8]

        # Merge, deduplicate, cap at 20 results total
        seen = set()
        result = []
        for kw in (role_missing + tech_missing + verb_missing + general_missing):
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
            if len(result) >= 20:
                break

        return result
