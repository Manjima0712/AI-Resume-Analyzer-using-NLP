import re

class ATSChecker:
    @staticmethod
    def evaluate(resume_text):
        """
        Rule-based ATS scoring engine out of 100 points based on section presence.
        Returns: ats_score, feedback_list, missing_sections
        """
        score = 0
        feedback = []
        missing_sections = []
        
        if not resume_text:
            return 0, ["Add text to your resume."], ["All Sections"]
            
        resume_lower = resume_text.lower()
        
        # 1. Formatting & Length (10 points)
        word_count = len(resume_text.split())
        if 300 <= word_count <= 1000:
            score += 10
            feedback.append("Resume length is optimal.")
        else:
            temp_score = min(10, max(0, 10 - abs(word_count - 500) // 100))
            score += temp_score
            feedback.append(f"Resume length is {word_count} words. Aim for 300-800 words.")

        # 2. Section Checks (70 points total -> roughly 10 pts per major section)
        sections = {
            'Summary': ['summary', 'objective', 'profile', 'about me'],
            'Skills': ['skills', 'technologies', 'technical skills', 'core competencies'],
            'Education': ['education', 'academic', 'degree', 'qualification'],
            'Projects': ['projects', 'personal projects', 'academic projects'],
            'Experience': ['experience', 'work history', 'employment', 'professional experience'],
            'Certifications': ['certifications', 'certificates', 'courses']
        }
        
        for section, keywords in sections.items():
            if any(kw in resume_lower for kw in keywords):
                if section in ['Summary', 'Skills', 'Education']:
                    score += 15
                elif section in ['Experience', 'Projects']:
                    score += 10
                else:
                    score += 5
            else:
                missing_sections.append(section)
                feedback.append(f"Missing '{section}' section.")
                
        # 3. Contact Info (20 points)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        phone_pattern = r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        
        if re.search(email_pattern, resume_text):
            score += 10
        else:
            missing_sections.append('Email')
            feedback.append("Missing email address.")
            
        if re.search(phone_pattern, resume_text):
            score += 10
        else:
            missing_sections.append('Phone Number')
            feedback.append("Missing phone number.")

        return min(100, score), feedback, missing_sections
