from pathlib import Path


class KnowledgeService:
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

    def identify_pathway(self, message: str) -> str:
        text = message.lower().strip()

        pathway_order = [
            "child_justice",
            "police_clearance",
            "application_prep",
            "tracking",
            "post_decision",
            "cannabis_related_relief",
            "general_expungement",
        ]

        for pathway in pathway_order:
            keywords = self.PATHWAY_KEYWORDS[pathway]

            if any(keyword in text for keyword in keywords):
                return pathway

        return "unknown"

    def _load_document(self, path: Path) -> dict[str, str] | None:
        if not path.exists():
            return None

        return {
            "source": str(path.relative_to(self.BASE_DIR)),
            "content": path.read_text(encoding="utf-8"),
        }

    def retrieve(
        self,
        message: str,
        pathway: str | None = None,
    ) -> list[dict[str, str]]:
        detected_pathway = pathway or self.identify_pathway(message)

        documents: list[dict[str, str]] = []

        common_files = [
            self.KNOWLEDGE_DIR / "safeguards" / "ai_principles.md",
            self.KNOWLEDGE_DIR / "safeguards" / "uncertainty.md",
        ]

        for path in common_files:
            document = self._load_document(path)
            if document:
                documents.append(document)

        filename = self.PATHWAY_FILES.get(detected_pathway)

        if filename:
            pathway_path = self.KNOWLEDGE_DIR / "pathways" / filename
            document = self._load_document(pathway_path)
            if document:
                documents.append(document)

        if detected_pathway == "unknown":
            fallback = (
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "criminal_record_relief.md"
            )

            document = self._load_document(fallback)
            if document:
                documents.append(document)

        return documents            "saps clearance",
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

    def identify_pathway(self, message: str) -> str:
        text = message.lower().strip()

        # More specific pathways should be detected before
        # the broad "general expungement" pathway.
        pathway_order = [
            "child_justice",
            "police_clearance",
            "application_prep",
            "tracking",
            "post_decision",
            "cannabis_related_relief",
            "general_expungement",
        ]

        for pathway in pathway_order:
            keywords = self.PATHWAY_KEYWORDS[pathway]

            if any(keyword in text for keyword in keywords):
                return pathway

        return "unknown"

    def _load_document(self, path: Path) -> dict[str, str] | None:
        if not path.exists():
            return None

        return {
            "source": str(path.relative_to(self.BASE_DIR)),
            "content": path.read_text(encoding="utf-8"),
        }

    def retrieve(
        self,
        message: str,
        pathway: str | None = None,
    ) -> list[dict[str, str]]:

        detected_pathway = pathway or self.identify_pathway(message)

        documents: list[dict[str, str]] = []

        # Always provide the AI safety layer.
        common_files = [
            self.KNOWLEDGE_DIR / "safeguards" / "ai_principles.md",
            self.KNOWLEDGE_DIR / "safeguards" / "uncertainty.md",
        ]

        for path in common_files:
            document = self._load_document(path)

            if document:
                documents.append(document)

        # Load the selected pathway.
        filename = self.PATHWAY_FILES.get(detected_pathway)

        if filename:
            pathway_path = self.KNOWLEDGE_DIR / "pathways" / filename
            document = self._load_document(pathway_path)

            if document:
                documents.append(document)

        # Preserve existing legal-framework knowledge for
        # unknown questions.
        if detected_pathway == "unknown":
            fallback = (
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "criminal_record_relief.md"
            )

            document = self._load_document(fallback)

            if document:
                documents.append(document)

        return documents        pathway: str | None = None,
    ) -> list[dict[str, str]]:

        detected_pathway = pathway or self.identify_pathway(message)

        documents: list[dict[str, str]] = []

        common_files = [
            self.KNOWLEDGE_DIR / "safeguards" / "ai_principles.md",
            self.KNOWLEDGE_DIR / "safeguards" / "uncertainty.md",
        ]

        for path in common_files:
            if path.exists():
                documents.append(
                    {
                        "source": str(path.relative_to(self.BASE_DIR)),
                        "content": path.read_text(
                            encoding="utf-8"
                        ),
                    }
                )

        if detected_pathway == "cannabis_related_relief":
            files = [
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "cannabis_related_relief.md",
                self.KNOWLEDGE_DIR
                / "expungement"
                / "eligibility.md",
                self.KNOWLEDGE_DIR
                / "expungement"
                / "process.md",
            ]
        elif detected_pathway == "general_expungement":
            files = [
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "general_expungement.md",
                self.KNOWLEDGE_DIR
                / "expungement"
                / "eligibility.md",
                self.KNOWLEDGE_DIR
                / "expungement"
                / "process.md",
            ]
        else:
            files = [
                self.KNOWLEDGE_DIR
                / "legal_framework"
                / "criminal_record_relief.md",
            ]

        for path in files:
            if path.exists():
                documents.append(
                    {
                        "source": str(path.relative_to(self.BASE_DIR)),
                        "content": path.read_text(
                            encoding="utf-8"
                        ),
                    }
                )

                return documents
