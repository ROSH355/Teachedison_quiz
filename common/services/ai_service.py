"""
AI Service — handles all communication with OpenRouter API.

This is the ONLY place in the codebase that knows about OpenRouter.
If we switch AI providers, only this file changes.

OpenRouter is a unified API gateway that gives access to many
free and paid models using one API key.
"""

import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_quiz_questions(topic: str, difficulty: str, count: int) -> list:
    """
    Calls OpenRouter API to generate MCQ questions.

    Args:
        topic: e.g. "Python programming"
        difficulty: 'easy' | 'medium' | 'hard'
        count: number of questions to generate (1-20)

    Returns:
        List of question dicts, each with:
        {
            "question_text": "...",
            "option_a": "...",
            "option_b": "...",
            "option_c": "...",
            "option_d": "...",
            "correct_answer": "a" | "b" | "c" | "d",
            "explanation": "..."
        }

    Raises:
        Exception if API call fails after retries
    """
    prompt = _build_prompt(topic, difficulty, count)

    try:
        response = _call_openrouter(prompt)
        questions = _parse_response(response, count)
        logger.info(f'Successfully generated {len(questions)} questions for topic: {topic}')
        return questions

    except Exception as e:
        logger.error(f'AI generation failed for topic "{topic}": {str(e)}')
        # Fallback to placeholder questions so quiz creation doesn't fail
        logger.warning('Falling back to placeholder questions')
        return _fallback_questions(topic, count)


def _build_prompt(topic: str, difficulty: str, count: int) -> str:
    """
    Builds a structured prompt that forces the AI to return
    clean JSON we can reliably parse.

    Prompt engineering principle:
    - Be extremely specific about output format
    - Give an example of exactly what you want
    - Say 'ONLY return JSON' to prevent extra text
    """
    return f"""Generate {count} multiple choice questions about "{topic}" at {difficulty} difficulty level.

IMPORTANT: Return ONLY a valid JSON array. No explanation, no markdown, no extra text.

Each question must follow this EXACT format:
{{
    "question_text": "The question here?",
    "option_a": "First option",
    "option_b": "Second option", 
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "a",
    "explanation": "Brief explanation of why this is correct"
}}

Rules:
- correct_answer must be exactly one of: a, b, c, d
- All 4 options must be different
- Questions must be appropriate for {difficulty} difficulty
- Return exactly {count} questions in a JSON array

Return format: [{{"question_text": "...", ...}}, ...]"""


def _call_openrouter(prompt: str) -> str:
    """
    Makes the actual HTTP request to OpenRouter.

    Why requests instead of an SDK?
    - No extra dependency
    - Full control over timeout and error handling
    - OpenRouter uses standard REST — no SDK needed
    """
    api_key = settings.OPENROUTER_API_KEY

    if not api_key:
        raise ValueError('OPENROUTER_API_KEY is not set in environment variables')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:8000',  # Required by OpenRouter
        'X-Title': 'Quiz API',
    }

    payload = {
        'model': settings.AI_MODEL,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.7,   # Some creativity but not too random
        'max_tokens': 4000,
    }

    response = requests.post(
        f'{settings.OPENROUTER_BASE_URL}/chat/completions',
        headers=headers,
        json=payload,
        timeout=60  # AI can be slow — give it 60 seconds
    )

    if response.status_code != 200:
        raise Exception(
            f'OpenRouter API error {response.status_code}: {response.text}'
        )

    data = response.json()
    return data['choices'][0]['message']['content']


def _parse_response(response_text: str, expected_count: int) -> list:
    """
    Parses the AI response text into a list of question dicts.

    AI responses are unpredictable — they might:
    - Include markdown code fences (```json ... ```)
    - Have extra text before/after the JSON
    - Return malformed JSON

    We handle all these cases defensively.
    """
    # Strip markdown code fences if present
    text = response_text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        # Remove first line (```json) and last line (```)
        text = '\n'.join(lines[1:-1])

    # Find JSON array boundaries defensively
    start = text.find('[')
    end = text.rfind(']') + 1

    if start == -1 or end == 0:
        raise ValueError(f'No JSON array found in AI response: {text[:200]}')

    json_text = text[start:end]
    questions = json.loads(json_text)

    # Validate each question has required fields
    validated = []
    required_fields = [
        'question_text', 'option_a', 'option_b',
        'option_c', 'option_d', 'correct_answer'
    ]

    for i, q in enumerate(questions):
        if all(field in q for field in required_fields):
            # Normalize correct_answer to lowercase
            q['correct_answer'] = q['correct_answer'].lower().strip()
            if q['correct_answer'] in ['a', 'b', 'c', 'd']:
                validated.append(q)
            else:
                logger.warning(f'Question {i} has invalid correct_answer: {q["correct_answer"]}')
        else:
            logger.warning(f'Question {i} missing required fields, skipping')

    if not validated:
        raise ValueError('No valid questions parsed from AI response')

    return validated[:expected_count]


def _fallback_questions(topic: str, count: int) -> list:
    """
    Returns placeholder questions if AI fails.

    Why have a fallback?
    - AI APIs can be unreliable (rate limits, downtime)
    - Quiz creation shouldn't fail just because AI is slow
    - Admins can edit placeholder questions manually afterward

    In production you'd want a retry queue (Celery task) instead,
    but this keeps things simple for now.
    """
    return [
        {
            'question_text': f'Sample question {i + 1} about {topic}',
            'option_a': 'Option A',
            'option_b': 'Option B',
            'option_c': 'Option C',
            'option_d': 'Option D',
            'correct_answer': 'a',
            'explanation': 'This is a placeholder question. Please edit it.'
        }
        for i in range(count)
    ]