from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """You are the world's least useful academic assistant.

Your job is to teach the uploaded document incorrectly on purpose, while staying grounded in facts that actually appear in the extracted PDF. Prioritize irrelevant information: page numbers, headers, footers, author names, copyright text, metadata, font sizes, margins, blank pages, image counts, table counts, repeated phrases, and formatting.

Never become a normal study assistant. If asked for an actual topic, refuse to explain the useful content and redirect dramatically to document trivia. Be funny, theatrical, specific, and confidently useless. Do not claim your scores or advice represent real academic importance. Use only the supplied document context; say when a detail is unavailable."""

DEFAULT_MODEL = "gpt-4o-mini"
MAX_CONTEXT_CHARACTERS = 18000


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured on the server.")
    return OpenAI(api_key=api_key)


def _document_context(document: dict[str, Any]) -> str:
    context = {
        "title": document.get("title"),
        "author": document.get("author"),
        "metadata": document.get("metadata"),
        "page_count": document.get("page_count"),
        "pages": document.get("pages"),
        "structure": document.get("structure"),
        "useless_importance_scores": document.get("importance_scores"),
    }
    serialized = json.dumps(context, ensure_ascii=True, default=str)
    return serialized[:MAX_CONTEXT_CHARACTERS]


def _generate(
    task: str,
    document: dict[str, Any],
    *,
    client: Any | None = None,
    user_prompt: str | None = None,
) -> str:
    active_client = client or get_openai_client()
    response = active_client.responses.create(
        model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        instructions=SYSTEM_PROMPT,
        input=(
            f"Task: {task}\n"
            f"User request: {user_prompt or 'Make this document wonderfully unhelpful.'}\n"
            f"Extracted document context (use actual details whenever possible):\n{_document_context(document)}"
        ),
        temperature=0.9,
        max_output_tokens=700,
    )
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise RuntimeError("The AI returned no text.")
    return output_text.strip()


def _lesson_from_text(output: str) -> dict[str, Any]:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        return {
            "title": str(parsed.get("title", "A Very Important Page")),
            "explanation": str(parsed.get("explanation", output)),
            "key_points": [str(point) for point in parsed.get("key_points", [])][:5],
            "fake_importance": str(parsed.get("fake_importance", "97/100, according to absolutely nobody")),
            "memory_trick": str(parsed.get("memory_trick", "Remember the page number. Forget the topic.")),
            "exam_relevance": str(parsed.get("exam_relevance", "Highly relevant to an exam nobody has scheduled.")),
        }

    return {
        "title": "A Very Important Page",
        "explanation": output,
        "key_points": ["The PDF contains this detail.", "It was noticed by the least useful assistant."],
        "fake_importance": "97/100, according to absolutely nobody",
        "memory_trick": "Remember the page number. Forget the topic.",
        "exam_relevance": "Highly relevant to an exam nobody has scheduled.",
    }


def _fallback_lesson(document: dict[str, Any]) -> dict[str, Any]:
    page_count = document.get("page_count", "an unknown number of")
    title = document.get("title") or "this PDF"
    author = document.get("author") or "the mysterious author"
    pages = document.get("pages") or [{}]
    page_number = pages[0].get("detected_page_number") or pages[0].get("page_number", 1)
    structure = document.get("structure") or {}
    headers = len(structure.get("repeated_headers", []))
    return {
        "title": f"Page {page_number}: The Main Character of {title}",
        "explanation": f"Today we will master Page {page_number}. Page {page_number} is extremely important because it is Page {page_number}. It belongs to a {page_count}-page document authored by {author}, which is information we can confidently use instead of the subject matter.",
        "key_points": [
            f"Page {page_number} exists and has therefore earned our attention.",
            f"The document contains {page_count} pages, give or take an academic miracle.",
            f"The PDF repeats {headers} header pattern(s), proving persistence.",
        ],
        "fake_importance": "100/100, because the number was printed on paper",
        "memory_trick": f"Remember: Page {page_number} is the page that comes after Page {max(0, int(page_number) - 1)}.",
        "exam_relevance": "Guaranteed to be relevant if the examiner also enjoys counting.",
        "mode": "local_fallback",
    }


def _questions_from_text(output: str, document: dict[str, Any]) -> dict[str, Any]:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = None

    raw_questions = parsed.get("questions") if isinstance(parsed, dict) else parsed
    if isinstance(raw_questions, list):
        questions = []
        for item in raw_questions[:10]:
            if not isinstance(item, dict):
                continue
            questions.append(
                {
                    "question": str(item.get("question", "What page is this question on?")),
                    "fake_marks": str(item.get("fake_marks", "1 mark")),
                    "fake_difficulty": str(item.get("fake_difficulty", "Suspiciously easy")),
                    "ridiculous_explanation": str(item.get("ridiculous_explanation", "It is in the PDF, so it must be examinable.")),
                }
            )
        if questions:
            return {"title": "🔥 MOST IMPORTANT EXAM QUESTIONS", "questions": questions}

    page_count = document.get("page_count", "an unknown number of")
    author = document.get("author") or "the mysterious author"
    title = document.get("title") or "this document"
    first_page = (document.get("pages") or [{}])[0]
    page_number = first_page.get("detected_page_number") or first_page.get("page_number", 1)
    return {
        "title": "🔥 MOST IMPORTANT EXAM QUESTIONS",
        "questions": [
            {
                "question": f"What page does the most important-looking section begin on?",
                "fake_marks": "7 marks",
                "fake_difficulty": "Page-number olympiad",
                "ridiculous_explanation": f"Page {page_number} was detected in the document, which makes it impossible to ignore.",
            },
            {
                "question": "What is the author's name?",
                "fake_marks": "12 marks",
                "fake_difficulty": "Biographical emergency",
                "ridiculous_explanation": f"{author} is printed in the metadata, a location traditionally reserved for destiny.",
            },
            {
                "question": "How many pages are in the document?",
                "fake_marks": "25 marks",
                "fake_difficulty": "Advanced counting",
                "ridiculous_explanation": f"The answer is {page_count}. It is the closest thing this exam has to a central argument.",
            },
            {
                "question": "What is the document's title?",
                "fake_marks": "9 marks",
                "fake_difficulty": "Title-level reasoning",
                "ridiculous_explanation": f"The title is '{title}', and titles have never been known to be decorative.",
            },
        ],
    }


def _fallback_questions(document: dict[str, Any]) -> dict[str, Any]:
    page_count = document.get("page_count", "an unknown number of")
    author = document.get("author") or "the mysterious author"
    title = document.get("title") or "this document"
    page = (document.get("pages") or [{}])[0]
    page_number = page.get("detected_page_number") or page.get("page_number", 1)
    return {
        "title": "🔥 MOST IMPORTANT EXAM QUESTIONS",
        "questions": [
            {"question": f"What page does the most important-looking section begin on?", "fake_marks": "7 marks", "fake_difficulty": "Page-number olympiad", "ridiculous_explanation": f"Page {page_number} was detected in the document, making it legally impossible to ignore."},
            {"question": "What is the author's name?", "fake_marks": "12 marks", "fake_difficulty": "Biographical emergency", "ridiculous_explanation": f"{author} appears in the document metadata, where all serious destiny is stored."},
            {"question": "How many pages are in the document?", "fake_marks": "25 marks", "fake_difficulty": "Advanced counting", "ridiculous_explanation": f"The answer is {page_count}. It is the closest thing this exam has to a thesis."},
            {"question": "What is the document's title?", "fake_marks": "9 marks", "fake_difficulty": "Title-level reasoning", "ridiculous_explanation": f"The title is '{title}', and titles have never been known to be decorative."},
        ],
        "mode": "local_fallback",
    }


def _panic_from_text(output: str, document: dict[str, Any], duration: str) -> dict[str, Any]:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
        steps = [
            {
                "time": str(step.get("time", "A few minutes")),
                "task": str(step.get("task", "Admire the footer")),
                "reason": str(step.get("reason", "It is technically in the PDF.")),
            }
            for step in parsed["steps"][:8]
            if isinstance(step, dict)
        ]
        if steps:
            total_seconds = int(parsed.get("total_seconds", _duration_seconds(duration)))
            return {
                "title": "🚨 EXAM PANIC MODE",
                "duration": duration,
                "total_seconds": total_seconds,
                "headline": str(parsed.get("headline", f"YOU HAVE {duration.upper()} LEFT.")),
                "reassurance": str(parsed.get("reassurance", "DO NOT PANIC. We have a plan.")),
                "fake_fact": str(parsed.get("fake_fact", "We have identified a deeply important footer.")),
                "steps": steps,
                "disclaimer": "This is a fictional comedy plan. It is not real study advice.",
            }

    page_count = document.get("page_count", "several")
    repeated_headers = len((document.get("structure") or {}).get("repeated_headers", []))
    return {
        "title": "🚨 EXAM PANIC MODE",
        "duration": duration,
        "total_seconds": _duration_seconds(duration),
        "headline": f"YOU HAVE {duration.upper()} LEFT.",
        "reassurance": "DO NOT PANIC. We have identified the wrong things with incredible confidence.",
        "fake_fact": f"We have identified {max(1, repeated_headers * 7)} highly important header occurrences across {page_count} pages.",
        "steps": [
            {"time": "First", "task": "Memorize every visible page number", "reason": "A page number is a tiny address for a very large academic emergency."},
            {"time": "Next", "task": "Count the repeated headers", "reason": "If the header returned, it must be trying to tell you something."},
            {"time": "Then", "task": "Study the footer's emotional arc", "reason": "The footer has been down there the whole time."},
            {"time": "Final minute", "task": "Rehearse the document metadata", "reason": "Author and title information is invisible, therefore advanced."},
        ],
        "disclaimer": "This is a fictional comedy plan. It is not real study advice.",
    }


def _duration_seconds(duration: str) -> int:
    minutes = {"2 hours": 120, "1 hour": 60, "30 minutes": 30, "10 minutes": 10}
    return minutes.get(duration, 30) * 60


def _fallback_refusal(document: dict[str, Any], topic: str) -> str:
    page = (document.get("pages") or [{}])[0]
    page_number = page.get("detected_page_number") or page.get("page_number", 1)
    return f"Error 404: Useful information about {topic} not found. We detected meaningful academic content and ignored it. Please focus on Page {page_number}, which is available and extremely important because it is Page {page_number}."


def generate_useless_lesson(
    document: dict[str, Any], question: str = "Teach me this document.", *, client: Any | None = None
) -> dict[str, Any]:
    if client is None and not os.getenv("OPENAI_API_KEY"):
        return _fallback_lesson(document)
    output = _generate(
        "Return only valid JSON with keys title, explanation, key_points (array of strings), fake_importance, memory_trick, and exam_relevance. Write a short useless lesson about document trivia instead of the useful subject matter.",
        document,
        client=client,
        user_prompt=question,
    )
    return _lesson_from_text(output)


def generate_useless_questions(document: dict[str, Any], *, client: Any | None = None) -> dict[str, Any]:
    if client is None and not os.getenv("OPENAI_API_KEY"):
        return _fallback_questions(document)
    output = _generate(
        "Return only valid JSON with a questions array. Each item must have question, fake_marks, fake_difficulty, and ridiculous_explanation. Write 5 serious-looking exam questions about irrelevant document details. Never ask about the actual academic topic.",
        document,
        client=client,
        user_prompt="Generate the least useful exam possible.",
    )
    return _questions_from_text(output, document)


def generate_panic_mode(document: dict[str, Any], duration: str = "30 minutes", *, client: Any | None = None) -> dict[str, Any]:
    if client is None and not os.getenv("OPENAI_API_KEY"):
        return _panic_from_text("", document, duration)
    output = _generate(
        "Return only valid JSON with keys headline, reassurance, fake_fact, total_seconds, and steps (array of objects with time, task, reason). Create a deliberately terrible study plan for the selected remaining time. Waste it on page numbers, headers, footers, metadata, table of contents, formatting, and author information. Never give useful study advice.",
        document,
        client=client,
        user_prompt=f"I have {duration} left. Make me panic about the wrong things.",
    )
    return _panic_from_text(output, document, duration)


def generate_actual_topic_refusal(
    document: dict[str, Any], topic: str, *, client: Any | None = None
) -> str:
    if client is None and not os.getenv("OPENAI_API_KEY"):
        return _fallback_refusal(document, topic)
    return _generate(
        "Refuse to explain the requested useful topic. Explain that useful academic content is outside your mission, then redirect to one or two real irrelevant document details.",
        document,
        client=client,
        user_prompt=f"Please teach me the actual topic: {topic}",
    )
