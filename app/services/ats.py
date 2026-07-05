"""ATS resume scoring service - Shakkar Daddy."""

__author__ = "Shakkar Daddy"

import re

from app.schemas.ats import ATSScoreReport, CategoryScore

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_CANDIDATE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{8,}\d)")
LINKEDIN_PATTERNS = [
    re.compile(r"linkedin\.com", re.IGNORECASE),
    re.compile(r"linked\s*in", re.IGNORECASE),
    re.compile(r"\bin\/[a-z0-9_-]{3,}", re.IGNORECASE),
]
YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")

SECTION_DEFINITIONS = {
    "experience": [
        "experience",
        "work experience",
        "work history",
        "employment",
        "employment history",
        "professional experience",
        "career history",
    ],
    "education": [
        "education",
        "academic background",
        "academic history",
        "qualifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "core skills",
        "technologies",
        "expertise",
        "proficiencies",
    ],
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "about me",
        "about",
        "objective",
        "career objective",
    ],
}

ACTION_VERBS = {
    "achieved",
    "analyzed",
    "architected",
    "built",
    "collaborated",
    "conducted",
    "coordinated",
    "created",
    "delivered",
    "designed",
    "developed",
    "devised",
    "drove",
    "enhanced",
    "established",
    "executed",
    "generated",
    "grew",
    "headed",
    "implemented",
    "improved",
    "increased",
    "initiated",
    "launched",
    "led",
    "maintained",
    "managed",
    "mentored",
    "negotiated",
    "optimized",
    "organized",
    "oversaw",
    "performed",
    "planned",
    "produced",
    "programmed",
    "published",
    "reduced",
    "resolved",
    "spearheaded",
    "streamlined",
    "supervised",
    "supported",
    "transformed",
}

METRIC_PATTERNS = [
    re.compile(r"\d+\s*%"),
    re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?[kmb]?", re.IGNORECASE),
    re.compile(
        r"\d+\+?\s*(?:team members?|employees?|people|staff|users?|customers?|clients?|projects?)",
        re.IGNORECASE,
    ),
    re.compile(r"\bteam of \d+\b", re.IGNORECASE),
    re.compile(r"\b\d+\s+major\b", re.IGNORECASE),
    re.compile(r"\b\d+x\b", re.IGNORECASE),
    re.compile(
        r"\b(?:increased|decreased|reduced|improved|grew|saved|cut|boosted|raised|lowered)\s+(?:by\s+)?\d+",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d+\s*(?:years?|yrs?|months?|weeks?)\s+(?:of\s+)?(?:experience|exp)\b", re.IGNORECASE),
]


def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _normalize_ocr_text(text: str) -> str:
    """Fix common OCR artifacts before analysis."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"\s*\(at\)\s*", "@", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s*\[at\]\s*", "@", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s*\(dot\)\s*", ".", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s*\[dot\]\s*", ".", normalized, flags=re.IGNORECASE)
    return normalized.strip()


def _ocr_quality(text: str, word_count: int) -> str:
    if word_count < 30:
        return "poor"
    noise_ratio = len(re.findall(r"[^a-zA-Z0-9\s@.+\-()/,]", text)) / max(len(text), 1)
    if noise_ratio > 0.08 or word_count < 80:
        return "fair"
    return "good"


def _has_phone(text: str) -> bool:
    for match in PHONE_CANDIDATE_PATTERN.finditer(text):
        digits = re.sub(r"\D", "", match.group())
        if len(digits) >= 10 and not YEAR_PATTERN.fullmatch(digits):
            return True
    return False


def _has_linkedin(text: str) -> bool:
    return any(pattern.search(text) for pattern in LINKEDIN_PATTERNS)


def _line_is_heading(line: str, keywords: list[str]) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 50:
        return False

    cleaned = re.sub(r"[^\w\s/&-]", "", stripped.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return False

    return any(cleaned == keyword or cleaned.startswith(f"{keyword} ") for keyword in keywords)


def _detect_sections(text: str) -> dict[str, bool]:
    lines = text.splitlines()
    found = {key: False for key in SECTION_DEFINITIONS}

    for line in lines:
        for key, keywords in SECTION_DEFINITIONS.items():
            if not found[key] and _line_is_heading(line, keywords):
                found[key] = True

    return found


def _count_action_verbs(text: str) -> int:
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        candidate = re.sub(r"^[-•·*\u2013\u2014▪○●◦]\s*", "", stripped).strip()
        match = re.match(r"^([a-zA-Z]+)", candidate)
        if match and match.group(1).lower() in ACTION_VERBS:
            count += 1
    return count


def _count_metrics(text: str) -> int:
    hits = set()
    for pattern in METRIC_PATTERNS:
        for match in pattern.finditer(text):
            snippet = match.group().strip()
            if YEAR_PATTERN.fullmatch(re.sub(r"\D", "", snippet)):
                continue
            hits.add(snippet.lower())
    return len(hits)


def _score_contact(text: str) -> CategoryScore:
    feedback: list[str] = []
    score = 0
    max_score = 15

    has_email = bool(EMAIL_PATTERN.search(text))
    has_phone = _has_phone(text)
    has_linkedin = _has_linkedin(text)

    if has_email:
        score += 6
    else:
        feedback.append("Add a professional email address.")

    if has_phone:
        score += 5
    else:
        feedback.append("Include a phone number for recruiters to reach you.")

    if has_linkedin:
        score += 4
    else:
        feedback.append("Add your LinkedIn profile URL.")

    if not feedback:
        feedback.append("Contact details look complete.")

    return CategoryScore(name="Contact Information", score=score, max_score=max_score, feedback=feedback)


def _score_sections(text: str) -> CategoryScore:
    detected = _detect_sections(text)
    feedback: list[str] = []
    weights = {
        "experience": 9,
        "education": 8,
        "skills": 8,
    }
    score = 0
    max_score = 25
    labels = {
        "experience": "Experience",
        "education": "Education",
        "skills": "Skills",
    }

    for key, weight in weights.items():
        if detected[key]:
            score += weight
        else:
            feedback.append(f"Add a clear '{labels[key]}' section heading.")

    if detected["summary"]:
        score = min(max_score, score + 2)
    elif score >= 20:
        feedback.append("Consider adding a 'Summary' or 'Profile' section for stronger ATS keyword matching.")

    if not feedback:
        feedback.append("Core resume sections are clearly labeled.")

    return CategoryScore(name="Section Structure", score=min(score, max_score), max_score=max_score, feedback=feedback)


def _score_content(text: str) -> CategoryScore:
    feedback: list[str] = []
    action_hits = _count_action_verbs(text)
    metric_hits = _count_metrics(text)
    score = 0
    max_score = 30

    if action_hits >= 5:
        score += 15
    elif action_hits >= 2:
        score += 9
        feedback.append("Use more strong action verbs at the start of bullet points (e.g. led, built, improved).")
    else:
        feedback.append("Start bullet points with action verbs to show impact.")

    if metric_hits >= 3:
        score += 15
    elif metric_hits >= 1:
        score += 8
        feedback.append("Add more quantified results (%, $, team size, timelines).")
    else:
        feedback.append("Include measurable achievements - numbers help ATS and recruiters.")

    if not feedback:
        feedback.append("Strong use of action verbs and measurable results.")

    return CategoryScore(name="Content Quality", score=score, max_score=max_score, feedback=feedback)


def _score_readability(word_count: int) -> CategoryScore:
    feedback: list[str] = []
    max_score = 15

    if 100 <= word_count <= 650:
        score = 15
        feedback.append("Resume length is in a good ATS-friendly range.")
    elif 60 <= word_count < 100:
        score = 10
        feedback.append("Resume may be too brief - add more detail to key roles.")
    elif 650 < word_count <= 1000:
        score = 10
        feedback.append("Resume is on the long side - tighten bullets for ATS parsing.")
    elif word_count >= 1000:
        score = 7
        feedback.append("Resume is quite long - only the first page was analyzed.")
    else:
        score = 4
        feedback.append("Very little text was detected - check layout or add more content.")

    return CategoryScore(name="Length & Readability", score=score, max_score=max_score, feedback=feedback)


def _score_formatting(text: str) -> CategoryScore:
    feedback: list[str] = []
    score = 15
    max_score = 15

    special_chars = len(re.findall(r"[|{}[\]~^`]", text))
    if special_chars > 5:
        score -= 5
        feedback.append("Reduce decorative symbols - ATS parsers prefer plain text.")

    if re.search(r"\t", text):
        score -= 3
        feedback.append("Avoid tab characters; use simple bullet lists instead.")

    line_count = len([line for line in text.splitlines() if line.strip()])
    if line_count < 8:
        score -= 4
        feedback.append("Very few lines detected - single-column layouts parse best.")

    score = max(0, score)

    if not feedback:
        feedback.append("Formatting looks ATS-friendly.")

    return CategoryScore(name="Formatting", score=score, max_score=max_score, feedback=feedback)


def analyze_resume(text: str) -> ATSScoreReport:
    """Score resume text against common ATS heuristics."""
    cleaned = _normalize_ocr_text(text)
    words = re.findall(r"[a-zA-Z]{2,}", cleaned)
    word_count = len(words)
    quality = _ocr_quality(cleaned, word_count)
    sections = _detect_sections(cleaned)

    categories = [
        _score_contact(cleaned),
        _score_sections(cleaned),
        _score_content(cleaned),
        _score_readability(word_count),
        _score_formatting(cleaned),
    ]

    max_total = sum(category.max_score for category in categories)
    earned = sum(category.score for category in categories)
    total_score = round(earned * 100 / max_total)
    grade = _grade(total_score)

    tips: list[str] = []
    if quality != "good":
        tips.append("OCR quality is limited - scores may be understated; simpler fonts improve accuracy.")
    if total_score < 70:
        tips.append("Mirror keywords from job descriptions in your skills and experience sections.")
    if not sections["skills"]:
        tips.append("Add a dedicated Skills section with role-relevant keywords.")
    if word_count < 120:
        tips.append("Only the first page was analyzed - multi-page resumes may score lower.")

    summaries = {
        "A": "Excellent ATS compatibility - your resume should parse well.",
        "B": "Good ATS compatibility - a few tweaks could strengthen parsing.",
        "C": "Fair ATS compatibility - address the issues below before applying.",
        "D": "Below average - several sections may not parse correctly in ATS.",
        "F": "Poor ATS compatibility - major improvements recommended.",
    }

    return ATSScoreReport(
        score=total_score,
        grade=grade,
        summary=summaries[grade],
        categories=categories,
        tips=tips[:4],
        word_count=word_count,
        ocr_quality=quality,
    )
