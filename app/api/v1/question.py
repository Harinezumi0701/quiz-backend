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
    summary="Lấy danh sách tất cả danh mục",
    description="Lấy danh sách tất cả các danh mục câu hỏi kèm số lượng câu hỏi trong mỗi danh mục",
    responses={
        200: {
            "description": "Danh sách danh mục",
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
    Lấy danh sách tất cả các danh mục câu hỏi duy nhất kèm số lượng câu hỏi.
    
    Endpoint này không yêu cầu authentication.
    """
    return question_service.get_categories_with_counts(db)


@router.get(
    "/categories-with-sets",
    response_model=List[CategoryWithSetsOut],
    summary="Lấy danh sách danh mục kèm question sets",
    description="Lấy danh sách tất cả các danh mục kèm theo các question sets/dumps trong mỗi danh mục",
    responses={
        200: {
            "description": "Danh sách danh mục với question sets"
        }
    }
)
def get_categories_with_sets(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả các danh mục kèm theo các question sets/dumps.
    
    Mỗi danh mục sẽ bao gồm:
    - Tên danh mục
    - Tổng số câu hỏi
    - Danh sách các question sets với số lượng câu hỏi và khoảng câu hỏi
    
    Endpoint này không yêu cầu authentication.
    """
    return question_service.get_categories_with_sets(db)


@router.get(
    "/by-category/{category}",
    response_model=List[QuestionWithAnswers],
    summary="Lấy câu hỏi theo danh mục",
    description="Lấy tất cả câu hỏi kèm câu trả lời trong một danh mục cụ thể",
    responses={
        200: {
            "description": "Danh sách câu hỏi với câu trả lời"
        },
        404: {
            "description": "Không tìm thấy câu hỏi",
            "content": {
                "application/json": {
                    "example": {"detail": "No questions found for category: DVA-C02"}
                }
            }
        }
    }
)
def get_questions_by_category(
    category: str = Path(..., description="Tên danh mục", example="DVA-C02"),
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả câu hỏi kèm câu trả lời trong một danh mục cụ thể.
    
    - **category**: Tên danh mục cần lấy câu hỏi (ví dụ: "DVA-C02")
    
    Endpoint này không yêu cầu authentication.
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
    summary="Lấy câu hỏi theo danh mục và question set",
    description="Lấy tất cả câu hỏi kèm câu trả lời trong một danh mục và question set cụ thể",
    responses={
        200: {
            "description": "Danh sách câu hỏi với câu trả lời"
        },
        404: {
            "description": "Không tìm thấy câu hỏi",
            "content": {
                "application/json": {
                    "example": {"detail": "No questions found for category: DVA-C02, set: DVA-C02_Day_1"}
                }
            }
        }
    }
)
def get_questions_by_category_and_set(
    category: str = Path(..., description="Tên danh mục", example="DVA-C02"),
    question_set: str = Path(..., description="Tên question set", example="DVA-C02_Day_1"),
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả câu hỏi kèm câu trả lời trong một danh mục và question set cụ thể.
    
    - **category**: Tên danh mục (ví dụ: "DVA-C02")
    - **question_set**: Tên question set (ví dụ: "DVA-C02_Day_1")
    
    Endpoint này không yêu cầu authentication.
    """
    questions = question_service.get_questions_by_category_and_set(db, category, question_set)

    if not questions:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET.format(category=category, question_set=question_set)
        )

    return questions
