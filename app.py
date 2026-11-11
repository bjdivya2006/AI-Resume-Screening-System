from flask import Flask, render_template, request, jsonify
from docx import Document
import os
import re
import math
import io
import fitz
import pytesseract
from PIL import Image
from collections import Counter
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
JOB_ROLES = {
    "java developer": {
        "skills": [
            "java",
            "spring",
            "spring boot",
            "sql",
            "mysql",
            "rest api",
            "api",
            "git",
            "github",
            "oops",
            "object oriented programming",
            "data structures",
            "algorithms",
            "backend",
            "problem solving"
        ]
    },
    "python developer": {
        "skills": [
            "python",
            "django",
            "flask",
            "fastapi",
            "sql",
            "mysql",
            "postgresql",
            "rest api",
            "api",
            "git",
            "github",
            "oops",
            "data structures",
            "algorithms",
            "backend",
            "problem solving"
        ]
    },
    "full stack developer": {
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "node",
            "nodejs",
            "express",
            "python",
            "java",
            "sql",
            "mysql",
            "mongodb",
            "rest api",
            "api",
            "git",
            "github",
            "frontend",
            "backend",
            "problem solving"
        ]
    },
    "frontend developer": {
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "angular",
            "typescript",
            "bootstrap",
            "frontend",
            "ui",
            "user interface",
            "git",
            "github",
            "problem solving"
        ]
    },
    "backend developer": {
        "skills": [
            "java",
            "python",
            "node",
            "nodejs",
            "spring boot",
            "django",
            "flask",
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
            "rest api",
            "api",
            "git",
            "github",
            "backend",
            "data structures",
            "algorithms"
        ]
    },
    "software engineer": {
        "skills": [
            "java",
            "python",
            "c",
            "c++",
            "javascript",
            "sql",
            "git",
            "github",
            "data structures",
            "algorithms",
            "oops",
            "object oriented programming",
            "software development",
            "problem solving",
            "communication"
        ]
    },
    "ai ml engineer": {
        "skills": [
            "python",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "ai",
            "nlp",
            "natural language processing",
            "tensorflow",
            "pytorch",
            "scikit learn",
            "data science",
            "numpy",
            "pandas",
            "sql",
            "git"
        ]
    },
    "data scientist": {
        "skills": [
            "python",
            "machine learning",
            "data science",
            "statistics",
            "pandas",
            "numpy",
            "sql",
            "data analysis",
            "visualization",
            "tensorflow",
            "pytorch",
            "nlp"
        ]
    },
    "web developer": {
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "node",
            "python",
            "php",
            "sql",
            "mysql",
            "mongodb",
            "rest api",
            "git",
            "github",
            "frontend",
            "backend"
        ]
    }
}
ALL_SKILLS = [
    "java",
    "python",
    "c++",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "angular",
    "node",
    "nodejs",
    "express",
    "flask",
    "django",
    "fastapi",
    "spring",
    "spring boot",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "google cloud",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "natural language processing",
    "data science",
    "data analysis",
    "tensorflow",
    "pytorch",
    "numpy",
    "pandas",
    "rest api",
    "api",
    "linux",
    "data structures",
    "algorithms",
    "oops",
    "object oriented programming",
    "problem solving",
    "communication",
    "teamwork",
    "leadership",
    "frontend",
    "backend"
]
def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(
        r"\s+",
        " ",
        text
    )
    return text.strip()
def clean_text(text):
    text = normalize_text(text)
    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text
    )
    text = re.sub(
        r"\s+",
        " ",
        text
    )
    return text.strip()
def extract_pdf_text(file):
    try:
        print("\n================================")
        print("PDF PROCESSING")
        print("================================")
        file.seek(0)
        pdf_bytes = file.read()
        print(
            "PDF size:",
            len(pdf_bytes),
            "bytes"
        )
        pdf = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )
        print(
            "Pages:",
            len(pdf)
        )
        normal_text = ""
        for page in pdf:
            page_text = page.get_text()
            if page_text:
                normal_text += page_text + "\n"
        print(
            "Normal text characters:",
            len(normal_text)
        )
        if len(normal_text.strip()) > 20:
            pdf.close()
            print(
                "Using normal PDF text extraction."
            )
            return normal_text.strip()
        print(
            "PDF appears scanned."
        )
        print(
            "Starting OCR..."
        )
        ocr_text = ""
        for page_number, page in enumerate(pdf):
            print(
                f"OCR page {page_number + 1}/"
                f"{len(pdf)}"
            )
            matrix = fitz.Matrix(
                2.5,
                2.5
            )
            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )
            image_bytes = pix.tobytes(
                "png"
            )
            image = Image.open(
                io.BytesIO(image_bytes)
            )
            page_text = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--psm 6"
            )
            ocr_text += (
                page_text + "\n"
            )
        pdf.close()
        print(
            "OCR characters:",
            len(ocr_text)
        )
        return ocr_text.strip()
    except Exception as e:
        print(
            "PDF extraction error:",
            str(e)
        )
        return ""
def extract_docx_text(file):
    try:
        document = Document(file)
        text_parts = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text_parts.append(
                    paragraph.text
                )
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(
                            cell.text
                        )
        return "\n".join(
            text_parts
        ).strip()
    except Exception as e:
        print(
            "DOCX extraction error:",
            str(e)
        )
        return ""
def extract_resume_text(file):
    filename = (
        file.filename or ""
    ).lower()
    if filename.endswith(".pdf"):
        return extract_pdf_text(file)
    if filename.endswith(".docx"):
        return extract_docx_text(file)
    return ""
def tokenize(text):
    cleaned = clean_text(text)
    words = cleaned.split()
    stop_words = {
        "the",
        "and",
        "or",
        "a",
        "an",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "was",
        "were",
        "this",
        "that",
        "from",
        "as",
        "at",
        "by",
        "be",
        "has",
        "have",
        "had",
        "it",
        "its",
        "their",
        "they",
        "he",
        "she",
        "we",
        "you",
        "i"
    }
    return [
        word
        for word in words
        if word not in stop_words
        and len(word) > 1
    ]
def calculate_tfidf(documents):
    tokenized_documents = [
        tokenize(document)
        for document in documents
    ]
    vocabulary = set()
    for document in tokenized_documents:
        vocabulary.update(
            document
        )
    vocabulary = list(vocabulary)
    total_documents = len(
        tokenized_documents
    )
    tfidf_documents = []
    for document in tokenized_documents:
        word_count = Counter(
            document
        )
        total_words = len(
            document
        )
        vector = {}
        for word in vocabulary:
            if total_words > 0:
                tf = (
                    word_count[word]
                    /
                    total_words
                )
            else:
                tf = 0
            document_frequency = sum(
                1
                for doc in tokenized_documents
                if word in doc
            )
            idf = (
                math.log(
                    (total_documents + 1)
                    /
                    (document_frequency + 1)
                )
                + 1
            )
            vector[word] = (
                tf * idf
            )
        tfidf_documents.append(
            vector
        )
    return tfidf_documents
def cosine_similarity(
    vector1,
    vector2
):
    dot_product = 0
    magnitude1 = 0
    magnitude2 = 0
    all_words = (
        set(vector1.keys())
        |
        set(vector2.keys())
    )
    for word in all_words:
        value1 = vector1.get(
            word,
            0
        )
        value2 = vector2.get(
            word,
            0
        )
        dot_product += (
            value1 * value2
        )
        magnitude1 += (
            value1 ** 2
        )
        magnitude2 += (
            value2 ** 2
        )
    magnitude1 = math.sqrt(
        magnitude1
    )
    magnitude2 = math.sqrt(
        magnitude2
    )
    if (
        magnitude1 == 0
        or
        magnitude2 == 0
    ):
        return 0
    return (
        dot_product
        /
        (
            magnitude1
            *
            magnitude2
        )
    )
def get_job_profile(job_role):
    role = clean_text(
        job_role
    )
    if role in JOB_ROLES:
        return JOB_ROLES[role]
    for known_role, profile in JOB_ROLES.items():
        if (
            known_role in role
            or
            role in known_role
        ):
            return profile
    detected_skills = []
    for skill in ALL_SKILLS:
        pattern = (
            r"(?<!\w)"
            +
            re.escape(skill)
            +
            r"(?!\w)"
        )
        if re.search(
            pattern,
            role
        ):
            detected_skills.append(
                skill
            )
    if detected_skills:
        return {
            "skills": detected_skills
        }
    return None
def extract_skills(text):
    cleaned = clean_text(
        text
    )
    found_skills = []
    for skill in ALL_SKILLS:
        pattern = (
            r"(?<!\w)"
            +
            re.escape(skill)
            +
            r"(?!\w)"
        )
        if re.search(
            pattern,
            cleaned
        ):
            found_skills.append(
                skill
            )
    return found_skills
def calculate_skill_score(
    resume_text,
    job_skills
):
    resume_skills = extract_skills(
        resume_text
    )
    matched = []
    missing = []
    for skill in job_skills:
        if skill in resume_skills:
            matched.append(
                skill
            )
        else:
            missing.append(
                skill
            )
    if not job_skills:
        score = 0
    else:
        score = (
            len(matched)
            /
            len(job_skills)
        ) * 100
    return (
        round(score, 2),
        matched,
        missing
    )
def detect_sections(text):
    cleaned = normalize_text(
        text
    )
    sections = {
        "education": bool(
            re.search(
                r"\b("
                r"education|"
                r"academic|"
                r"degree|"
                r"b\.?e\.?|"
                r"b\.?tech|"
                r"m\.?tech|"
                r"bachelor|"
                r"master|"
                r"university|"
                r"college"
                r")\b",
                cleaned,
                re.IGNORECASE
            )
        ),
        "experience": bool(
            re.search(
                r"\b("
                r"experience|"
                r"work experience|"
                r"employment|"
                r"internship|"
                r"internships|"
                r"professional experience"
                r")\b",
                cleaned,
                re.IGNORECASE
            )
        ),
        "projects": bool(
            re.search(
                r"\b("
                r"projects|"
                r"project|"
                r"academic project|"
                r"personal project"
                r")\b",
                cleaned,
                re.IGNORECASE
            )
        ),
        "skills": bool(
            re.search(
                r"\b("
                r"skills|"
                r"technical skills|"
                r"technologies|"
                r"technical"
                r")\b",
                cleaned,
                re.IGNORECASE
            )
        ),
        "certifications": bool(
            re.search(
                r"\b("
                r"certification|"
                r"certifications|"
                r"certificate|"
                r"certified"
                r")\b",
                cleaned,
                re.IGNORECASE
            )
        )
    }
    return sections
def calculate_section_score(
    sections
):
    total = len(
        sections
    )
    found = sum(
        1
        for value in sections.values()
        if value
    )
    if total == 0:
        return 0
    return round(
        (found / total) * 100,
        2
    )
def calculate_experience_score(
    text
):
    cleaned = normalize_text(
        text
    )
    score = 0
    if re.search(
        r"\bexperience\b",
        cleaned
    ):
        score += 50
    if re.search(
        r"\binternship\b|\binternships\b",
        cleaned
    ):
        score += 25
    if re.search(
        r"\bdeveloper\b|\bengineer\b|\bsoftware\b",
        cleaned
    ):
        score += 25
    return min(
        score,
        100
    )
def calculate_education_score(
    text
):
    cleaned = normalize_text(
        text
    )
    keywords = [
        "b.e",
        "b.tech",
        "be",
        "btech",
        "m.e",
        "m.tech",
        "me",
        "mtech",
        "bachelor",
        "master",
        "degree",
        "engineering",
        "computer science",
        "university",
        "college"
    ]
    found = 0
    for keyword in keywords:
        if keyword in cleaned:
            found += 1
    if found >= 3:
        return 100
    if found == 2:
        return 80
    if found == 1:
        return 60
    return 20
def calculate_project_score(
    text
):
    cleaned = normalize_text(
        text
    )
    if re.search(
        r"\bprojects?\b",
        cleaned
    ):
        return 100
    if re.search(
        r"\bdeveloped\b|\bimplemented\b|\bbuilt\b",
        cleaned
    ):
        return 70
    return 20
def calculate_certification_score(
    text
):
    cleaned = normalize_text(
        text
    )
    if re.search(
        r"\bcertifications?\b|\bcertified\b|\bcertificate\b",
        cleaned
    ):
        return 100
    return 20
def calculate_role_score(
    text,
    job_role
):
    cleaned_resume = normalize_text(
        text
    )
    role_words = [
        word
        for word in clean_text(
            job_role
        ).split()
        if len(word) > 2
    ]
    if not role_words:
        return 0
    matched = 0
    for word in role_words:
        if word in cleaned_resume:
            matched += 1
    return round(
        (matched / len(role_words))
        * 100,
        2
    )
def calculate_ats_score(
    text,
    sections,
    matched_skills
):
    score = 0
    if len(text.strip()) > 100:
        score += 20
    elif len(text.strip()) > 30:
        score += 10
    section_count = sum(
        1
        for value in sections.values()
        if value
    )
    score += min(
        section_count * 8,
        40
    )
    if len(matched_skills) >= 5:
        score += 30
    elif len(matched_skills) >= 3:
        score += 20
    elif len(matched_skills) >= 1:
        score += 10
    if re.search(
        r"\b[\w.-]+@[\w.-]+\.\w+\b",
        text
    ):
        score += 5
    if re.search(
        r"\b\d{10}\b",
        re.sub(r"\D", " ", text)
    ):
        score += 5
    return min(
        score,
        100
    )
def get_recommendation(
    score
):
    if score >= 80:
        return (
            "Excellent Match",
            "Highly Recommended"
        )
    if score >= 65:
        return (
            "Good Match",
            "Recommended for Interview"
        )
    if score >= 50:
        return (
            "Moderate Match",
            "Consider for Interview"
        )
    return (
        "Low Match",
        "Not Recommended"
    )
@app.route("/")
def index():
    return render_template(
        "index.html"
    )
@app.route(
    "/screen",
    methods=["POST"]
)
def screen_resumes():
    try:
        job_role = request.form.get(
            "job_role",
            ""
        ).strip()
        resumes = request.files.getlist(
            "resumes"
        )
        print("\n================================")
        print("NEW SCREENING REQUEST")
        print("================================")
        print(
            "Job role:",
            job_role
        )
        print(
            "Number of resumes:",
            len(resumes)
        )
        if not job_role:
            return jsonify({
                "error":
                "Please enter the vacancy/job name."
            }), 400
        if not resumes:
            return jsonify({
                "error":
                "Please upload at least one resume."
            }), 400
        job_profile = get_job_profile(
            job_role
        )
        if not job_profile:
            return jsonify({
                "error":
                "Job role not supported. Try a role such as "
                "Java Developer, Python Developer, Full Stack Developer, "
                "Frontend Developer, Backend Developer, Software Engineer, "
                "AI ML Engineer, Data Scientist or Web Developer."
            }), 400
        job_skills = job_profile[
            "skills"
        ]
        resume_data = []
        for resume in resumes:
            if not resume.filename:
                continue
            filename = resume.filename
            print(
                "\nProcessing:",
                filename
            )
            text = extract_resume_text(
                resume
            )
            print(
                "Extracted characters:",
                len(text)
            )
            if not text.strip():
                print(
                    "WARNING: No text extracted"
                )
                continue
            resume_data.append({
                "filename": filename,
                "text": text
            })
        if not resume_data:
            return jsonify({
                "error":
                "No readable text was found in the uploaded resumes. "
                "Please upload a PDF or DOCX resume with readable content."
            }), 400
        documents = [
            job_role
        ]
        documents.extend(
            resume["text"]
            for resume in resume_data
        )
        tfidf_vectors = calculate_tfidf(
            documents
        )
        job_vector = tfidf_vectors[0]
        results = []
        for index, resume in enumerate(
            resume_data
        ):
            text = resume["text"]
            resume_vector = tfidf_vectors[
                index + 1
            ]
            similarity = cosine_similarity(
                job_vector,
                resume_vector
            )
            similarity_score = min(
                similarity * 100,
                100
            )
            skill_score, matched_skills, missing_skills = (
                calculate_skill_score(
                    text,
                    job_skills
                )
            )
            sections = detect_sections(
                text
            )
            role_score = calculate_role_score(
                text,
                job_role
            )
            education_score = calculate_education_score(
                text
            )
            experience_score = calculate_experience_score(
                text
            )
            project_score = calculate_project_score(
                text
            )
            certification_score = calculate_certification_score(
                text
            )
            ats_score = calculate_ats_score(
                text,
                sections,
                matched_skills
            )
            eligibility = (
                skill_score * 0.35
                +
                similarity_score * 0.20
                +
                role_score * 0.10
                +
                experience_score * 0.10
                +
                education_score * 0.10
                +
                project_score * 0.10
                +
                certification_score * 0.05
            )
            eligibility = round(
                min(
                    max(
                        eligibility,
                        0
                    ),
                    100
                ),
                2
            )
            status, decision = get_recommendation(
                eligibility
            )
            results.append({
                "filename":
                    resume["filename"],
                "eligibility":
                    eligibility,
                "ats_score":
                    ats_score,
                "skill_score":
                    skill_score,
                "similarity_score":
                    round(
                        similarity_score,
                        2
                    ),
                "experience_score":
                    experience_score,
                "role_score":
                    role_score,
                "education_score":
                    education_score,
                "project_score":
                    project_score,
                "certification_score":
                    certification_score,
                "matched_skills":
                    matched_skills,
                "missing_skills":
                    missing_skills,
                "sections":
                    sections,
                "status":
                    status,
                "decision":
                    decision,
                "rank":
                    0
            })
        results.sort(
            key=lambda candidate:
                candidate["eligibility"],
            reverse=True
        )
        for index, candidate in enumerate(
            results
        ):
            candidate["rank"] = (
                index + 1
            )
        response = {
            "job_role":
                job_role,
            "total_candidates":
                len(results),
            "job_skills":
                job_skills,
            "candidates":
                results
        }
        print(
            "\n================================"
        )
        print(
            "SCREENING COMPLETED"
        )
        print(
            "Candidates:",
            len(results)
        )
        print(
            "================================\n"
        )
        return jsonify(
            response
        )
    except Exception as e:
        print(
            "\n================================"
        )
        print(
            "SERVER ERROR"
        )
        print(
            str(e)
        )
        print(
            "================================\n"
        )
        return jsonify({
            "error":
            "An error occurred while analyzing "
            "the resumes: " + str(e)
        }), 500
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )