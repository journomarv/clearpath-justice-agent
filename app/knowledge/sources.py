"""
Path verified source registry.

This registry records where information comes from.

Important distinction:

A source can be authoritative enough to cite without being approved
for automated eligibility decisions.

For example:
- an official DOJ page may be cited;
- a parliamentary discussion may describe a proposed change;
- an academic paper may provide research evidence;
- a news article may report a development.

None of those automatically changes Path's legal rules.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    OFFICIAL = "official"
    PARLIAMENTARY = "parliamentary"
    CASE_LAW = "case_law"
    LAW_REFORM = "law_reform"
    ACADEMIC = "academic"
    DATASET = "dataset"
    NEWS = "news"
    CIVIL_SOCIETY = "civil_society"
    LOCAL_GOVERNMENT = "local_government"
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
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None

    geography: Optional[str] = None
    topic: Optional[str] = None

    content_verified_for_automation: bool = False

    notes: Optional[str] = None


SOURCE_REGISTRY: Dict[str, KnowledgeSource] = {

    # ---------------------------------------------------------
    # OFFICIAL GOVERNMENT
    # ---------------------------------------------------------

    "doj_expungements_overview": KnowledgeSource(
        id="doj_expungements_overview",
        title="Expungement of a Criminal Record",
        organization="Department of Justice and Constitutional Development",
        source_type=SourceType.OFFICIAL,
        url="https://justice.gov.za/expungements.html",
        topic="expungement",
        notes=(
            "Official citizen-facing information about the expungement "
            "process. Use as an official process source. Do not treat "
            "the page alone as authority for automated eligibility logic."
        ),
    ),

    "gov_za_expungement": KnowledgeSource(
        id="gov_za_expungement",
        title="Apply for expungement of your criminal record",
        organization="South African Government",
        source_type=SourceType.OFFICIAL,
        url="https://www.gov.za/node/778102",
        topic="expungement",
        notes=(
            "Official citizen-facing government information."
        ),
    ),

    "saps": KnowledgeSource(
        id="saps",
        title="South African Police Service",
        organization="South African Police Service",
        source_type=SourceType.OFFICIAL,
        url="https://www.saps.gov.za/",
        topic="policing",
        notes=(
            "Official SAPS source for policing information and "
            "publicly released statistics."
        ),
    ),

    # ---------------------------------------------------------
    # PARLIAMENT / PMG
    # ---------------------------------------------------------

    "parliament": KnowledgeSource(
        id="parliament",
        title="Parliament of the Republic of South Africa",
        organization="Parliament of South Africa",
        source_type=SourceType.PARLIAMENTARY,
        url="https://www.parliament.gov.za/",
        topic="parliament",
        notes=(
            "Primary source for parliamentary legislative and oversight "
            "activity."
        ),
    ),

    "pmg": KnowledgeSource(
        id="pmg",
        title="Parliamentary Monitoring Group",
        organization="Parliamentary Monitoring Group",
        source_type=SourceType.PARLIAMENTARY,
        url="https://pmg.org.za/",
        topic="parliament",
        notes=(
            "Use for committee meetings, bills, parliamentary questions, "
            "replies, submissions, hearings, Hansards and reports. "
            "PMG material describes parliamentary activity; it does not "
            "itself amend the law."
        ),
    ),

    # ---------------------------------------------------------
    # CASE LAW
    # ---------------------------------------------------------

    "saflii": KnowledgeSource(
        id="saflii",
        title="South African Legal Information Institute",
        organization="SAFLII",
        source_type=SourceType.CASE_LAW,
        url="https://www.saflii.org/",
        topic="case law",
        notes=(
            "Use for South African judgments and judicial interpretation. "
            "Always identify the court, case name and date where possible."
        ),
    ),

    # ---------------------------------------------------------
    # LAW REFORM
    # ---------------------------------------------------------

    "salrc": KnowledgeSource(
        id="salrc",
        title="South African Law Reform Commission",
        organization="South African Law Reform Commission",
        source_type=SourceType.LAW_REFORM,
        url="https://www.justice.gov.za/salrc/",
        topic="law reform",
        notes=(
            "Use for law-reform projects, discussion papers, issue papers "
            "and recommendations."
        ),
    ),

    "salrc_expungement_project": KnowledgeSource(
        id="salrc_expungement_project",
        title="Project 151: Review of the Criminal Procedure Act",
        organization="South African Law Reform Commission",
        source_type=SourceType.LAW_REFORM,
        url="https://www.justice.gov.za/salrc/projects/project151.html",
        topic="expungement",
        notes=(
            "Includes Discussion Paper 179: Expungement of Criminal Records. "
            "A discussion paper is law-reform material and should not be "
            "presented as enacted law."
        ),
    ),

    # ---------------------------------------------------------
    # ACADEMIC RESEARCH
    # ---------------------------------------------------------

    "academic_research": KnowledgeSource(
        id="academic_research",
        title="Academic research on criminal records and justice",
        organization="South African universities and research institutions",
        source_type=SourceType.ACADEMIC,
        topic="criminal records",
        notes=(
            "Prioritise peer-reviewed South African research, university "
            "repositories, theses, dissertations and research reports."
        ),
    ),

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    "datafirst": KnowledgeSource(
        id="datafirst",
        title="DataFirst",
        organization="University of Cape Town",
        source_type=SourceType.DATASET,
        url="https://www.datafirst.uct.ac.za/",
        topic="justice data",
        notes=(
            "Use for research datasets and metadata. Prefer aggregate or "
            "appropriately anonymised data."
        ),
    ),

    "saps_crime_records": KnowledgeSource(
        id="saps_crime_records",
        title="SAPS Annual Crime Records",
        organization="South African Police Service",
        source_type=SourceType.DATASET,
        url="https://www.saps.gov.za/",
        topic="crime statistics",
        notes=(
            "Police-recorded crime data is not equivalent to arrests, "
            "convictions or proof of guilt."
        ),
    ),

    "stats_sa": KnowledgeSource(
        id="stats_sa",
        title="Statistics South Africa",
        organization="Statistics South Africa",
        source_type=SourceType.DATASET,
        url="https://www.statssa.gov.za/",
        topic="official statistics",
        notes=(
            "Use for official demographic, population, labour and "
            "socio-economic statistics."
        ),
    ),

    # ---------------------------------------------------------
    # NEWS
    # ---------------------------------------------------------

    "news": KnowledgeSource(
        id="news",
        title="South African justice and public-interest news",
        organization="Multiple publishers",
        source_type=SourceType.NEWS,
        topic="current affairs",
        notes=(
            "News is time-sensitive. Always retain publication date and "
            "publisher. News reporting must not be presented as primary law."
        ),
    ),

    # ---------------------------------------------------------
    # CIVIL SOCIETY
    # ---------------------------------------------------------

    "civil_society": KnowledgeSource(
        id="civil_society",
        title="Civil society and legal assistance organisations",
        organization="Multiple organisations",
        source_type=SourceType.CIVIL_SOCIETY,
        topic="access to justice",
        notes=(
            "Useful for practical barriers, referrals, research and "
            "community-level evidence. Do not treat advocacy positions "
            "as official government policy."
        ),
    ),

    # ---------------------------------------------------------
    # LOCAL GOVERNMENT
    # ---------------------------------------------------------

    "local_government": KnowledgeSource(
        id="local_government",
        title="South African local and provincial government services",
        organization="Municipal and provincial governments",
        source_type=SourceType.LOCAL_GOVERNMENT,
        topic="local services",
        notes=(
            "Use for local service points, libraries, digital access, "
            "community programmes and referrals. Local government is not "
            "the national authority on criminal-record expungement."
        ),
    ),

    # ---------------------------------------------------------
    # CLEARPATH
    # ---------------------------------------------------------

    "clearpath_referrals": KnowledgeSource(
        id="clearpath_referrals",
        title="ClearPath Justice referral organisations",
        organization="ClearPath Justice",
        source_type=SourceType.CURATED,
        topic="referrals",
        notes=(
            "Curated ClearPath referral information. Must be periodically "
            "reviewed for accuracy."
        ),
    ),
}


def get_source(source_id: str) -> Optional[KnowledgeSource]:
    return SOURCE_REGISTRY.get(source_id)


def get_sources(
    source_ids: List[str],
) -> List[KnowledgeSource]:
    return [
        SOURCE_REGISTRY[source_id]
        for source_id in source_ids
        if source_id in SOURCE_REGISTRY
    ]


def list_sources_by_type(
    source_type: SourceType,
) -> List[KnowledgeSource]:
    return [
        source
        for source in SOURCE_REGISTRY.values()
        if source.source_type == source_type
    ]


def list_unverified_sources() -> List[KnowledgeSource]:
    return [
        source
        for source in SOURCE_REGISTRY.values()
        if not source.content_verified_for_automation
    ]
