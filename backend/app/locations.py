import re

# Ported from greenhouse-radar, where it was tuned on real job data.
# "Beth Israel" is a Boston hospital chain with ~2,000 open jobs, so it must not match.
ISRAEL_PATTERN = re.compile(
    r"(?<!beth )israel|tel[\s-]?aviv|herzliya|haifa|jerusalem|petah|petach|ra'?anana|ramat[\s-]?gan|netanya|"
    r"yokneam|rehovot|be'?er[\s-]?sheva|hod[\s-]?hasharon|kfar[\s-]?saba|or[\s-]?yehuda|caesarea|"
    r"modi'?in|airport city|rosh ha'?ayin|givatayim|bnei brak|holon|\bTLV\b",
    re.IGNORECASE,
)


def is_israel(location: str) -> bool:
    return ISRAEL_PATTERN.search(location) is not None
