"""ATS scoring tests."""

from app.services.ats import analyze_resume

STRONG_RESUME = """
John Doe
john.doe@email.com | +1 (555) 123-4567 | linkedin.com/in/johndoe

Professional Summary
Experienced software engineer with 5 years building scalable web applications.

Experience
Senior Developer - Tech Corp
- Led a team of 4 engineers and delivered 3 major product launches
- Improved application performance by 40% and reduced costs by $50k annually
- Built REST APIs using Python, FastAPI, and PostgreSQL

Education
B.S. Computer Science, State University

Skills
Python, JavaScript, React, SQL, AWS, Docker
"""

MINIMAL_RESUME = """
Jane Smith
jane@company.org
5559876543

Experience
Marketing Manager
- Managed campaigns for 12 clients
- Increased engagement by 25%

Education
MBA, Business School

Skills
SEO, Analytics, Content Strategy
"""


def test_strong_resume_scores_high():
    report = analyze_resume(STRONG_RESUME)
    assert report.score >= 80
    assert report.grade in {"A", "B"}
    contact = next(category for category in report.categories if category.name == "Contact Information")
    assert contact.score == contact.max_score
    sections = next(category for category in report.categories if category.name == "Section Structure")
    assert sections.score >= 23
    content = next(category for category in report.categories if category.name == "Content Quality")
    assert content.score >= 20


def test_years_are_not_counted_as_metrics_only():
    resume_with_years_only = """
John Doe
john@email.com | 5551234567

Experience
Developer at Acme
- Worked from 2019 to 2024 on internal tools
- Supported the platform team

Education
B.S. CS

Skills
Python
"""
    report = analyze_resume(resume_with_years_only)
    content = next(category for category in report.categories if category.name == "Content Quality")
    assert content.score < content.max_score


def test_section_headings_required_not_body_mentions():
    resume_without_headings = """
John Doe
john@email.com | 5551234567

I have 5 years of experience at a university-backed startup.
My skills include Python and SQL.
"""
    report = analyze_resume(resume_without_headings)
    sections = next(category for category in report.categories if category.name == "Section Structure")
    assert sections.score <= 10
    assert any("section heading" in item.lower() for item in sections.feedback)


def test_linkedin_text_variant_detected():
    resume = """
Alex Lee
alex@email.com | 5551112222
Linked In: in/alexdoe

Experience
Engineer

Education
B.A.

Skills
Java
"""
    report = analyze_resume(resume)
    contact = next(category for category in report.categories if category.name == "Contact Information")
    assert contact.score >= 13


def test_minimal_valid_resume_passes():
    report = analyze_resume(MINIMAL_RESUME)
    assert report.score >= 55
    assert report.word_count >= 20
    sections = next(category for category in report.categories if category.name == "Section Structure")
    assert sections.score >= 20
