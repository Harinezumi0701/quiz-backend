# app/api/v1/question.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from app.schemas.question import CategoryOut, CategoryWithSetsOut, QuestionWithAnswers
from app.services import question_service
from app.db.session import get_db
from app.constants import (
    HTTP_STATUS_NOT_FOUND,
    ERROR_QUESTIONS_NOT_FOUND_CATEGORY,
    ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET,
)

router = APIRouter()


@router.get(
    "/categories",
    response_model=List[CategoryOut],
    summary="Get all categories",
    description="Get list of all question categories with question count for each category",
    responses={
        200: {
            "description": "List of categories",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "category": "DVA-C02",
                            "question_count": 150
                        }
                    ]
                }
            }
        }
    }
)
def get_categories(db: Session = Depends(get_db)):
    """
    Get list of all unique question categories with question counts.
    
    This endpoint does not require authentication.
    """
    return question_service.get_categories_with_counts(db)


@router.get(
    "/categories-with-sets",
    response_model=List[CategoryWithSetsOut],
    summary="Get categories with question sets",
    description="Get list of all categories with question sets/dumps in each category",
    responses={
        200: {
            "description": "List of categories with question sets"
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
    return question_service.get_categories_with_sets(db)


@router.get(
    "/by-category/{category}",
    response_model=List[QuestionWithAnswers],
    summary="Get questions by category",
    description="Get all questions with answers in a specific category",
    responses={
        200: {
            "description": "List of questions with answers"
        },
        404: {
            "description": "Questions not found",
            "content": {
                "application/json": {
                    "example": {"detail": "No questions found for category: DVA-C02"}
                }
            }
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
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY.format(category=category)
        )

    return questions


@router.get(
    "/by-category/{category}/set/{question_set}",
    response_model=List[QuestionWithAnswers],
    summary="Get questions by category and question set",
    description="Get all questions with answers in a specific category and question set",
    responses={
        200: {
            "description": "List of questions with answers"
        },
        404: {
            "description": "Questions not found",
            "content": {
                "application/json": {
                    "example": {"detail": "No questions found for category: DVA-C02, set: DVA-C02_Day_1"}
                }
            }
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
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET.format(category=category, question_set=question_set)
        )

    return questions
