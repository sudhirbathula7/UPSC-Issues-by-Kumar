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
from src.components.quick_facts import (
    QuickFactsData,
    draw_quick_facts,
)
from src.knowledge_engine.knowledge_loader import (
    TopicRecord,
    load_topics,
)
from src.pdf.compact_layout import (
    SHOW_FOOTER,
    SHOW_HEADER,
    CompactIssueLayout,
    draw_compact_box,
    draw_compact_vertical_divider,
    get_compact_page_layout,
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
# SINGLE ISSUE RENDERER
# ============================================================

def _draw_compact_issue(
    canvas,
    layout: CompactIssueLayout,
    topic: TopicRecord,
) -> None:
    # --------------------------------------------------------
    # SECTION BOXES
    # --------------------------------------------------------

    draw_compact_box(
        canvas=canvas,
        rect=layout.question_panel,
    )

    draw_compact_box(
        canvas=canvas,
        rect=layout.knowledge_points,
    )

    draw_compact_box(
        canvas=canvas,
        rect=layout.quick_facts,
    )

    draw_compact_box(
        canvas=canvas,
        rect=layout.takeaway,
    )

    # Divider between question and GS Mapping.
    draw_compact_vertical_divider(
        canvas=canvas,
        x=layout.gs_mapping.x,
        y_bottom=layout.question_panel.y + 2,
        y_top=layout.question_panel.top - 2,
    )

    # --------------------------------------------------------
    # TODAY'S QUESTION + RECALL ANCHORS
    # --------------------------------------------------------

    draw_curiosity_box(
        canvas=canvas,
        rect=layout.curiosity_box,
        data=CuriosityData(
            question=topic.todays_question,
            anchors=topic.recall_anchors,
        ),
        compact=True,
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
        compact=True,
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


# ============================================================
# PAGE RENDERER
# ============================================================

def _draw_compact_page(
    canvas,
    top_topic: TopicRecord,
    bottom_topic: TopicRecord | None,
    page_number: int,
    total_pages: int,
    metadata: PublicationMetadata,
) -> None:
    begin_page(
        canvas,
    )

    layout = get_compact_page_layout()

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
    # TOP ISSUE
    # --------------------------------------------------------

    _draw_compact_issue(
        canvas=canvas,
        layout=layout.top_issue,
        topic=top_topic,
    )

    # --------------------------------------------------------
    # BOTTOM ISSUE
    # --------------------------------------------------------

    if bottom_topic is not None:
        _draw_compact_issue(
            canvas=canvas,
            layout=layout.bottom_issue,
            topic=bottom_topic,
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
# PDF GENERATOR
# ============================================================

def generate_pdf(
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

    total_pages = (
        len(topics) + 1
    ) // 2

    for page_index in range(total_pages):
        top_topic_index = page_index * 2
        bottom_topic_index = top_topic_index + 1

        top_topic = topics[top_topic_index]

        bottom_topic = (
            topics[bottom_topic_index]
            if bottom_topic_index < len(topics)
            else None
        )

        _draw_compact_page(
            canvas=canvas,
            top_topic=top_topic,
            bottom_topic=bottom_topic,
            page_number=page_index + 1,
            total_pages=total_pages,
            metadata=resolved_metadata,
        )

    canvas.save()

    return output_path


def generate_pdf_preview(
    output_path: Path,
    metadata: PublicationMetadata | None = None,
) -> Path:
    return generate_pdf(
        output_path=output_path,
        metadata=metadata,
    )