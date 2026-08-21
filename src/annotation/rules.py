import re


ENTITY_RULES = {
    "DATE": [
        re.compile(
            r"\b(?:19|20)\d{2}\b"
        ),
        re.compile(
            r"\b(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+\d{1,2},\s+(?:19|20)\d{2}\b"
        ),
        re.compile(
            r"\b(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+(?:19|20)\d{2}\b"
        ),
    ],

    "MONEY": [
        re.compile(
            r"\$\s?\d+(?:\.\d+)?\s?"
            r"(?:million|billion|trillion|thousand)?\b",
            re.IGNORECASE,
        ),
    ],

    "PERCENTAGE": [
        re.compile(
            r"\b\d+(?:\.\d+)?\s?%"
        ),
        re.compile(
            r"\b\d+(?:\.\d+)?\s?percent\b",
            re.IGNORECASE,
        ),
    ],
}


ENTITY_DICTIONARIES = {
    "ORGANIZATION": [
        "Microsoft",
        "Microsoft Corporation",
        "OpenAI",
        "SEC",
    ],

    "PRODUCT": [
        "Microsoft 365",
        "Azure",
        "Windows",
        "LinkedIn",
        "GitHub",
        "Xbox",
        "Office",
        "Teams",
    ],
}