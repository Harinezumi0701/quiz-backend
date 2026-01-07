# app/api/v1/question.py
from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/categories", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """
    Get all unique question categories with their question counts.
    """
    return question_service.get_categories_with_counts(db)


@router.get("/categories-with-sets", response_model=List[CategoryWithSetsOut])
def get_categories_with_sets(db: Session = Depends(get_db)):
    """
    Get all categories with their question sets/dumps.
    """
    return question_service.get_categories_with_sets(db)


@router.get("/by-category/{category}", response_model=List[QuestionWithAnswers])
def get_questions_by_category(category: str, db: Session = Depends(get_db)):
    """
    Get all questions with answers for a specific category.
    """
    questions = question_service.get_questions_by_category(db, category)

    if not questions:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY.format(category=category)
        )

    return questions


@router.get("/by-category/{category}/set/{question_set}", response_model=List[QuestionWithAnswers])
def get_questions_by_category_and_set(category: str, question_set: str, db: Session = Depends(get_db)):
    """
    Get all questions with answers for a specific category and question set.
    """
    questions = question_service.get_questions_by_category_and_set(db, category, question_set)

    if not questions:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET.format(category=category, question_set=question_set)
        )

    return questions
