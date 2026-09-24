from pathlib import Path
from typing import Any


class KnowledgeService:
    """
    Path knowledge retrieval service.

    Path separates:
    - personal justice navigation
    - justice research
    - general justice questions

    Within personal justice navigation, Path also separates:
    - matter/pathway
    - user intent

    Knowledge sources include:
    - parliamentary material
    - case law
    - law reform
    - academic research
    - datasets
    - news
    - local government
    - civil society
    - historical research
    - safeguards
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
        "cannabis_history": [
            "cannabis history",
            "dagga history",
            "history of cannabis",
            "history of dagga",
            "cannabis policing",
            "dagga policing",
            "cannabis criminalisation",
            "cannabis criminalization",
            "dagga criminalisation",
            "dagga criminalization",
            "cannabis prohibition",
            "history of cannabis prohibition",
            "history of cannabis criminalisation",
            "history of cannabis criminalization",
            "cannabis and apartheid",
            "dagga and apartheid",
            "cannabis and segregation",
            "dagga and segregation",
            "cannabis arrests",
            "dagga arrests",
            "cannabis prosecutions",
            "dagga prosecutions",
            "1952 committee",
            "abuse of dagga",
            "prince judgment",
            "prince judgement",
            "prince case",
            "cannabis for private purposes act",
            "private purposes act",
            "cppa",
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

    CANNABIS_HISTORY_FILES = [
        "history/cannabis_sa/south_africa_cannabis_history.md",
        "research/cannabis_sa/cannabis_policy_timeline.md",
        "legal_framework/cannabis/prince_2018.md",
        "sources/cannabis_sa/nkosi_devey_waetjen_2020.md",
    ]

    def identify_question_type(self, message: str) -> str:
        """
        Separate personal justice navigation from broader justice research.
        """

        text = message.lower().strip()

        personal_markers = [
            "my record",
            "my conviction",
            "my application",
            "my expungement",
            "my criminal record",
            "i was convicted",
            "i have a conviction",
            "can i expunge",
            "can i clear my record",
            "can i remove my record",
            "what documents do i need",
            "where do i apply",
            "how do i apply",
            "how can i apply",
            "my police clearance",
        ]

        research_markers = [
            "parliament",
            "hansard",
            "committee",
            "bill",
            "legislation",
            "law reform",
            "judgment",
            "judgement",
            "court case",
            "case law",
            "research",
            "study",
            "statistics",
            "data",
            "policy",
            "government said",
            "government has said",
            "government report",
            "how many times",
            "how many",
            "how often",
            "what has parliament",
            "what did parliament",
            "what happened in parliament",
            "according to parliament",
        ]

        cannabis_research_markers = [
            "cannabis history",
            "dagga history",
            "history of cannabis",
            "history of dagga",
            "cannabis policing",
            "dagga policing",
            "cannabis criminalisation",
            "cannabis criminalization",
            "dagga criminalisation",
            "dagga criminalization",
            "cannabis prohibition",
            "cannabis and apartheid",
            "dagga and apartheid",
            "cannabis and segregation",
            "dagga and segregation",
            "cannabis arrests",
            "dagga arrests",
            "cannabis prosecutions",
            "dagga prosecutions",
            "1952 committee",
            "abuse of dagga",
            "prince judgment",
            "prince judgement",
            "prince case",
            "cannabis for private purposes act",
            "private purposes act",
        ]

        if any(marker in text for marker in personal_markers):
            return "personal_justice"

        if any(marker in text for marker in research_markers):
            return "justice_research"

        if any(marker in text for marker in cannabis_research_markers):
            return "justice_research"

        return "general_justice"

    def identify_pathway(self, message: str) -> str:
        text = message.lower().strip()

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

        if any(
            keyword in text
            for keyword in [
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
            ]
        ):
            return "tracking"

        if any(
            keyword in text
            for keyword in [
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
            ]
        ):
            return "application_prep"

        if any(
            keyword in text
            for keyword in [
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
            ]
        ):
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

    def _load_cannabis_history(self) -> list[dict[str, Any]]:
        """
        Load the dedicated South African cannabis history collection.
        """

        documents: list[dict[str, Any]] = []

        for relative_path in self.CANNABIS_HISTORY_FILES:
            path = self.KNOWLEDGE_DIR / relative_path
            document = self._load_document(path)

            if document:
                document["source_category"] = "cannabis_history"
                documents.append(document)

        return documents

    def retrieve(
        self,
        message: str,
        pathway: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve knowledge according to the type of question.

        Personal justice:
            matter + intent + safeguards

        Justice research:
            requested source categories + research indexes + safeguards

        General justice:
            relevant source categories + legal framework + safeguards
        """

        question_type = self.identify_question_type(message)

        detected_pathway = pathway or self.identify_pathway(message)
        intent = self.identify_intent(message)

        documents: list[dict[str, Any]] = []

        common_files = [
            self.KNOWLEDGE_DIR / "safeguards" / "ai_principles.md",
            self.KNOWLEDGE_DIR / "safeguards" / "uncertainty.md",
        ]

        for path in common_files:
            document = self._load_document(path)

            if document:
                document["source_category"] = "safeguards"
                documents.append(document)

        # Research questions get research-specific evidence first.
        if question_type == "justice_research":
            source_categories = self.identify_source_categories(message)

            text = message.lower()

            # Parliament is especially important for questions about
            # Parliament, Hansard, Bills, committees and legislative history.
            if (
                "parliament" in text
                or "hansard" in text
                or "bill" in text
                or "committee" in text
            ):
                if "parliament" not in source_categories:
                    source_categories.insert(0, "parliament")

            # Load the dedicated cannabis history collection whenever
            # the question concerns South African cannabis history,
            # policing, criminalisation or the transition to the current law.
            cannabis_history_markers = [
                "cannabis",
                "dagga",
                "marijuana",
                "prince",
                "private purposes act",
                "cppa",
            ]

            if any(marker in text for marker in cannabis_history_markers):
                if "cannabis_history" not in source_categories:
                    source_categories.insert(0, "cannabis_history")

            for category in source_categories:
                if category == "cannabis_history":
                    documents.extend(self._load_cannabis_history())
                    continue

                document = self._load_source_category(category)

                if document:
                    documents.append(document)

            # Existing parliamentary research index remains available.
            research_index = (
                self.KNOWLEDGE_DIR
                / "research"
                / "parliament_expungement_index.md"
            )

            if research_index.exists():
                document = self._load_document(research_index)

                if document:
                    document["source_category"] = "research_index"
                    documents.append(document)

            # Give research questions the broader legal framework as context.
            framework = (
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "criminal_record_relief.md"
            )

            document = self._load_document(framework)

            if document:
                document["source_category"] = "legal_framework"
                documents.append(document)

            return documents

        # Personal justice navigation.
        filename = self.PATHWAY_FILES.get(detected_pathway)

        if filename:
            pathway_path = (
                self.KNOWLEDGE_DIR
                / "pathways"
                / filename
            )

            document = self._load_document(pathway_path)

            if document:
                document["source_category"] = "pathway"
                document["pathway"] = detected_pathway
                documents.append(document)

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
