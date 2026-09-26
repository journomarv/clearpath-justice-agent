"""
ClearPath knowledge retrieval.

This module maps conversational routing results to the Markdown knowledge
base. Retrieval is evidence gathering only; it does not determine legal
eligibility.

Architecture:
    user message
        -> KnowledgeRouter
        -> KnowledgeRetriever
        -> bounded knowledge context
        -> rules engine (where applicable)
        -> LLM explanation

AI assists; it does not adjudicate.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from app.knowledge.routing import Route
from app.knowledge.sources import get_source


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[2] / "knowledge"


PATHWAY_FILES = {
    "cannabis_related_relief": "pathways/cannabis_related_relief.md",
    "general_expungement": "pathways/general_expungement.md",
    "child_justice": "pathways/child_justice.md",
    "police_clearance": "pathways/police_clearance.md",
}

INTENT_FILES = {
    "application_prep": "pathways/application_prep.md",
    "tracking": "pathways/tracking.md",
    "post_decision": "pathways/post_decision.md",
}

SOURCE_FILES = {
    "parliament": "sources/parliament_pmg.md",
    "case_law": "sources/case_law_saflii.md",
    "law_reform": "sources/law_reform_salrc.md",
    "academic": "sources/academic_research.md",
    "datasets": "sources/justice_data.md",
    "news": "sources/news.md",
    "civil_society": "sources/civil_society.md",
    "local_government": "sources/local_government.md",
}


@dataclass(frozen=True)
class RetrievedKnowledge:
    """Knowledge retrieved for one conversational turn."""

    sections: List[str]
    source_ids: List[str]

    @property
    def context(self) -> str:
        if not self.sections:
            return ""

        return "\n\n".join(self.sections)


class KnowledgeRetriever:
    """Retrieve bounded Markdown knowledge based on a conversational route."""

    def _read(self, relative_path: str) -> str:
        path = KNOWLEDGE_ROOT / relative_path

        if not path.is_file():
            return ""

        return path.read_text(encoding="utf-8").strip()

    def _add_file(
        self,
        sections: List[str],
        relative_path: str,
        heading: str,
    ) -> None:
        content = self._read(relative_path)

        if content:
            sections.append(
                f"===== {heading} =====\n{content}"
            )

    def _source_ids_for_categories(
        self,
        categories: List[str],
    ) -> List[str]:
        ids: List[str] = []

        for category in categories:
            source = get_source(category)
            if source and source.id not in ids:
                ids.append(source.id)

        return ids

    def retrieve(self, route: Route) -> RetrievedKnowledge:
        sections: List[str] = []
        source_ids: List[str] = []

        # Safeguards apply to every Path conversation.
        self._add_file(
            sections,
            "safeguards/ai_principles.md",
            "AI PRINCIPLES",
        )
        self._add_file(
            sections,
            "safeguards/uncertainty.md",
            "UNCERTAINTY AND VERIFICATION",
        )

        # Personal justice navigation.
        if route.pathway in PATHWAY_FILES:
            self._add_file(
                sections,
                PATHWAY_FILES[route.pathway],
                f"PATHWAY: {route.pathway}",
            )

        if route.intent in INTENT_FILES:
            self._add_file(
                sections,
                INTENT_FILES[route.intent],
                f"INTENT: {route.intent}",
            )

        if route.pathway in {
            "general_expungement",
            "child_justice",
            "cannabis_related_relief",
            "police_clearance",
        }:
            self._add_file(
                sections,
                "legal_framework/criminal_record_relief.md",
                "GENERAL LEGAL FRAMEWORK",
            )

        # Cannabis research gets the historical evidence collection.
        if (
            route.pathway == "cannabis_related_relief"
            and route.question_type == "justice_research"
        ):
            self._add_file(
                sections,
                "history/cannabis_sa/south_africa_cannabis_history.md",
                "CANNABIS HISTORY",
            )
            self._add_file(
                sections,
                "research/cannabis_sa/cannabis_policy_timeline.md",
                "CANNABIS POLICY TIMELINE",
            )
            self._add_file(
                sections,
                "legal_framework/cannabis/prince_2018.md",
                "PRINCE JUDGMENT",
            )
            self._add_file(
                sections,
                "sources/cannabis_sa/nkosi_devey_waetjen_2020.md",
                "CANNABIS ACADEMIC SOURCE",
            )

        # Parliamentary research gets the dedicated expungement index.
        if (
            route.question_type == "justice_research"
            and "parliament" in route.source_categories
        ):
            self._add_file(
                sections,
                "research/parliament_expungement_index.md",
                "PARLIAMENT EXPUNGEMENT EVIDENCE INDEX",
            )

        # General research source material.
        if route.question_type == "justice_research":
            for category in route.source_categories:
                relative_path = SOURCE_FILES.get(category)

                if relative_path:
                    self._add_file(
                        sections,
                        relative_path,
                        f"SOURCE CATEGORY: {category}",
                    )

            source_ids.extend(
                self._source_ids_for_categories(
                    route.source_categories
                )
            )

        return RetrievedKnowledge(
            sections=sections,
            source_ids=source_ids,
        )


retriever = KnowledgeRetriever()


def retrieve_knowledge(route: Route) -> RetrievedKnowledge:
    """Retrieve knowledge for a routed conversational turn."""
    return retriever.retrieve(route)
