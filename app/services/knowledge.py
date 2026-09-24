from pathlib import Path
from typing import Any


class KnowledgeService:
    """
    Path knowledge retrieval service.

    Knowledge is organised into:
    - existing user pathways
    - source categories
    - safeguards
    - legal framework material

    Path should distinguish between law, official guidance, case law,
    research, parliamentary material, news and datasets.
    """

    BASE_DIR = Path(__file__).resolve().parents[2]
    KNOWLEDGE_DIR = BASE_DIR / "knowledge"

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
            "criminal records centre",
            "crc",
        ],
        "application_prep": [
            "application",
            "form j744",
            "form a",
            "j744",
            "documents",
            "supporting documents",
            "what documents",
            "prepare my application",
            "prepare",
            "checklist",
            "submit my application",
            "how do i apply",
            "application form",
        ],
        "tracking": [
            "track",
            "tracking",
            "status",
            "application status",
            "where is my application",
            "follow up",
            "follow-up",
            "how long",
            "still waiting",
            "submitted my application",
            "application submitted",
            "application received",
            "processing",
            "backlog",
        ],
        "post_decision": [
            "approved",
            "approval",
            "refused",
            "rejected",
            "refusal",
            "decision",
            "expungement certificate",
            "certificate",
            "after expungement",
            "after approval",
            "after refusal",
            "what happens next",
            "record removed",
            "record cleared",
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

    PATHWAY_FILES = {
        "cannabis_related_relief": "cannabis_related_relief.md",
        "child_justice": "child_justice.md",
        "police_clearance": "police_clearance.md",
        "application_prep": "application_prep.md",
        "tracking": "tracking.md",
        "post_decision": "post_decision.md",
        "general_expungement": "general_expungement.md",
    }

    SOURCE_KEYWORDS = {
    "parliament": [
        "parliament",
        "pmg",
        "portfolio committee",
        "select committee",
        "committee meeting",
        "committee report",
        "parliamentary question",
        "written reply",
        "public hearing",
        "public submission",
        "bill",
        "hansard",
    ],

    "case_law": [
        "saflii",
        "judgment",
        "judgement",
        "court case",
        "court judgment",
        "high court",
        "supreme court",
        "constitutional court",
        "appeal",
        "case law",
    ],

    "law_reform": [
        "south african law reform commission",
        "salrc",
        "law reform",
        "discussion paper",
        "issue paper",
        "project 151",
        "expungement of criminal records",
    ],

    "academic": [
        "academic research",
        "research paper",
        "journal article",
        "academic article",
        "university research",
        "thesis",
        "dissertation",
        "literature review",
        "criminology research",
        "criminal record and employment",
    ],

    "datasets": [
        "dataset",
        "data set",
        "statistics",
        "crime statistics",
        "saps statistics",
        "stats sa",
        "datafirst",
        "arrest data",
        "crime data",
        "municipality data",
        "population data",
        "corrections data",
        "court statistics",
    ],

    "news": [
        "news",
        "latest news",
        "recent news",
        "today",
        "this week",
        "latest",
        "breaking",
        "reported",
        "announcement",
        "media report",
    ],

    "local_government": [
        "municipality",
        "municipal",
        "metro",
        "local government",
        "local municipality",
        "ward",
        "province",
        "provincial government",
        "community centre",
        "library",
        "local services",
        "service point",
    ],

    "civil_society": [
        "civil society",
        "ngo",
        "nonprofit",
        "non-profit",
        "legal aid",
        "legal clinic",
        "advocacy",
        "human rights organisation",
        "research institute",
    ],
    }


    SOURCE_FILES = {
        "parliament": "parliament_pmg.md",
        "case_law": "case_law_saflii.md",
        "law_reform": "law_reform_salrc.md",
        "academic": "academic_research.md",
        "datasets": "justice_data.md",
        "news": "news.md",
        "local_government": "local_government.md",
        "civil_society": "civil_society.md",
    }

    def identify_pathway(self, message: str) -> str:
        text = message.lower().strip()

        # Matter-specific exclusions must be checked before broad
        # criminal-record keywords. This prevents a mention of
        # "cannabis" from hijacking a question that explicitly says
        # the conviction was for another offence.
        non_cannabis_offences = [
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

        if any(offence in text for offence in non_cannabis_offences):
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

        # More specific pathways should be evaluated before broad
        # application/record terminology.
        pathway_order = [
            "child_justice",
            "police_clearance",
            "cannabis_related_relief",
            "general_expungement",
        ]

        for pathway in pathway_order:
            if any(
                keyword in text
                for keyword in self.PATHWAY_KEYWORDS[pathway]
            ):
                return pathway

        return "unknown"

    def identify_intent(self, message: str) -> str:
        text = message.lower().strip()

        if any(keyword in text for keyword in [
            "track",
            "tracking",
            "status",
            "where is my application",
            "follow up",
            "follow-up",
            "how long",
            "still waiting",
            "submitted my application",
            "application submitted",
            "application received",
            "processing",
            "backlog",
        ]):
            return "tracking"

        if any(keyword in text for keyword in [
            "what documents",
            "documents",
            "supporting documents",
            "what form",
            "application form",
            "prepare my application",
            "how do i apply",
            "apply",
            "checklist",
        ]):
            return "application_prep"

        if any(keyword in text for keyword in [
            "approved",
            "approval",
            "refused",
            "rejected",
            "refusal",
            "decision",
            "after expungement",
            "after approval",
            "after refusal",
            "record removed",
            "record cleared",
        ]):
            return "post_decision"

        return "eligibility"

    def identify_source_categories(self, message: str) -> list[str]:
        text = message.lower().strip()
        categories: list[str] = []

        for category, keywords in self.SOURCE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)

        return categories

    def _load_document(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None

        return {
            "source": str(path.relative_to(self.BASE_DIR)),
            "content": path.read_text(encoding="utf-8"),
        }

    def _load_source_category(
        self,
        category: str,
    ) -> dict[str, Any] | None:
        filename = self.SOURCE_FILES.get(category)

        if not filename:
            return None

        path = self.KNOWLEDGE_DIR / "sources" / filename

        document = self._load_document(path)

        if document:
            document["source_category"] = category

        return document

    def retrieve(
        self,
        message: str,
        pathway: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve knowledge using two dimensions:

        1. Matter/pathway:
           - cannabis-related relief
           - child justice
           - police clearance
           - general expungement

        2. User intent:
           - eligibility
           - application preparation
           - tracking
           - post-decision

        This prevents an intent such as "how long?" or
        "what documents?" from replacing the underlying matter.
        """
        detected_pathway = pathway or self.identify_pathway(message)
        intent = self.identify_intent(message)

        documents: list[dict[str, Any]] = []

        # Always load safeguards.
        common_files = [
            self.KNOWLEDGE_DIR / "safeguards" / "ai_principles.md",
            self.KNOWLEDGE_DIR / "safeguards" / "uncertainty.md",
        ]

        for path in common_files:
            document = self._load_document(path)

            if document:
                document["source_category"] = "safeguards"
                documents.append(document)

        # Load matter-specific knowledge.
        filename = self.PATHWAY_FILES.get(detected_pathway)

        if filename:
            pathway_path = self.KNOWLEDGE_DIR / "pathways" / filename

            document = self._load_document(pathway_path)

            if document:
                document["source_category"] = "pathway"
                document["pathway"] = detected_pathway
                documents.append(document)

        # Load intent-specific knowledge.
        intent_filename = {
            "application_prep": "application_prep.md",
            "tracking": "tracking.md",
            "post_decision": "post_decision.md",
        }.get(intent)

        if intent_filename:
            intent_path = (
                self.KNOWLEDGE_DIR
                / "pathways"
                / intent_filename
            )

            document = self._load_document(intent_path)

            if document:
                document["source_category"] = "intent"
                document["intent"] = intent
                documents.append(document)

        # If the matter is unknown, provide the general legal framework.
        if detected_pathway == "unknown":
            fallback = (
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "criminal_record_relief.md"
            )

            document = self._load_document(fallback)

            if document:
                document["source_category"] = "legal_framework"
                documents.append(document)

        return documents

    def get_knowledge_context(
        self,
        message: str,
        pathway: str | None = None,
    ) -> str:
        """
        Build a compact context block for the language model.
        """
        documents = self.get_relevant_documents(
            message=message,
            pathway=pathway,
        )

        if not documents:
            return ""

        context_parts = []

        for document in documents:
            title = document.get("title", "Untitled source")
            source = document.get("source", "")
            content = document.get("content", "")

            section = f"### {title}"

            if source:
                section += f"\nSource: {source}"

            if content:
                section += f"\n{content}"

            context_parts.append(section)

        return "\n\n".join(context_parts)
