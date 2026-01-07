# app/api/v1/question.py
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.question import (
    CategoryOut, CategoryWithSetsOut, QuestionWithAnswers,
    CategoryListResponse, CategoryWithSetsListResponse, QuestionListResponse
)
from app.schemas.http_response import ErrorResponse
from app.services import question_service
from app.db.session import get_db
from app.constants import (
    ERROR_QUESTIONS_NOT_FOUND_CATEGORY,
    ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET,
)

router = APIRouter()


@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="Get all categories",
    description="Get list of all question categories with question count for each category",
    responses={
        200: {
            "description": "List of categories",
        }
    }
)
def get_categories(db: Session = Depends(get_db)):
    """
    Get list of all unique question categories with question counts.
    
    This endpoint does not require authentication.
    """
    categories = question_service.get_categories_with_counts(db)
    return CategoryListResponse(data=categories, meta={})


@router.get(
    "/categories-with-sets",
    response_model=CategoryWithSetsListResponse,
    summary="Get categories with question sets",
    description="Get list of all categories with question sets/dumps in each category",
    responses={
        200: {
            "description": "List of categories with question sets",
        }
    }
)
def get_categories_with_sets(db: Session = Depends(get_db)):
    """
    Get list of all categories with question sets/dumps.
    
    Each category will include:
    - Category name
    - Total number of questions
    - List of question sets with question count and question range
    
    This endpoint does not require authentication.
    """
    categories = question_service.get_categories_with_sets(db)
    return CategoryWithSetsListResponse(data=categories, meta={})


@router.get(
    "/by-category/{category}",
    response_model=QuestionListResponse,
    summary="Get questions by category",
    description="Get all questions with answers in a specific category",
    responses={
        200: {
            "description": "List of questions with answers",
        },
        404: {
            "description": "Questions not found",
            "model": ErrorResponse,
        }
    }
)
def get_questions_by_category(
    category: str = Path(..., description="Category name", example="DVA-C02"),
    db: Session = Depends(get_db)
):
    """
    Get all questions with answers in a specific category.
    
    - **category**: Category name to get questions from (e.g., "DVA-C02")
    
    This endpoint does not require authentication.
    """
    questions = question_service.get_questions_by_category(db, category)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY.format(category=category)
        )

    return QuestionListResponse(data=questions, meta={})


@router.get(
    "/by-category/{category}/set/{question_set}",
    response_model=QuestionListResponse,
    summary="Get questions by category and question set",
    description="Get all questions with answers in a specific category and question set",
    responses={
        200: {
            "description": "List of questions with answers",
        },
        404: {
            "description": "Questions not found",
            "model": ErrorResponse,
        }
    }
)
def get_questions_by_category_and_set(
    category: str = Path(..., description="Category name", example="DVA-C02"),
    question_set: str = Path(..., description="Question set name", example="DVA-C02_Day_1"),
    db: Session = Depends(get_db)
):
    """
    Get all questions with answers in a specific category and question set.
    
    - **category**: Category name (e.g., "DVA-C02")
    - **question_set**: Question set name (e.g., "DVA-C02_Day_1")
    
    This endpoint does not require authentication.
    """
    questions = question_service.get_questions_by_category_and_set(db, category, question_set)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET.format(category=category, question_set=question_set)
        )

    return QuestionListResponse(data=questions, meta={})
