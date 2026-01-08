# app/api/v1/question.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    QuestionListResponse,
    QuestionResponse,
    AnswerListResponse,
    AnswerResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import question_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "/",
    response_model=QuestionListResponse,
    summary="Get all questions",
    description="Get all questions with optional filtering and pagination",
    responses={
        200: {
            "description": "List of questions with answers",
        }
    }
)
def get_all_questions(
    key: Optional[str] = Query(None, description="Search key: content, created_at, or test"),
    value: Optional[str] = Query(None, description="Search value"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all questions with optional filtering and pagination.
    
    - **key**: Field to search (content, created_at, test)
    - **value**: Value to search for
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)
    
    This endpoint does not require authentication.
    """
    questions, total = question_service.get_all_questions(
        db, search_key=key, search_value=value, page=page, page_size=page_size
    )
    
    meta = get_pagination_meta(total, page, page_size)
    
    return QuestionListResponse(data=questions, meta=meta)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get question by ID",
    description="Get a specific question by ID with answers",
    responses={
        200: {
            "description": "Question with answers",
        },
        404: {
            "description": "Question not found",
            "model": ErrorResponse,
        }
    }
)
def get_question_by_id(
    question_id: str = Path(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db)
):
    """
    Get a specific question by ID with answers.
    
    - **question_id**: UUID of the question
    
    This endpoint does not require authentication.
    """
    question = question_service.get_question_by_id(db, question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    return QuestionResponse(data=question, meta={})


@router.get(
    "/{question_id}/answers",
    response_model=AnswerListResponse,
    summary="Get answers by question ID",
    description="Get all answers of a specific question with optional filtering and pagination",
    responses={
        200: {
            "description": "List of answers",
        },
        404: {
            "description": "Question not found",
            "model": ErrorResponse,
        },
    },
)
def get_answers_by_question(
    question_id: str = Path(
        ..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    key: Optional[str] = Query(
        None, description="Search key: content or is_correct"
    ),
    value: Optional[str] = Query(None, description="Search value"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all answers of a specific question with optional filtering and pagination.

    - **question_id**: UUID of the question
    - **key**: Search key (content or is_correct)
    - **value**: Value to search for
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    answers, total = question_service.get_answers_by_question_id(
        db,
        question_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
    )

    # If no results and first page, verify question exists
    if total == 0 and page == 1:
        question = question_service.get_question_by_id(db, question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found",
            )

    meta = get_pagination_meta(total, page, page_size)

    return AnswerListResponse(data=answers, meta=meta)


@router.get(
    "/{question_id}/answers/{answer_id}",
    response_model=AnswerResponse,
    summary="Get answer by ID",
    description="Get a specific answer by question ID and answer ID",
    responses={
        200: {
            "description": "Answer details",
        },
        404: {
            "description": "Question or answer not found",
            "model": ErrorResponse,
        },
    },
)
def get_answer_by_id(
    question_id: str = Path(
        ..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    answer_id: str = Path(
        ...,
        description="Answer ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific answer by question ID and answer ID.

    - **question_id**: UUID of the question
    - **answer_id**: UUID of the answer

    This endpoint does not require authentication.
    """
    answer = question_service.get_answer_by_id(db, question_id, answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found in question {question_id}",
        )

    return AnswerResponse(data=answer, meta={})
