import pytest

from app.classify import classify_category


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        # QA
        ("QA Automation Engineer", "qa"),
        ("AI-First QA Automation Engineer", "qa"),
        ("Software Engineer in Test", "qa"),
        ("SDET", "qa"),
        # Stack families win over a domain word in the title
        ("Android Developer - AI Finance Agent", "mobile"),
        ("Senior Full Stack Engineer", "fullstack"),
        ("Senior Frontend Engineer", "frontend"),
        ("Backend Team Lead", "backend"),
        ("Senior Java Developer", "backend"),
        ("Senior .NET Developer", "backend"),
        # Other tech families
        ("Machine Learning Engineer", "ai_ml"),
        ("Data Engineer", "data"),
        ("DevOps Engineer", "devops"),
        ("Network Automation Engineer", "devops"),
        ("Security Researcher", "security"),
        ("Senior FPGA Engineer", "hardware"),
        ("Help Desk", "it_support"),
        ("Sales Engineer", "solutions"),
        ("Forward Deployed Engineer", "solutions"),
        ("Senior Product Manager", "product"),
        ("Product Designer", "design"),
        ("Senior Software Engineer", "software"),
        ("Engineering Manager", "software"),
        ("Hebrew Speaker - Freelance AI Trainer Project", "ai_training"),
        # Non-tech
        ("Account Executive", "sales"),
        ("Customer Success Manager", "customer_success"),
        ("Financial Analyst", "finance"),
        ("Talent Acquisition Partner", "hr"),
        ("Legal Counsel", "legal"),
        ("Product Marketing Manager", "marketing"),
        ("Project Manager", "operations"),
        ("Mechanical Engineer", "mechanical"),
        ("Supplier Quality Engineer", "mechanical"),
        ("Civil Engineer", "mechanical"),
        ("Registered Nurse", "healthcare"),
        ("Personal Trainer", "fitness"),
        ("General Application (Israel)", "general_application"),
        # Hebrew titles
        ("בנקאי.ת שירות", "finance"),
        ("איש/אשת מכירות", "sales"),
        ("מפתח.ת Java למערכות IVR & CTI", "software"),
        ("מלקטים - וולט מרקט - כפר סבא", "trades"),
        ('מדריך חי"ר', "education"),
        ("לא מצאת משרה רלוונטית?", "general_application"),
        # Nothing matches
        ("Secret Evaluator in Tel Aviv", "other"),
        ("", "other"),
    ],
)
def test_classify_category(title, expected):
    assert classify_category(title) == expected
