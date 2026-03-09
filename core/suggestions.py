class SuggestionsEngine:

    # ── Per-metric improvement text ────────────────────────────────────────────
    _IMPROVEMENT = {
        "JD Match": (
            "Resume is not sufficiently tailored to the job description. "
            "Add role-specific keywords, match the tools and technologies mentioned in the JD, "
            "and align your project descriptions with the target role's language."
        ),
        "ATS Score": (
            "Resume may not pass ATS filters due to formatting or missing sections. "
            "Use a clean layout with standard headings (Summary, Skills, Education, "
            "Projects, Experience, Certifications), clear bullet points, and complete contact details."
        ),
        "Skills Match": (
            "Resume lacks key technical skills required for the role. "
            "Add missing skills you genuinely possess and prove them through project "
            "or experience descriptions — not just a skills list."
        ),
    }

    @staticmethod
    def _improvement_for(metric):
        return SuggestionsEngine._IMPROVEMENT.get(
            metric, "Improve the resume overall before applying."
        )

    # ── Main entry point ──────────────────────────────────────────────────────
    @staticmethod
    def generate(
        target_role, missing_skills, missing_keywords, missing_sections,
        skill_match, jd_match, ats_score,
        shortlist_score, shortlist_label, weakest_metric, weakest_score
    ):
        """
        Returns a structured dict:
            jd_match         – per-metric suggestion string
            ats_score        – per-metric suggestion string
            skills_match     – per-metric suggestion string
            composite_score  – per-metric suggestion string
            recommendation   – label-driven, weakest-metric-aware suggestion
            weakest_metric   – name of the weakest metric
            weakest_improve  – specific improvement text for the weakest metric
            tips             – list of detailed actionable bullets
        """

        # ── 1. JD Match suggestion ─────────────────────────────────────────────
        if jd_match >= 80:
            jd_suggestion = (
                "Strong JD alignment. Fine-tune keyword placement in your summary "
                "and project descriptions to maintain a high match."
            )
        elif jd_match >= 60:
            jd_suggestion = (
                "Partial JD alignment. Add more role-specific keywords — especially in "
                "your summary, skills, and project sections — using the exact terms from the JD."
            )
        else:
            jd_suggestion = (
                "Low JD alignment. Tailor your summary, skills, and project descriptions "
                "to mirror the language and keywords in the JD. Remove unrelated content."
            )
        if missing_keywords:
            top_kw = [kw.title() for kw in missing_keywords[:5]]
            jd_suggestion += f"  Missing terms: {', '.join(top_kw)}."

        # ── 2. ATS Score suggestion ────────────────────────────────────────────
        if ats_score >= 80:
            ats_suggestion = (
                "Resume is ATS-friendly. Ensure contact details are complete "
                "and section headings are standard."
            )
        elif ats_score >= 60:
            ats_suggestion = (
                "Moderate ATS compatibility. Add standard headings "
                "(Summary, Skills, Education, Projects, Experience, Certifications), "
                "clear bullet points, and complete contact information."
            )
        else:
            ats_suggestion = (
                "Poor ATS compatibility. Use a simple, clean layout with standard "
                "section headings and bullet points. Avoid tables, icons, and complex design. "
                "Add complete contact details (email + phone)."
            )
        if missing_sections:
            ats_suggestion += f"  Missing sections: {', '.join(missing_sections)}."

        # ── 3. Skills Match suggestion ─────────────────────────────────────────
        if skill_match >= 80:
            skills_suggestion = (
                "Strong skill match. Demonstrate each skill through quantified "
                "project outcomes for maximum impact."
            )
        elif skill_match >= 55:
            skills_suggestion = (
                "Partial skill match. Add missing role-specific skills and show "
                "their practical application in project or experience descriptions."
            )
        else:
            skills_suggestion = (
                "Weak skill match. Add missing skills from the JD (only those you "
                "genuinely have) and back each one with a concrete project or experience example."
            )
        if missing_skills:
            top_sk = missing_skills[:5]
            skills_suggestion += f"  Key missing skills: {', '.join(top_sk)}."

        # ── 4. Composite Score suggestion ──────────────────────────────────────
        if shortlist_score >= 75:
            composite_suggestion = (
                "Strong overall profile. Add quantified achievements and ensure "
                "all three score areas remain high."
            )
        elif shortlist_score >= 65:
            composite_suggestion = (
                f"Moderate overall profile. Focus improvement on your weakest area: "
                f"**{weakest_metric}** ({weakest_score:.0f}). "
                "Improving it will have the biggest single impact on your composite score."
            )
        else:
            composite_suggestion = (
                f"Weak overall profile. Your biggest drag is **{weakest_metric}** "
                f"({weakest_score:.0f}). Address ATS formatting, JD keyword alignment, "
                "and role-specific skill coverage together."
            )

        # ── 5. Recommendation — driven by weakest metric ───────────────────────
        if shortlist_label == "Strong Shortlist":
            recommendation_suggestion = (
                "Resume is well optimised and has a strong shortlist chance. "
                "Minor improvements: add measurable achievements and optimise keyword placement."
            )
        elif shortlist_label in ("Needs ATS Improvement",):
            recommendation_suggestion = (
                "Resume may not pass ATS screening due to formatting or missing sections. "
                + SuggestionsEngine._improvement_for("ATS Score")
            )
        elif shortlist_label in ("Needs Better Job Alignment",):
            recommendation_suggestion = (
                "Resume is not sufficiently tailored to the job description. "
                + SuggestionsEngine._improvement_for("JD Match")
            )
        elif shortlist_label in ("Needs Skill Alignment",):
            recommendation_suggestion = (
                "Resume lacks key skills required for the role. "
                + SuggestionsEngine._improvement_for("Skills Match")
            )
        elif shortlist_label == "Low Shortlist Chance":
            recommendation_suggestion = (
                "Resume needs major improvement before applying. "
                f"Start with the weakest area — {weakest_metric} — then improve "
                "ATS structure, JD alignment, and skill relevance together."
            )
        else:  # Moderate Match
            recommendation_suggestion = (
                f"Resume has potential but needs targeted improvements. "
                f"Main area to fix: **{weakest_metric}** ({weakest_score:.0f}).  "
                + SuggestionsEngine._improvement_for(weakest_metric)
            )

        # ── 6. Detailed tips list ──────────────────────────────────────────────
        tips = []

        for section in missing_sections:
            if section in ('Summary', 'Objective'):
                tips.append(
                    f"Add a Professional Summary. Example: '{target_role} with hands-on "
                    "experience in [tools], seeking to contribute to [domain].'"
                )
            elif section == 'Skills':
                tips.append("Add a dedicated 'Skills' section listing relevant tools, languages, and frameworks.")
            elif section == 'Projects':
                tips.append(
                    "Add a 'Projects' section with name, tools used, and measurable impact. "
                    "Example: 'Django web app serving 100+ users with CRUD operations.'"
                )
            elif section == 'Experience':
                tips.append("Add an 'Experience' section with action-verb bullet points for each role.")
            elif section == 'Certifications':
                tips.append("List relevant online certifications (Coursera, Google, AWS, etc.).")
            elif section == 'Email':
                tips.append("Add your professional email to the resume header.")
            elif section == 'Phone Number':
                tips.append("Add your phone number to the contact section.")

        if missing_skills:
            tips.append(
                f"Add these missing skills (only if genuine): {', '.join(missing_skills[:6])}. "
                "Back each skill with a project or experience example."
            )

        if missing_keywords:
            top_kw = [kw.title() for kw in missing_keywords[:5]]
            tips.append(
                f"Include these JD keywords to improve ATS matching: {', '.join(top_kw)}. "
                "Use the exact terminology from the job description."
            )

        # Always add the specific improvement for the weakest metric first
        tips.insert(0, f"🎯 Priority fix ({weakest_metric}): " + SuggestionsEngine._improvement_for(weakest_metric))

        tips.append("Use standard section headings: Summary, Skills, Education, Projects, Experience, Certifications.")
        tips.append(
            "Add measurable impact to projects. Instead of 'Built a web app', write: "
            "'Built a Flask REST API handling 10K requests/day, reducing latency by 35%.'"
        )
        tips.append(f"Tailor this resume specifically for the '{target_role}' role — avoid mixing multiple targets.")

        return {
            "jd_match":          jd_suggestion,
            "ats_score":         ats_suggestion,
            "skills_match":      skills_suggestion,
            "composite_score":   composite_suggestion,
            "recommendation":    recommendation_suggestion,
            "weakest_metric":    weakest_metric,
            "weakest_improve":   SuggestionsEngine._improvement_for(weakest_metric),
            "tips":              tips,
        }
