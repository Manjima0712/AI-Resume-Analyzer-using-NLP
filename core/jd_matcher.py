import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class JDMatcher:
    def __init__(self, keywords_file='data/jd_keywords.json'):
        self.action_verbs = []
        try:
            with open(keywords_file, 'r') as f:
                data = json.load(f)
                self.action_verbs = data.get('action_verbs', [])
        except Exception as e:
            print(f"Could not load JD keywords: {e}")

    def calculate_match(self, cleaned_resume, cleaned_jd):
        """
        Uses TF-IDF + Cosine Similarity to compare full resume text with full JD text.
        Returns percentage (0-100).
        """
        if not cleaned_jd:
            return 0.0 # If no JD is provided, JD match is 0. Wait, should probably prompt user to provide JD.
            
        if not cleaned_resume:
            return 0.0
            
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 2)
        except Exception:
            return 0.0
            
    def find_missing_keywords(self, resume_lower, jd_lower):
        """Find important words in JD that are missing from the resume."""
        if not jd_lower:
            return []
            
        jd_words = set(re.findall(r'\b[a-z]{4,}\b', jd_lower))
        resume_words = set(re.findall(r'\b[a-z]{4,}\b', resume_lower))
        
        # Simple stopword ignoring
        ignore = {'this', 'that', 'with', 'from', 'have', 'your', 'will', 'they', 'what', 'about'}
        jd_words = jd_words - ignore
        
        missing = list(jd_words - resume_words)
        
        # Prioritize matching against known action verbs or technical jargon
        important_missing = [w for w in missing if w in self.action_verbs]
        other_missing = [w for w in missing if w not in self.action_verbs][:10] # cap
        
        return important_missing + other_missing
