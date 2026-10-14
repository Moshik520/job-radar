import re

# Every Israeli place that appeared in a job location across ~775,000 scanned jobs, plus its common spellings.
# One entry per place; each is a regex fragment. An apostrophe may be written ' ’ ‘ or left out (A).
A = "['’‘]?"
SEP = r"[\s-]?"  # "Tel Aviv", "Tel-Aviv", "TelAviv"

ISRAELI_PLACES = [
    rf"tel{SEP}aviv",
    r"yafo|jaffa",
    r"jerusalem|yerushalayim",
    r"haifa",
    r"herzliy+a",
    r"petah|petach|tikva",
    rf"ra{A}anana",
    rf"ramat{SEP}gan",
    rf"ramat{SEP}ha{SEP}sharon",
    rf"hod{SEP}ha{SEP}sharon",
    r"netanya",
    rf"yok?q?ne{A}am",
    r"rehovot",
    rf"be{A}er{SEP}sheva",
    rf"be{A}er{SEP}ya{A}akov",
    rf"k[ae]fa?r{SEP}s[ae][bv]a",
    rf"or{SEP}yehuda",
    r"yehud",
    r"caesarea",
    rf"modi{A}in",
    r"maccabim",
    r"airport city",
    rf"rosh{SEP}ha{A}?{SEP}ayin",
    rf"giv{A}atayim",
    rf"bnei{SEP}b[ae]rak",
    r"holon",
    rf"bat{SEP}yam",
    rf"rishon{SEP}le{SEP}(zion|tsiyon|ziyyon)",
    rf"ness{SEP}ziona",
    r"yavne",
    r"gedera",
    r"shoham",
    r"tzrifin",
    r"ashdod",
    r"ashkelon",
    r"ofakim",
    rf"kiryat{SEP}(gat|ono|bialik|ata|motzkin|shmona)",
    rf"migdal{SEP}ha{SEP}{A}?emek",
    rf"tirat{SEP}carmel",
    r"karmiel",
    r"afula",
    rf"yizr[ae]{A}el|jezreel",
    rf"beit{SEP}she{A}?an",
    rf"be(i)?t{SEP}shemesh",
    rf"nazareth{SEP}il+it|nof{SEP}hagalil",  # plain "Nazareth" is also a town in Pennsylvania
    rf"tel{SEP}hai",
    r"capernaum",
    rf"kibbutz\s+\w+",
    r"shefayim",
    r"gush dan",
    rf"mahoz{SEP}tzafon|hamerkaz",
]

ISRAEL_PATTERN = re.compile(
    r"(?<!beth )\bisrael\b"  # "Beth Israel" is a Boston hospital chain with ~2,000 open jobs
    r"|\b(TLV|ISR)\b"  # Tel Aviv airport code, Israel's ISO country code
    r"|[֐-׿]"  # any Hebrew text
    r"|\b(" + "|".join(ISRAELI_PLACES) + r")\b",
    re.IGNORECASE,
)


def is_israel(location: str) -> bool:
    return ISRAEL_PATTERN.search(location) is not None
