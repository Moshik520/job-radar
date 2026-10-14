"""Sort a job into one job-type category by its title.

Rules are checked in order and the first match wins, so specific families come before general ones
("Android Developer - AI Finance Agent" is mobile, not AI). Tuned on ~775,000 real job titles,
including Hebrew titles from Israeli companies.
"""

import re

from app.models import Category


def words(pattern: str) -> re.Pattern:
    """Whole words, case-insensitive; works for words that start/end with symbols (.net, c#, c++)."""
    return re.compile(rf"(?<!\w)(?:{pattern})(?!\w)", re.IGNORECASE)


def heb(pattern: str) -> re.Pattern:
    """Hebrew word prefixes: "בנקא" matches בנקאי.ת, בנקאים.ות ..."""
    return re.compile(rf"(?<!\w)(?:{pattern})", re.IGNORECASE)


# Ordered: the first matching rule wins, so more specific families come first.
TECH_RULES: list[tuple[Category, re.Pattern]] = [
    ("general_application", words(
        r"initiativbewerbung|general application|open application|open sollicitatie|spontaneous application|"
        r"candidature spontan\w*|general interest|talent pool|talent community|future opportunities|"
        r"don't see (a|the) (role|position)|join our talent"
    )),
    # --- gigs that look like tech but are not engineering ---
    ("ai_training", words(
        r"ai (trainer|tutor|writer|rater|evaluator|data trainer)|data annotat\w*|annotator|"
        r"(freelance|expert) .*\b(ai|llm)\b|ai .*(freelance|contract)|labeling specialist|rlhf|"
        r"(generalist|specialist|expert) - ai|train(ing)? ai|evaluation specialist|"
        r"generative ai associate|data collection contributor|ai data specialist"
    )),
    # --- tech: specific families first ---
    ("design", words(
        r"ux|ui|ux/ui|ui/ux|product designer|interaction designer|visual designer|web designer|"
        r"user research(er)?|design researcher|graphic designer|brand designer|motion designer|"
        r"content designer|design system|creative director|art director|illustrator|designer|"
        r"head of design|design (lead|manager|director)"
    )),
    ("product", words(
        r"product (manager|management|owner|lead|director|operations|analyst|strategy|specialist)|"
        r"(vp|head|director|chief) of product|cpo|group product|technical product|product ops"
    )),
    ("qa", words(
        r"qa|quality assurance|sdet|software (development )?engineer in test|test automation|"
        r"automation (qa|test(er|ing)?)|(software|qa|manual|automation|game|mobile|performance|integration|"
        r"system|systems|validation) test(er|ing)?|test (engineer|lead|manager|analyst|architect|developer)|"
        r"tester|quality engineer(ing)?|software quality"
    )),
    ("security", words(
        r"security|cyber|cybersecurity|secops|devsecops|soc analyst|pentest(er|ing)?|penetration|"
        r"threat|malware|vulnerability|incident response|detection engineer|red team|blue team|grc|"
        r"iam|identity and access|appsec|offensive|ciso|edr|siem|forensic\w*"
    )),
    # Stack families before AI: "Android Developer - AI Finance Agent" is a mobile job.
    ("mobile", words(r"ios|android|mobile (developer|engineer|application)|react native|flutter|swift|kotlin")),
    ("fullstack", words(r"full[\s-]?stack|fullstack")),
    ("frontend", words(r"front[\s-]?end|frontend|react|angular|vue|javascript|typescript|web developer|ui engineer")),
    ("backend", words(r"back[\s-]?end|backend|server[\s-]side|api engineer|distributed systems|microservices")),
    ("ai_ml", words(
        r"machine learning|ml|mlops|ai|a\.i\.|artificial intelligence|llm|llms|nlp|computer vision|"
        r"deep learning|genai|generative|applied scientist|research scientist|ai/ml|ml/ai|"
        r"algorithms?|perception|reinforcement learning|inference|agentic"
    )),
    ("data", words(
        r"data(?! center)|analytics|business intelligence|bi|bi developer|etl|data warehouse|dbt|"
        r"statistician|statistics|insights analyst|tableau|power bi|business analyst|"
        r"quantitative (researcher|developer|analyst)|quant (researcher|developer)"
    )),
    ("devops", words(
        r"devops|sre|site reliability|reliability engineer|cloud|kubernetes|k8s|infrastructure|"
        r"platform engineer(ing)?|production engineer|build engineer|release engineer|"
        r"systems engineer|system engineer|linux|network engineer|network(ing)?|data center|"
        r"observability|terraform|aws|azure|gcp|ci/cd"
    )),
    ("hardware", words(
        r"fpga|asic|rtl|soc|vlsi|verification|silicon|chip|firmware|embedded|hardware|"
        r"board design|pcb|physical design|analog|mixed[\s-]signal|layout engineer|dft|sta|"
        r"photonics|optical|rf engineer|semiconductor|emulation|post[\s-]silicon|signal integrity|"
        r"power electronics|electronics engineer|robotics|autonomy|avionics"
    )),
    # Language-named roles with no clearer family: "Senior Java Developer".
    ("backend", words(
        r"java|golang|go developer|\.net|c#|node|node\.js|nodejs|python|ruby|rails|php|scala|rust|elixir"
    )),
    ("solutions", words(
        r"forward[\s-]deployed|solutions? (engineer|architect|consultant)|sales engineer|pre[\s-]?sales|"
        r"presales|customer engineer|field engineer|implementation (engineer|consultant|specialist|manager)|"
        r"technical account manager|integration engineer|deployment engineer|professional services|"
        r"technical consultant|sales architect|partner engineer|developer advocate|devrel|"
        r"developer relations|technical solutions|deployment strategist|customer success engineer"
    )),
    ("it_support", words(
        r"it|helpdesk|help desk|service desk|desktop support|system administrator|sysadmin|"
        r"systems administrator|technical support|tech support|support engineer|it support|"
        r"application support|erp|sap|salesforce (admin|administrator|developer)|servicenow|"
        r"database administrator|dba|noc"
    )),
    ("software", words(
        r"software|developer|programmer|coder|c\+\+|c|engineering manager|vp engineering|"
        r"head of engineering|director of engineering|cto|chief technology officer|r&d|tech lead|technical lead|"
        r"member of technical staff|mts|architect|game engineer|graphics engineer|compiler|"
        r"engineer|engineering"
    )),
]

# Non-tech families. Checked BEFORE the generic "engineer" fallbacks matter, but after specific tech families.
NON_TECH_RULES: list[tuple[Category, re.Pattern]] = [
    ("healthcare", words(
        r"physicians|surgeons?|\w+ologists?|\w+iatrists?|\w+odontists?|dentists?|disability examiner|"
        r"telehealth|assistante de vie|psychotherap\w*|auxiliaire de vie|aide[\s-]soignant\w*|aide à domicile|aide aux personnes|"
        r"infirmi\w*|pflege\w*|krankenpfleg\w*|arzt|ärzt\w*|zahnarzt\w*|zahnärzt\w*|operationstechnisch\w*|"
        r"anästhesie\w*|child development|autism|intervention specialist|behavioral interventionist|"
        r"behavior analyst|personal care|direct support professional|dsp|medisch\w*|verpleeg\w*|"
        r"nurse|nursing|rn|lpn|cna|np|pmhnp|physician|doctor|md|do|medical|clinical|clinician|patient|"
        r"pharmac\w*|dental|dentist|hygienist|therapist|therapy|psychiatr\w*|psycholog\w*|counselor|"
        r"behavior technician|rbt|bcba|aba|veterinar\w*|vet tech|surgeon|surgical|radiolog\w*|"
        r"sonographer|phlebotom\w*|paramedic|emt|caregiver|care (assistant|worker|coordinator)|"
        r"home health|hospice|health|healthcare|locum|optometr\w*|audiolog\w*|speech[\s-]language|"
        r"occupational|respiratory|anesthes\w*|midwife|medical assistant|dietitian|nutritionist|"
        r"social worker|case manager|mental|lab technician|laboratory|histotech\w*|cardio\w*"
    )),
    ("fitness", words(
        r"personal trainer|fitness|yoga|pilates|lifeguard|wellness|massage|"
        r"esthetician|spa|fitness trainer|barber|stylist|cosmetolog\w*|swim\w*|zwem\w*"
    )),
    ("education", words(
        r"teacher|tutor|teaching|professor|lecturer|instructional|curriculum|education|educator|"
        r"school|faculty|academic|learning designer|trainer|training specialist|preschool|childcare"
    )),
    ("legal", words(
        r"legal|lawyer|attorney|counsel|paralegal|compliance|regulatory|privacy|contracts? manager|"
        r"litigation|aml|kyc|risk|audit|auditor|governance|ethics|policy"
    )),
    ("finance", words(
        r"finance|financial|accountant|accounting|accounts (payable|receivable)|controller|"
        r"bookkeep\w*|payroll|tax|treasury|fp&a|cfo|billing|invoic\w*|credit|underwrit\w*|"
        r"actuar\w*|investment|investor|portfolio|banker|banking|trader|trading|wealth|"
        r"procurement|purchasing|buyer|revenue accountant|collections|claims|insurance|loan|mortgage|"
        r"financial analyst|fp&a|quantitative trader|quant trader|appraiser|belasting\w*|steuer\w*|"
        r"buchhalt\w*|comptab\w*|private equity|venture|equity research"
    )),
    ("hr", words(
        r"recruit\w*|talent|sourcer|hr|human resources|people (partner|operations|ops|business partner|"
        r"team|experience)|hrbp|compensation|benefits|people|learning (and|&) development|l&d|onboarding|"
        r"workplace|employee experience"
    )),
    ("sales", words(
        r"sales|account executive|ae|sdr|bdr|business development|bizdev|partnerships?|partner manager|"
        r"channel|alliances|account director|key account|territory|commercial|revenue|seller|"
        r"retail|store|merchandis\w*|cashier|deal desk|inside sales|enterprise account|"
        r"customer acquisition|real estate agent|realtor|leasing|broker|verkäufer\w*|verkauf\w*|vertrieb\w*|"
        r"verkoop\w*|vendeur|vendeuse|commercial\w*|vente|promoter|product advisor|client partner"
    )),
    ("marketing", words(
        r"marketing|marketer|growth|seo|sem|content|copywriter|writer|editor|social media|community|"
        r"brand|communications|comms|public relations|pr|demand gen\w*|campaign|events?|influencer|"
        r"creative|media|journalist|video|photographer|producer|go[\s-]to[\s-]market|gtm|lifecycle|crm"
    )),
    ("customer_success", words(
        r"customer success|customer support|customer service|customer experience|customer care|"
        r"client success|client services|support specialist|support agent|support representative|"
        r"support|call center|contact center|cx|onboarding specialist|technical account|"
        r"account manager|client manager|relationship manager|concierge|guest|receptionist|front desk"
    )),
    ("operations", words(
        r"supervisor|superintendent|general manager|branch manager|area manager|regional manager|"
        r"district manager|store manager|service manager|production manager|plant manager|property manager|"
        r"shift lead|leader in training|engagement manager|consultant|consulting|analyst|quality manager|"
        r"project|projects|scrum master|agile coach|program|safety manager|team lead|leitung\w*|leiter\w*|"
        r"chef de projet|responsable|director|manager|lead|head of|executive|"
        r"operations|ops|operational|supply chain|logistics|warehouse|fulfillment|inventory|"
        r"procurement|sourcing|planner|planning|scheduler|dispatcher|dispatch|driver|delivery|"
        r"courier|shipping|transportation|fleet|facilities|facility|program manager|project manager|"
        r"pmo|chief of staff|strategy|business operations|bizops|revops|biz ops|"
        r"project coordinator|program coordinator|operator"
    )),
    ("admin", words(
        r"assistant|administrative|admin|office|secretary|executive assistant|clerk|data entry|"
        r"coordinator|receptionist|scheduler|associate"
    )),
    ("mechanical", words(
        r"mechanical|electrical|civil|structural|chemical|process engineer|manufacturing|"
        r"industrial|mechatronics|controls engineer|automation engineer|plc|hvac|"
        r"materials|metallurg\w*|aerospace|propulsion|thermal|piping|environmental|geotechnical|"
        r"water resources|transportation engineer|traffic|construction|estimator|surveyor|"
        r"quality (inspector|control|technician)|supplier quality|reliability engineer|maintenance engineer|"
        r"energy|solar|battery|nuclear|biomedical engineer|test technician"
    )),
    ("trades", words(
        r"technician|tech|mechanic|electrician|plumber|plumbing|welder|welding|carpenter|"
        r"machinist|installer|maintenance|repair|hvac|cook|chef|kitchen|server|bartender|"
        r"barista|housekeep\w*|janitor|custodian|cleaner|security officer|security guard|guard|"
        r"labor(er)?|assembler|operator|forklift|painter|landscap\w*|groundskeeper|reinigung\w*|"
        r"cleaning|detailer|lot attendant|dishwasher|material handler|hospitality|koch|köchin|"
        r"servicemitarbeiter\w*|hulpkracht|janitor\w*|vehicle inspector|crew member|team member|"
        r"agent d'entretien|nettoyage|mitarbeiter\w*|medewerker\w*|restaurant|host|hostess|porter|"
        r"bus person|busser|steward|küchen\w*|spül\w*|key holder|piercer|foreman|crew chief|apprentice|"
        r"waiter|waitress|food|catering|hotel|housekeeper|valet|usher|attendant"
    )),
]

HARD_NON_TECH = words(
    r"nurse|nursing|rn|lpn|physician|therapist|psychotherap\w*|psychiatr\w*|veterinar\w*|dental|pharmacist|"
    r"behavior technician|behavior analyst|rbt|bcba|caregiver|personal trainer|home health|hospice|"
    r"mechanical|civil engineer|electrical engineer|structural engineer|chemical engineer|controls engineer|"
    r"project engineer|process engineer|manufacturing engineer|hvac|electrician|plumber|welder|mechanic|"
    r"engineering technician|financial analyst|fp&a|quantitative trader|supplier quality|thermal"
)


# Hebrew titles (mostly from Comeet). Checked first for titles that contain Hebrew.
HEBREW_RULES: list[tuple[Category, re.Pattern]] = [
    ("general_application", heb(r"לא מצאת משרה|משרה כללית|הגשת מועמדות כללית|יריד תעסוקה")),
    ("design", heb(r"מעצב")),
    ("legal", heb(r'עו"ד|עו״ד|ניהול סיכונים')),
    ("it_support", heb(r"תקשוב")),
    ("it_support", heb(r"טכנאי\S* מערכות|תמיכה טכנית|תקשורת ותשתיות|תשתיות רשת|סיסטם|IT(?!\w)")),
    ("qa", heb(r"בודק|בדיקות|בקר\S* איכות תוכנה")),
    ("software", heb(r"מפתח|מתכנת|פיתוח תוכנה|תוכנה|מהנדס\S* מערכת|מהנדס\S* תוכנה")),
    ("hardware", heb(r"אינטגרטור|אלקטרוני|חומרה|משובץ")),
    ("data", heb(r"מנתח\S* נתונים|דאטה|אנליסט")),
    ("finance", heb(r"בנקא|כספר|השקעות|משכנתא|חשב|הנהלת חשבונות|כלכל|גבי|אשראי|ביטוח")),
    ("sales", heb(r"מכירות|מכירה|פיתוח עסקי")),
    ("customer_success", heb(r"שירות|קשרי לקוחות|לקוחות|מוקד|נציג")),
    ("education", heb(r"מדריך|מדריכ|מורה|פדגוג|הדרכה|педагог|учитель")),
    ("hr", heb(r"גיוס|משאבי אנוש")),
    ("marketing", heb(r"שיווק|תוכן|סושיאל|מיתוג")),
    ("legal", heb(r"משפט|עורך\S* דין|ציות|רגולציה")),
    ("trades", heb(r"טכנאי|מלקט|מחסנ|נהג|הרכבות|מכונא|חשמלאי|ליקוט")),
    ("operations", heb(r"רכז|מנהל\S* אתר|אחראי\S* משמרת|מנהל|תפעול|בטיחות|לוגיסטיקה|פרויקט")),
    ("admin", heb(r"מזכיר|אדמיניסטרצ|משרד|קבלה")),
]
HEBREW = re.compile(r"[\u0590-\u05FF\u0400-\u04FF]")  # Hebrew or Cyrillic letters

# English titles seen among Israeli jobs that the main rules miss.
EXTRA_RULES: list[tuple[Category, re.Pattern]] = [
    ("general_application", words(r"external post|the role you are perfect for")),
    ("product", words(r"technical pm|pm|product expert")),
    ("security", words(r"incident respond\w*|investigator")),
    ("solutions", words(
        r"salesforce implementer|system integrator|systems integrator|integration specialist|implementer|"
        r"system expert|technical field representative"
    )),
    ("software", words(r"sw|quantum|bioinformatics")),
    ("finance", words(r"collection specialist|treasurer|card processing")),
    ("sales", words(r"regional vice president|retention representative|account development")),
    ("marketing", words(r"ppc|ad operations?|employer branding")),
]


def classify_category(title: str) -> Category:
    title = title or ""
    if HEBREW.search(title):
        for category, pattern in HEBREW_RULES:
            if pattern.search(title):
                return category
    for category, pattern in EXTRA_RULES:
        if pattern.search(title):
            return category
    # Clearly non-tech titles ("Mechanical Engineer", "Nurse") skip the tech rules.
    if HARD_NON_TECH.search(title):
        for category, pattern in NON_TECH_RULES:
            if pattern.search(title):
                return category
    for category, pattern in TECH_RULES:
        if pattern.search(title):
            return category
    for category, pattern in NON_TECH_RULES:
        if pattern.search(title):
            return category
    return "other"
