from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class AnalysisResult(db.Model):
    """Stores data from a single-resume analysis (Analyzer page)."""
    __tablename__ = 'analysis_results'

    id              = db.Column(db.Integer, primary_key=True)
    filename        = db.Column(db.String(255), nullable=False)
    target_role     = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    ats_score       = db.Column(db.Float, nullable=False)
    jd_match        = db.Column(db.Float, nullable=False)
    skill_match     = db.Column(db.Float, nullable=False)
    composite_score = db.Column(db.Float, nullable=False)
    recommendation  = db.Column(db.String(100), nullable=False)
    weakest_metric  = db.Column(db.String(50))
    missing_skills  = db.Column(db.Text)     # stored as JSON list
    missing_keywords = db.Column(db.Text)    # stored as JSON list
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def set_missing_skills(self, skills_list):
        self.missing_skills = json.dumps(skills_list or [])

    def get_missing_skills(self):
        return json.loads(self.missing_skills or '[]')

    def set_missing_keywords(self, kw_list):
        self.missing_keywords = json.dumps(kw_list or [])

    def get_missing_keywords(self):
        return json.loads(self.missing_keywords or '[]')

    def to_dict(self):
        return {
            'id':             self.id,
            'filename':       self.filename,
            'target_role':    self.target_role,
            'ats_score':      self.ats_score,
            'jd_match':       self.jd_match,
            'skill_match':    self.skill_match,
            'composite_score': self.composite_score,
            'recommendation': self.recommendation,
            'weakest_metric': self.weakest_metric,
            'created_at':     self.created_at.strftime('%Y-%m-%d %H:%M'),
        }


class RankingBatch(db.Model):
    """Groups a set of RankingResult rows from one Ranker submission."""
    __tablename__ = 'ranking_batches'

    id              = db.Column(db.Integer, primary_key=True)
    target_role     = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    results         = db.relationship('RankingResult', backref='batch',
                                       cascade='all, delete-orphan',
                                       lazy=True, order_by='RankingResult.rank')


class RankingResult(db.Model):
    """Stores one candidate row from a bulk ranking session."""
    __tablename__ = 'ranking_results'

    id              = db.Column(db.Integer, primary_key=True)
    batch_id        = db.Column(db.Integer, db.ForeignKey('ranking_batches.id'), nullable=False)
    rank            = db.Column(db.Integer, nullable=False)
    filename        = db.Column(db.String(255), nullable=False)
    ats_score       = db.Column(db.Float, nullable=False)
    jd_match        = db.Column(db.Float, nullable=False)
    skill_match     = db.Column(db.Float, nullable=False)
    composite_score = db.Column(db.Float, nullable=False)
    recommendation  = db.Column(db.String(100), nullable=False)
    weakest_metric  = db.Column(db.String(50))
