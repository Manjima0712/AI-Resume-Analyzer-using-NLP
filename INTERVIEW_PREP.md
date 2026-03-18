# Technical Interview Preparation Guide

This document explains the core architecture and technical decisions behind the AI Resume Analyzer to help you explain the project during technical interviews.

## 🏗️ System Architecture

The project follows a modular 3-tier structure:
1.  **Presentation Tier**: Flask templates using Jinja2, modern CSS, and JS for real-time validation.
2.  **Application Tier**: `app.py` handles the workflow orchestrating multiple core services.
3.  **Engine Tier (Core)**: Modular NLP and ML engines for parsing, matching, and scoring.

## 🧠 Core Technical Concepts

### 1. Resume & JD Matching (JD Match)
- **Algorithm**: TF-IDF (Term Frequency-Inverse Document Frequency) + Cosine Similarity.
- **Explanation**: We convert the cleaned resume and JD text into numerical vectors. TF-IDF highlights important keywords (excluding common stop words). Cosine similarity measures the angle between these vectors — a higher similarity means the resume uses similar language and keywords as the JD.

### 2. Skill Extraction & Normalization
- **Problem**: Candidates use different terms (e.g., "scikit-learn", "sklearn", "sk-learn").
- **Solution**: I implemented a **Canonical Alias Map**. Before matching, the text is normalized where all aliases are replaced with a standard canonical name.
- **Scoring**: Role-required skills (from `role_skills.json`) have full weight (1.0). Skills found only in the JD have half weight (0.5). This prevents penalizing a candidate for missing "nice-to-have" extras.

### 3. Comparison-Based Recommendation
- **Motivation**: A generic average score can be misleading. A candidate might have "Good" skills but a "Poor" ATS score, making them 100% likely to be rejected.
- **Implementation**: The `ShortlistEngine` identifies the **weakling metric**. It flags the lowest score and uses it to drive the final recommendation label (e.g., "Needs ATS Improvement").

### 4. Text Preprocessing
- **Workflow**:
    1.  Remove special characters and numbers.
    2.  Tokenization (NLTK).
    3.  Stop word removal.
    4.  Lemmatization (reducing words to their root form).

## ❓ Common Technical Q&A

**Q: Why did you use TF-IDF instead of simple word counting?**
*A: Word counting gives too much weight to common words like 'the' or 'and'. TF-IDF penalizes common words and highlights unique, domain-specific keywords (like 'Django' or 'PyTorch'), making the match much more accurate.*

**Q: How do you handle different file formats like PDF and DOCX?**
*A: I use `PyMuPDF` (fitz) for PDF extraction because it's fast and handles complex layouts well. For DOCX, I use `docx2txt`. Both extract raw text which is then passed to our cleaning pipeline.*

**Q: What was the biggest challenge in this project?**
*A: Handling skill synonyms. Many candidates are rejected by ATS simply because they use a different name for a skill. By building a canonical alias map (Normalization), my system is much more robust and "fair" compared to basic keyword matchers.*

**Q: How do you ensure the system is scalable for bulk ranking?**
*A: The system uses an O(N) ranking approach where each resume is processed independently. In a production environment, this could be offloaded to a task queue like Celery to process thousands of resumes asynchronously.*

**Q: Why choose Flask over Django?**
*A: Flask is lightweight and perfect for a data-driven microservice like this. It allowed me to focus on the NLP logic without the overhead of a heavy ORM or built-in admin panels that wasn't needed for this architecture.*
