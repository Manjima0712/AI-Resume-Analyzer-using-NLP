import json
import re


class SkillMatcher:
    """
    Skill matcher with alias/synonym support and JD-weighted matching.

    How it works:
    1.  Each entry in role_skills.json is treated as a canonical skill name.
    2.  An ALIAS_MAP maps alternative spellings/names to the canonical skill.
    3.  required skills = role skills ∪ skills found in the JD.
    4.  Skills found only in the JD get a lower weight (0.5) when computing
        the match %, because they may not all be truly required.
    5.  Returns match_pct, sorted matched list, sorted missing list.
    """

    # ── Alias / synonym map ───────────────────────────────────────────────────
    # Key = alias found in resume/JD text   →   Value = canonical skill name
    ALIAS_MAP = {
        # Python ecosystem
        "scikit learn":     "Scikit-Learn",
        "sklearn":          "Scikit-Learn",
        "scikit-learn":     "Scikit-Learn",
        "tf":               "TensorFlow",
        "tensorflow":       "TensorFlow",
        "torch":            "PyTorch",
        "pytorch":          "PyTorch",
        "keras":            "TensorFlow",          # Keras is now bundled with TF
        "numpy":            "NumPy",
        "np":               "NumPy",
        "pandas":           "Pandas",
        "pd":               "Pandas",
        "spacy":            "spaCy",
        "hugging face":     "HuggingFace",
        "huggingface":      "HuggingFace",
        "transformers":     "HuggingFace",

        # Web frameworks
        "django rest framework": "REST API",
        "drf":              "REST API",
        "restful":          "REST API",
        "rest":             "REST API",
        "graphql":          "REST API",
        "express":          "Express.js",
        "expressjs":        "Express.js",
        "nextjs":           "Next.js",
        "next js":          "Next.js",
        "vuejs":            "Vue",
        "vue.js":           "Vue",
        "angularjs":        "Angular",
        "reactjs":          "React",
        "react.js":         "React",

        # Database
        "postgres":         "PostgreSQL",
        "postgresql":       "PostgreSQL",
        "mysql":            "MySQL",
        "mongodb":          "MongoDB",
        "mongo":            "MongoDB",
        "mssql":            "SQL Server",
        "microsoft sql":    "SQL Server",
        "nosql":            "NoSQL",
        "redis":            "Redis",
        "elasticsearch":    "Elasticsearch",
        "elastic search":   "Elasticsearch",

        # Cloud / DevOps
        "amazon web services": "AWS",
        "gcp":              "GCP",
        "google cloud":     "GCP",
        "azure":            "Azure",
        "k8s":              "Kubernetes",
        "kubectl":          "Kubernetes",
        "helm":             "Kubernetes",
        "terraform":        "Terraform",
        "ansible":          "Ansible",
        "ci/cd":            "CI/CD",
        "cicd":             "CI/CD",
        "ci cd":            "CI/CD",
        "github actions":   "CI/CD",
        "gitlab ci":        "GitLab CI",
        "jenkins":          "Jenkins",
        "prometheus":       "Monitoring",
        "grafana":          "Monitoring",

        # Languages
        "c++":              "C++",
        "cpp":              "C++",
        "c#":               "C#",
        "csharp":           "C#",
        "js":               "JavaScript",
        "typescript":       "TypeScript",
        "ts":               "TypeScript",
        "bash":             "Bash",
        "shell":            "Bash",
        "shell script":     "Bash",
        "golang":           "Go",
        "go lang":          "Go",
        "kotlin":           "Kotlin",
        "swift":            "Swift",
        "r language":       "R",

        # Data / BI
        "power bi":         "Power BI",
        "powerbi":          "Power BI",
        "tableau":          "Tableau",
        "ms excel":         "Excel",
        "microsoft excel":  "Excel",
        "a/b test":         "A/B Testing",
        "ab testing":       "A/B Testing",
        "apache spark":     "Spark",
        "pyspark":          "Spark",
        "big query":        "BigQuery",
        "bigquery":         "BigQuery",

        # Testing
        "selenium webdriver": "Selenium",
        "playwright":       "Selenium",
        "cypress":          "Cypress",
        "postman":          "Postman",
        "junit":            "JUnit",
        "testng":           "TestNG",
        "manual test":      "Manual Testing",
        "automation test":  "Automation Testing",
        "api test":         "API Testing",

        # Design / UX
        "figma":            "Figma",
        "adobe xd":         "Adobe XD",
        "invision":         "Prototyping",
        "ux research":      "User Research",
        "usability":        "Usability Testing",
        "wireframe":        "Wireframing",

        # Misc
        "agile scrum":      "Agile",
        "scrum":            "Agile",
        "kanban":           "Agile",
        "jira":             "JIRA",
        "confluence":       "JIRA",
        "mlops":            "MLOps",
        "ml ops":           "MLOps",
        "model deploy":     "Model Deployment",
        "docker":           "Docker",
        "linux":            "Linux",
        "unix":             "Linux",
        "git":              "Git",
        "github":           "Git",
        "bitbucket":        "Git",
    }

    def __init__(self, role_skills_file='data/role_skills.json'):
        self.role_skills = {}
        # Pre-compile alias regex patterns once for speed
        self._alias_patterns = {
            re.compile(r'\b' + re.escape(alias) + r'\b', re.IGNORECASE): canonical
            for alias, canonical in self.ALIAS_MAP.items()
        }
        try:
            with open(role_skills_file, 'r') as f:
                self.role_skills = json.load(f)
        except Exception as e:
            print(f"Could not load role_skills.json: {e}")

    def _normalise_text(self, text):
        """
        Return a copy of `text` where every known alias phrase has been
        replaced by its canonical skill name — making subsequent exact-match
        searches far more reliable.
        """
        for pattern, canonical in self._alias_patterns.items():
            text = pattern.sub(canonical, text)
        return text

    def get_role_skills(self, target_role):
        return self.role_skills.get(target_role, [])

    def extract_skills_from_text(self, text, all_skills):
        """
        Match canonical skill names against normalised text.
        Uses whole-word, case-insensitive matching.
        """
        text_norm = self._normalise_text(text)
        text_lower = text_norm.lower()
        found = []
        for skill in all_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
        return found

    def match(self, resume_text, jd_text, target_role):
        """
        Calculates Skill Match % with alias normalisation and JD weighting.

        - Role-required skills count with full weight (1.0).
        - JD-only skills count with half weight (0.5) to avoid unfair penalisation
          when a JD lists many niche extras that aren't truly required.

        Returns: match_percentage (float), matched_skills (list), missing_skills (list)
        """
        role_skills = set(self.get_role_skills(target_role))

        # Skills mentioned in JD drawn from the full known universe + normalization
        all_known_skills = list({
            skill for skills in self.role_skills.values() for skill in skills
        })
        jd_norm  = self._normalise_text(jd_text)
        jd_skills = set(self.extract_skills_from_text(jd_norm, all_known_skills))

        # JD-only skills (not in the role baseline)
        jd_only_skills = jd_skills - role_skills

        # Combined set for matching
        required_skills = role_skills | jd_skills

        if not required_skills:
            return 0.0, [], []

        resume_norm   = self._normalise_text(resume_text)
        resume_skills = set(self.extract_skills_from_text(resume_norm, list(required_skills)))

        matched = sorted(resume_skills)
        missing = sorted(required_skills - resume_skills)

        # Weighted score: role skills = 1.0 pt, JD-only skills = 0.5 pt
        total_weight = len(role_skills) + 0.5 * len(jd_only_skills)
        if total_weight == 0:
            return 0.0, matched, missing

        earned_weight = sum(
            1.0 if skill in role_skills else 0.5
            for skill in resume_skills
        )

        match_pct = round(min(100.0, (earned_weight / total_weight) * 100), 2)
        return match_pct, matched, missing
