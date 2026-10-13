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
from src.components.concept_unfold import (
    ConceptUnfoldConsequence,
    ConceptUnfoldData,
    draw_concept_unfold,
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
from src.pdf.pro_text_formatter import (
    bold_italic_text,
    bold_knowledge_heading,
    bold_recall_anchors,
)
from src.publication import (
    PublicationMetadata,
    build_publication_metadata,
)


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

    return "<br/><br/>".join(paragraphs)


def _pro_text(
    text: str,
    anchors,
) -> str:
    return bold_recall_anchors(
        text=text,
        anchors=anchors,
    )


def _pro_options(
    options: tuple[str, str, str, str],
    anchors,
) -> tuple[str, str, str, str]:
    return tuple(
        _pro_text(option, anchors)
        for option in options
    )


def _draw_topic_page(
    canvas,
    topic: TopicRecord,
    page_number: int,
    total_pages: int,
    metadata: PublicationMetadata,
) -> None:
    begin_page(canvas)

    layout = get_full_page_layout()
    anchors = topic.recall_anchors

    if SHOW_HEADER:
        draw_header(
            canvas=canvas,
            rect=layout.header,
            data=HeaderData(
                title=metadata.title,
                subtitle=metadata.subtitle,
                publication_date=metadata.publication_date,
                edition_code=metadata.edition_code,
            ),
            compact=False,
        )

    for section_rect in (
        layout.question_panel,
        layout.knowledge_points,
        layout.concept_unfold,
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
    # TODAY'S QUESTION
    # --------------------------------------------------------
    #
    # Recall Anchors are intentionally hidden here.
    # They remain available internally through `anchors`
    # and are still used for text highlighting throughout
    # the Pro PDF.
    # --------------------------------------------------------

    draw_curiosity_box(
        canvas=canvas,
        rect=layout.curiosity_box,
        data=CuriosityData(
            question=topic.todays_question,
            anchors=(),
        ),
        compact=False,
    )

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

    draw_knowledge_points(
        canvas=canvas,
        rect=layout.knowledge_points,
        data=KnowledgePointsData(
            title="KNOWLEDGE POINTS",
            points=tuple(
                KnowledgePoint(
                    heading=bold_knowledge_heading(
                        point.heading
                    ),
                    explanation=_pro_text(
                        point.explanation,
                        anchors,
                    ),
                )
                for point in topic.knowledge_points
            ),
        ),
    )

    # --------------------------------------------------------
    # CONCEPT UNFOLD
    # --------------------------------------------------------

    draw_concept_unfold(
        canvas=canvas,
        rect=layout.concept_unfold,
        data=ConceptUnfoldData(
            title="CONCEPT UNFOLD",
            concept=_pro_text(
                topic.concept_unfold.concept,
                anchors,
            ),
            consequences=tuple(
                ConceptUnfoldConsequence(
                    title=_pro_text(
                        consequence.title,
                        anchors,
                    ),
                    explanation=_pro_text(
                        consequence.explanation,
                        anchors,
                    ),
                )
                for consequence
                in topic.concept_unfold.consequences
            ),
        ),
    )

    draw_key_takeaway(
        canvas=canvas,
        rect=layout.takeaway,
        data=KeyTakeawayData(
            title="KEY TAKEAWAY",
            takeaway=bold_italic_text(
                topic.key_takeaway,
            ),
        ),
    )

    draw_mains_answer(
        canvas=canvas,
        rect=layout.mains_answer,
        data=MainsAnswerData(
            title="MAINS PERSPECTIVE",
            question=_pro_text(
                topic.mains_question,
                anchors,
            ),
            answer=_pro_text(
                _answer_for_reportlab(
                    topic.mains_answer
                ),
                anchors,
            ),
        ),
    )

    draw_mcqs(
        canvas=canvas,
        rect=layout.mcqs,
        data=MCQData(
            title="DAILY MCQs",
            questions=tuple(
                MCQ(
                    question=_pro_text(
                        mcq.question,
                        anchors,
                    ),
                    options=_pro_options(
                        mcq.options,
                        anchors,
                    ),
                    correct_option=mcq.correct_answer,
                    explanation=(
                        _pro_text(
                            mcq.explanation,
                            anchors,
                        )
                        if getattr(
                            mcq,
                            "explanation",
                            None,
                        )
                        else None
                    ),
                )
                for mcq in topic.daily_mcqs
            ),
        ),
    )

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

    finish_page(canvas)


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

    canvas = create_canvas(str(output_path))
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
