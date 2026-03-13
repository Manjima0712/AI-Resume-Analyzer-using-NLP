class Ranker:
    @staticmethod
    def rank_resumes(results):
        """Rank a list of resume result dicts by their shortlist_score (descending)."""
        return sorted(results, key=lambda x: x.get('shortlist_score', 0), reverse=True)
