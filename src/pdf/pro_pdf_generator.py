from __future__ import annotations

from pathlib import Path

from src.components.curiosity_box import (
    CuriosityData,
    draw_curiosity_box,
)
from src.components.footer import (
    FooterData,
    draw_footer,
)
from src.components.gs_mapping import (
    GSMappingItem,
    draw_gs_mapping,
)
from src.components.header import (
    HeaderData,
    draw_header,
)
from src.components.key_takeaway import (
    KeyTakeawayData,
    draw_key_takeaway,
)
from src.components.knowledge_points import (
    KnowledgePoint,
    KnowledgePointsData,
    draw_knowledge_points,
)
from src.components.mains_answer import (
    MainsAnswerData,
    draw_mains_answer,
)
from src.components.mcq_section import (
    MCQ,
    MCQData,
    draw_mcqs,
)
from src.components.quick_facts import (
    QuickFactsData,
    draw_quick_facts,
)
from src.knowledge_engine.knowledge_loader import (
    TopicRecord,
    load_topics,
)
from src.pdf.layout import (
    SHOW_FOOTER,
    SHOW_HEADER,
    draw_layout_box,
    draw_vertical_divider,
    get_full_page_layout,
)
from src.pdf.page_setup import (
    begin_page,
    create_canvas,
    finish_page,
)
from src.publication import (
    PublicationMetadata,
    build_publication_metadata,
)


# ============================================================
# REPORTLAB ANSWER FORMATTER
# ============================================================

def _answer_for_reportlab(
    answer: str,
) -> str:
    paragraphs = [
        paragraph.strip()
        for paragraph in (
            answer
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .split("\n\n")
        )
        if paragraph.strip()
    ]

    return "<br/><br/>".join(
        paragraphs
    )


# ============================================================
# SINGLE TOPIC PAGE
# ============================================================

def _draw_topic_page(
    canvas,
    topic: TopicRecord,
    page_number: int,
    total_pages: int,
    metadata: PublicationMetadata,
) -> None:
    begin_page(
        canvas,
    )

    layout = get_full_page_layout()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    if SHOW_HEADER:
        draw_header(
            canvas=canvas,
            rect=layout.header,
            data=HeaderData(
                title=metadata.title,
                subtitle=metadata.subtitle,
                publication_date=(
                    metadata.publication_date
                ),
                edition_code=metadata.edition_code,
            ),
            compact=False,
        )

    # --------------------------------------------------------
    # SECTION BOXES
    # --------------------------------------------------------

    for section_rect in (
        layout.question_panel,
        layout.knowledge_points,
        layout.quick_facts,
        layout.takeaway,
        layout.mains_answer,
        layout.mcqs,
    ):
        draw_layout_box(
            canvas=canvas,
            rect=section_rect,
        )

    draw_vertical_divider(
        canvas=canvas,
        x=layout.gs_mapping.x,
        y_bottom=layout.question_panel.y + 2,
        y_top=layout.question_panel.top - 2,
    )

    # --------------------------------------------------------
    # QUESTION + RECALL ANCHORS
    # --------------------------------------------------------

    draw_curiosity_box(
        canvas=canvas,
        rect=layout.curiosity_box,
        data=CuriosityData(
            question=topic.todays_question,
            anchors=topic.recall_anchors,
        ),
        compact=False,
    )

    # --------------------------------------------------------
    # GS MAPPING
    # --------------------------------------------------------

    draw_gs_mapping(
        canvas=canvas,
        rect=layout.gs_mapping,
        items=(
            GSMappingItem(
                paper=topic.gs_mapping.paper,
                subject=topic.gs_mapping.subject,
                topic=topic.gs_mapping.syllabus,
            ),
        ),
        compact=False,
    )

    # --------------------------------------------------------
    # KNOWLEDGE POINTS
    # --------------------------------------------------------

    draw_knowledge_points(
        canvas=canvas,
        rect=layout.knowledge_points,
        data=KnowledgePointsData(
            title="KNOWLEDGE POINTS",
            points=tuple(
                KnowledgePoint(
                    heading=point.heading,
                    explanation=point.explanation,
                )
                for point in topic.knowledge_points
            ),
        ),
    )

    # --------------------------------------------------------
    # QUICK FACTS
    # --------------------------------------------------------

    draw_quick_facts(
        canvas=canvas,
        rect=layout.quick_facts,
        data=QuickFactsData(
            title="QUICK FACTS",
            facts=topic.quick_facts,
        ),
    )

    # --------------------------------------------------------
    # KEY TAKEAWAY
    # --------------------------------------------------------

    draw_key_takeaway(
        canvas=canvas,
        rect=layout.takeaway,
        data=KeyTakeawayData(
            title="KEY TAKEAWAY",
            takeaway=topic.key_takeaway,
        ),
    )

    # --------------------------------------------------------
    # MAINS PERSPECTIVE
    # --------------------------------------------------------

    draw_mains_answer(
        canvas=canvas,
        rect=layout.mains_answer,
        data=MainsAnswerData(
            title="MAINS PERSPECTIVE",
            question=topic.mains_question,
            answer=_answer_for_reportlab(
                topic.mains_answer
            ),
        ),
    )

    # --------------------------------------------------------
    # DAILY MCQS
    # --------------------------------------------------------

    draw_mcqs(
        canvas=canvas,
        rect=layout.mcqs,
        data=MCQData(
            title="DAILY MCQs",
            questions=tuple(
                MCQ(
                    question=mcq.question,
                    options=mcq.options,
                    correct_option=(
                        mcq.correct_answer
                    ),
                    explanation=getattr(
                        mcq,
                        "explanation",
                        None,
                    ),
                )
                for mcq in topic.daily_mcqs
            ),
        ),
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    if SHOW_FOOTER:
        draw_footer(
            canvas=canvas,
            rect=layout.footer,
            data=FooterData(
                brand_name=metadata.footer_brand,
                publication_code=metadata.edition_code,
                page_number=page_number,
                total_pages=total_pages,
            ),
        )

    finish_page(
        canvas,
    )


# ============================================================
# PRO PDF GENERATOR
# ============================================================

def generate_pro_pdf(
    output_path: Path,
    metadata: PublicationMetadata | None = None,
) -> Path:
    topics = load_topics()

    if not topics:
        raise ValueError(
            "No topics were found in INPUT.json."
        )

    resolved_metadata = (
        metadata
        if metadata is not None
        else build_publication_metadata()
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    canvas = create_canvas(
        str(output_path),
    )

    total_pages = len(topics)

    for page_number, topic in enumerate(
        topics,
        start=1,
    ):
        _draw_topic_page(
            canvas=canvas,
            topic=topic,
            page_number=page_number,
            total_pages=total_pages,
            metadata=resolved_metadata,
        )

    canvas.save()

    return output_path


def generate_pro_pdf_preview(
    output_path: Path,
    metadata: PublicationMetadata | None = None,
) -> Path:
    return generate_pro_pdf(
        output_path=output_path,
        metadata=metadata,
    )