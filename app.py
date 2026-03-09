from flask import Flask, render_template, request, flash, redirect, url_for, Response, session
import os
import io
import csv
import threading
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from core.parser import ResumeParser
from core.preprocess import TextPreprocessor
from core.ats_checker import ATSChecker
from core.jd_matcher import JDMatcher
from core.skill_matcher import SkillMatcher
from core.shortlist_engine import ShortlistEngine
from core.suggestions import SuggestionsEngine
from core.ranker import Ranker

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_fallback_key_for_dev_only')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Background thread loading
preprocessor = None
jd_matcher = None
skill_matcher = None
services_loading_event = threading.Event()

def load_services_bg():
    global preprocessor, jd_matcher, skill_matcher
    print("Background thread: Initializing Core Services...")
    try:
        preprocessor = TextPreprocessor()
        jd_matcher = JDMatcher()
        skill_matcher = SkillMatcher()
    except Exception as e:
        print(f"Error loading services: {e}")
    finally:
        services_loading_event.set()
        print("Background thread: Services ready!")

threading.Thread(target=load_services_bg, daemon=True).start()

def get_services():
    if not services_loading_event.is_set():
        services_loading_event.wait()
    return preprocessor, jd_matcher, skill_matcher

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
TARGET_ROLES = [
    "Python Developer", "Data Analyst", "Data Scientist", "ML Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "QA Engineer", "UI/UX Developer"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def analyzer():
    if request.method == 'POST':
        target_role = request.form.get('target_role', '').strip()
        job_description = request.form.get('job_description', '').strip()

        if not target_role or not job_description:
            flash('Please select a Target Role and provide a Job Description.')
            return redirect(request.url)

        if 'resume' not in request.files:
            flash('No file uploaded.')
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                prep, jd_m, skill_m = get_services()

                # 1. Extract and clean text
                resume_text = ResumeParser.extract_text(file_path)
                cleaned_resume = prep.clean_text(resume_text)
                cleaned_jd = prep.clean_text(job_description)

                # 2. ATS Score & missing sections
                ats_score, ats_feedback, missing_sections = ATSChecker.evaluate(resume_text)

                # 3. JD Match Score
                jd_match = jd_m.calculate_match(cleaned_resume, cleaned_jd)
                missing_keywords = jd_m.find_missing_keywords(resume_text.lower(), job_description.lower())

                # 4. Skill Match
                skill_match, matched_skills, missing_skills = skill_m.match(resume_text, job_description, target_role)

                # 5. Shortlist Chance (comparison-based)
                shortlist_score, shortlist_label, weakest_metric, weakest_score, score_statuses = \
                    ShortlistEngine.calculate(ats_score, jd_match, skill_match)

                # 6. Suggestions — weakest-metric aware
                suggestions = SuggestionsEngine.generate(
                    target_role, missing_skills, missing_keywords,
                    missing_sections, skill_match, jd_match,
                    ats_score, shortlist_score, shortlist_label,
                    weakest_metric, weakest_score
                )

                os.remove(file_path)

                return render_template('analyzer.html',
                    roles=TARGET_ROLES,
                    target_role=target_role,
                    ats_score=ats_score,
                    jd_match=jd_match,
                    skill_match=skill_match,
                    shortlist_score=shortlist_score,
                    shortlist_label=shortlist_label,
                    weakest_metric=weakest_metric,
                    weakest_score=weakest_score,
                    score_statuses=score_statuses,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills[:8],
                    missing_keywords=[kw.title() for kw in missing_keywords[:8]],
                    missing_sections=missing_sections,
                    suggestions=suggestions
                )
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Only PDF, DOCX, and TXT allowed.')
            return redirect(request.url)

    return render_template('analyzer.html', roles=TARGET_ROLES)

@app.route('/ranker', methods=['GET', 'POST'])
def ranker():
    if request.method == 'POST':
        target_role = request.form.get('target_role', '').strip()
        job_description = request.form.get('job_description', '').strip()
        files = request.files.getlist('resumes')

        if not target_role or not job_description:
            flash('Please select a Target Role and provide a Job Description.')
            return redirect(request.url)

        if not files or files[0].filename == '':
            flash('No files selected.')
            return redirect(request.url)

        if len(files) > 20:
            flash('Maximum 20 resumes allowed.')
            return redirect(request.url)

        prep, jd_m, skill_m = get_services()
        cleaned_jd = prep.clean_text(job_description)
        results = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                try:
                    resume_text = ResumeParser.extract_text(file_path)
                    cleaned_resume = prep.clean_text(resume_text)

                    ats_score, _, _ = ATSChecker.evaluate(resume_text)
                    jd_match = jd_m.calculate_match(cleaned_resume, cleaned_jd)
                    skill_match, _, _ = skill_m.match(resume_text, job_description, target_role)
                    shortlist_score, shortlist_label, weakest_metric, _, _ = \
                        ShortlistEngine.calculate(ats_score, jd_match, skill_match)

                    results.append({
                        'filename': filename,
                        'ats_score': ats_score,
                        'jd_match': jd_match,
                        'skill_match': skill_match,
                        'shortlist_score': shortlist_score,
                        'shortlist_label': shortlist_label,
                        'weakest_metric': weakest_metric,
                    })
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

        ranked = Ranker.rank_resumes(results)
        # Cache for CSV export (store only serialisable data)
        session['last_ranker_results'] = ranked
        session['last_ranker_role'] = target_role
        return render_template('ranker.html', roles=TARGET_ROLES, results=ranked,
                               target_role=target_role, jd_provided=bool(job_description))

    return render_template('ranker.html', roles=TARGET_ROLES)


@app.route('/ranker/export')
def ranker_export():
    """Stream the last ranker results as a downloadable CSV file."""
    results = session.get('last_ranker_results', [])
    role = session.get('last_ranker_role', 'results')

    if not results:
        flash('No ranker results to export. Please rank resumes first.')
        return redirect(url_for('ranker'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Candidate', 'ATS Score', 'JD Match (%)', 'Skill Match (%)', 'Composite Score', 'Status'])
    for i, r in enumerate(results, 1):
        writer.writerow([
            i,
            r.get('filename', '').rsplit('.', 1)[0],
            r.get('ats_score', ''),
            r.get('jd_match', ''),
            r.get('skill_match', ''),
            r.get('shortlist_score', ''),
            r.get('shortlist_label', '')
        ])

    output.seek(0)
    safe_role = role.replace(' ', '_').replace('/', '-')
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=ranker_{safe_role}.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
