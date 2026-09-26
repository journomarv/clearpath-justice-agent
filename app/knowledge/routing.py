"""
ClearPath conversational routing.

Routing is conversational triage only. It does not determine legal
eligibility.

The router identifies:
- question type
- justice pathway
- user intent
- requested knowledge source categories

Legal eligibility remains the responsibility of the rules engine.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Route:
    """Non-legal routing result for a user message."""

    question_type: str
    pathway: str
    intent: str
    source_categories: List[str]


class KnowledgeRouter:
    """Conservative keyword-based router for ClearPath conversations."""

    PATHWAY_KEYWORDS = {
        "cannabis_related_relief": [
            "cannabis",
            "dagga",
            "marijuana",
            "weed",
            "cppa",
            "private purposes act",
        ],
        "child_justice": [
            "child justice",
            "juvenile",
            "under 18",
            "under-18",
            "when i was a child",
            "when i was under 18",
            "convicted as a child",
            "childhood conviction",
            "j763",
            "schedule 1",
            "schedule 2",
            "diversion",
        ],
        "police_clearance": [
            "police clearance",
            "police clearance certificate",
            "police clearance report",
            "pcc",
            "pcr",
            "saps clearance",
            "criminal record centre",
            "criminal record centres",
            "crc",
        ],
        "general_expungement": [
            "expungement",
            "expunge",
            "criminal record",
            "criminal record removal",
            "criminal record relief",
            "clear my record",
            "remove my record",
            "previous conviction",
            "old conviction",
            "criminal conviction",
            "criminal record clean",
        ],
    }

    SOURCE_KEYWORDS = {
        "parliament": [
            "parliament",
            "hansard",
            "bill",
            "committee",
            "legislation",
            "according to parliament",
            "what happened in parliament",
        ],
        "case_law": [
            "case law",
            "judgment",
            "judgement",
            "court decision",
            "court case",
            "saflii",
            "prince judgment",
            "prince judgement",
        ],
        "law_reform": [
            "law reform",
            "south african law reform commission",
            "salrc",
            "discussion paper",
            "issue paper",
        ],
        "academic": [
            "academic",
            "research",
            "study",
            "paper",
            "journal",
            "thesis",
            "dissertation",
            "university",
        ],
        "datasets": [
            "dataset",
            "data",
            "statistics",
            "statistics south africa",
            "stats sa",
            "saps crime statistics",
        ],
        "news": [
            "news",
            "latest",
            "recent",
            "reported",
            "article",
        ],
        "civil_society": [
            "civil society",
            "ngo",
            "nonprofit",
            "legal aid",
            "legal assistance",
            "advocacy",
        ],
        "local_government": [
            "municipality",
            "municipal",
            "local government",
            "provincial government",
            "library",
            "community centre",
            "community center",
        ],
    }

    PERSONAL_MARKERS = [
        "my",
        "i ",
        "i'm",
        "ive",
        "i've",
        "me ",
        "was convicted",
        "was arrested",
        "my conviction",
        "my record",
        "my application",
        "my case",
    ]

    RESEARCH_MARKERS = [
        "research",
        "study",
        "history",
        "how was",
        "why was",
        "when was",
        "statistics",
        "data",
        "parliament",
        "hansard",
        "bill",
        "committee",
        "according to",
        "evidence",
        "literature",
    ]

    CANNABIS_RESEARCH_MARKERS = [
        "cannabis history",
        "dagga history",
        "history of cannabis",
        "history of dagga",
        "how was cannabis criminalised",
        "how was cannabis criminalized",
        "why was cannabis criminalised",
        "why was cannabis criminalized",
        "when was cannabis criminalised",
        "when was cannabis criminalized",
        "cannabis policing",
        "dagga policing",
        "cannabis criminalisation",
        "cannabis criminalization",
        "dagga criminalisation",
        "dagga criminalization",
        "criminalisation of cannabis",
        "criminalization of cannabis",
        "cannabis prohibition",
        "cannabis and apartheid",
        "apartheid and cannabis",
        "dagga and apartheid",
        "cannabis and segregation",
        "dagga and segregation",
        "racialisation of cannabis",
        "racialization of cannabis",
        "cannabis arrests",
        "dagga arrests",
        "cannabis prosecutions",
        "dagga prosecutions",
        "1952 committee",
        "abuse of dagga",
        "prince case",
        "cannabis for private purposes act",
        "private purposes act",
    ]

    NON_CANNABIS_OFFENCES = [
        "theft",
        "fraud",
        "assault",
        "robbery",
        "burglary",
        "shoplifting",
        "forgery",
        "drug dealing",
        "drug trafficking",
    ]

    INTENT_KEYWORDS = {
        "tracking": [
            "track",
            "tracking",
            "status",
            "where is my application",
            "follow up",
            "follow-up",
            "how long",
            "still waiting",
            "waiting",
            "submitted my application",
            "application submitted",
            "application received",
            "processing",
            "backlog",
        ],
        "application_prep": [
            "what documents",
            "documents",
            "supporting documents",
            "what form",
            "application form",
            "prepare my application",
            "how do i apply",
            "how can i apply",
            "where do i apply",
            "application checklist",
            "checklist",
        ],
        "post_decision": [
            "approved",
            "approval",
            "refused",
            "rejected",
            "refusal",
            "decision",
            "expungement certificate",
            "after expungement",
            "after approval",
            "after refusal",
            "record removed",
            "record cleared",
        ],
    }

    PATHWAY_ORDER = [
        "child_justice",
        "police_clearance",
        "cannabis_related_relief",
        "general_expungement",
    ]

    def identify_question_type(self, message: str) -> str:
        text = message.lower().strip()

        if any(marker in text for marker in self.PERSONAL_MARKERS):
            return "personal_justice"

        if any(marker in text for marker in self.RESEARCH_MARKERS):
            return "justice_research"

        if any(marker in text for marker in self.CANNABIS_RESEARCH_MARKERS):
            return "justice_research"

        return "general_justice"

    def identify_pathway(self, message: str) -> str:
        text = message.lower().strip()

        if any(offence in text for offence in self.NON_CANNABIS_OFFENCES):
            if not any(
                phrase in text
                for phrase in [
                    "cannabis offence",
                    "cannabis conviction",
                    "cannabis charge",
                    "cannabis possession",
                    "cannabis-related",
                ]
            ):
                return "general_expungement"

        for pathway in self.PATHWAY_ORDER:
            if any(
                keyword in text
                for keyword in self.PATHWAY_KEYWORDS[pathway]
            ):
                return pathway

        return "unknown"

    def identify_intent(self, message: str) -> str:
        text = message.lower().strip()

        # Tracking must be checked before application preparation because
        # phrases such as "my application is still waiting" contain the
        # generic word "application" but clearly describe status/tracking.
        for intent in ["tracking", "application_prep", "post_decision"]:
            if any(
                keyword in text
                for keyword in self.INTENT_KEYWORDS[intent]
            ):
                return intent

        return "eligibility"

    def identify_source_categories(self, message: str) -> List[str]:
        text = message.lower().strip()
        categories: List[str] = []

        for category, keywords in self.SOURCE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)

        return categories

    def route(self, message: str) -> Route:
        return Route(
            question_type=self.identify_question_type(message),
            pathway=self.identify_pathway(message),
            intent=self.identify_intent(message),
            source_categories=self.identify_source_categories(message),
        )


router = KnowledgeRouter()


def route_message(message: str) -> Route:
    """Route a message using the shared ClearPath knowledge router."""
    return router.route(message)
