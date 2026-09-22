from pathlib import Path
import re


class KnowledgeService:
    BASE_DIR = Path(__file__).resolve().parents[2]
    KNOWLEDGE_DIR = BASE_DIR / "knowledge"

    PATHWAY_KEYWORDS = {
        "cannabis_related_relief": [
            "cannabis",
            "dagga",
            "marijuana",
            "weed",
            "possession of cannabis",
        ],
        "general_expungement": [
            "expungement",
            "criminal record",
            "criminal record removal",
            "criminal record relief",
        ],
    }

    def identify_pathway(self, message: str) -> str:
        text = message.lower()

        for pathway, keywords in self.PATHWAY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return pathway

        return "unknown"

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