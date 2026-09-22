"""
Verified source registry for the knowledge base.

Every fact ClearPath surfaces to a user should be traceable to an entry
here. This registry does NOT contain legal conclusions or eligibility
criteria — it contains metadata about *where* information comes from, so
the agent (and any human reviewer) can see provenance at a glance.

Fields:
    source_type:
        OFFICIAL   — a .gov.za / justice.gov.za / saps.gov.za page or an
                     Act/Regulation itself.
        CURATED    — material ClearPath has written or compiled, e.g. a
                     plain-language explainer, pending legal sign-off.
        UNVERIFIED — anything not yet checked against a current source.
    content_verified_for_automation:
        True only once a ClearPath legal reviewer has confirmed the
        specific facts drawn from this source are current AND approved
        for use in automated eligibility logic (app/rules/). A source can
        be a perfectly legitimate OFFICIAL reference (safe to *cite* to a
        user) while this flag is still False (not yet safe to *encode* as
        pass/fail logic) — see app/rules/cannabis_cppa.py and
        app/rules/criminal_record_expungement.py for why that distinction
        matters.

PRINCIPLE: No invented South African law. Every URL below was located via
web search at build time and should be re-verified periodically, since
government sites do restructure.
"""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    OFFICIAL = "official"
    CURATED = "curated"
    UNVERIFIED = "unverified"


class KnowledgeSource(BaseModel):
    id: str
    title: str
    organization: str
    source_type: SourceType
    jurisdiction: str = "South Africa"
    url: Optional[str] = None
    verified_date: Optional[str] = None
    content_verified_for_automation: bool = False
    notes: Optional[str] = None


SOURCE_REGISTRY: Dict[str, KnowledgeSource] = {
    "cppa_act_7_2024": KnowledgeSource(
        id="cppa_act_7_2024",
        title="Cannabis for Private Purposes Act 7 of 2024",
        organization="Parliament of South Africa",
        source_type=SourceType.OFFICIAL,
        url=None,
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "TODO(legal-verification): add the official gazetted text URL "
            "and the specific section(s) relevant to expungement once "
            "confirmed by ClearPath legal. Do not cite specific section "
            "numbers to users until this is filled in."
        ),
    ),
    "doj_expungements_overview": KnowledgeSource(
        id="doj_expungements_overview",
        title="Expungement of a Criminal Record (Criminal Procedure Act, 1977)",
        organization="Department of Justice and Constitutional Development",
        source_type=SourceType.OFFICIAL,
        url="https://justice.gov.za/expungements.html",
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "Public overview page describing the general expungement "
            "process, the Form A / J744 application, and the SAPS "
            "Criminal Record Centre's role. Safe to cite as a pointer to "
            "the official process; NOT yet approved to encode specific "
            "numeric thresholds (waiting periods, fine amounts) into "
            "app/rules/ without legal sign-off, since these are subject "
            "to amendment."
        ),
    ),
    "gov_za_expungement_summary": KnowledgeSource(
        id="gov_za_expungement_summary",
        title="Apply for expungement of your criminal record",
        organization="South African Government (gov.za)",
        source_type=SourceType.OFFICIAL,
        url="https://www.gov.za/node/778102",
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "Citizen-facing summary of s271B criteria. Useful as a plain-"
            "language reference for the knowledge base; NOT wired into "
            "app/rules/ automated logic pending legal review."
        ),
    ),
    "cpa_1977_s271b": KnowledgeSource(
        id="cpa_1977_s271b",
        title="Criminal Procedure Act 51 of 1977, Section 271B",
        organization="Parliament of South Africa",
        source_type=SourceType.OFFICIAL,
        url=None,
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "TODO(legal-verification): add the current consolidated Act "
            "text URL (with amendments) once confirmed by ClearPath legal."
        ),
    ),
    "child_justice_act_s87": KnowledgeSource(
        id="child_justice_act_s87",
        title="Child Justice Act 75 of 2008, Section 87 (expungement)",
        organization="Parliament of South Africa",
        source_type=SourceType.OFFICIAL,
        url=None,
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "TODO(legal-verification): confirm applicability and add the "
            "current text URL / Form 13 (J763) link."
        ),
    ),
    "saps_criminal_record_centre": KnowledgeSource(
        id="saps_criminal_record_centre",
        title="Police clearance certificate (SAPS Criminal Record Centre)",
        organization="South African Police Service",
        source_type=SourceType.OFFICIAL,
        url=None,
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "TODO(knowledge): add the current SAPS page/process for "
            "requesting a police clearance certificate, which most relief "
            "types require as a supporting document."
        ),
    ),
    "clearpath_referral_organizations": KnowledgeSource(
        id="clearpath_referral_organizations",
        title="ClearPath partner / referral organisations",
        organization="ClearPath Justice",
        source_type=SourceType.CURATED,
        url=None,
        verified_date=None,
        content_verified_for_automation=False,
        notes=(
            "TODO(clearpath): populate with the current list of legal aid "
            "clinics, NGOs, and partner organisations that can take a "
            "referral, with contact details and intake criteria."
        ),
    ),
}


def get_source(source_id: str) -> Optional[KnowledgeSource]:
    return SOURCE_REGISTRY.get(source_id)


def get_sources(source_ids: List[str]) -> List[KnowledgeSource]:
    return [SOURCE_REGISTRY[sid] for sid in source_ids if sid in SOURCE_REGISTRY]


def list_unverified_sources() -> List[KnowledgeSource]:
    """Sources not yet cleared for use in automated eligibility logic."""
    return [s for s in SOURCE_REGISTRY.values() if not s.content_verified_for_automation]
