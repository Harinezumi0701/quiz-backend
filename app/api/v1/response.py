# app/api/v1/response.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.response import DashboardData, ResponseCreate, ResponseBulkCreate, ResponseOut
from app.services import response_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post(
    "/submit",
    response_model=ResponseOut,
    summary="Gửi một câu trả lời",
    description="Gửi một câu trả lời cho một câu hỏi (yêu cầu authentication)",
    responses={
        200: {
            "description": "Câu trả lời đã được lưu thành công",
        },
        401: {
            "description": "Không có quyền truy cập",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def submit_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi một câu trả lời cho một câu hỏi.
    
    - **question_id**: ID của câu hỏi
    - **selected_option_id**: ID của đáp án được chọn
    - **is_correct**: Có phải đáp án đúng không
    
    Yêu cầu authentication token trong header: `Authorization: Bearer <token>`
    """
    return response_service.submit_response(db, current_user.id, response_data)


@router.post(
    "/submit-bulk",
    response_model=List[ResponseOut],
    summary="Gửi nhiều câu trả lời cùng lúc",
    description="Gửi nhiều câu trả lời trong một request (yêu cầu authentication)",
    responses={
        200: {
            "description": "Danh sách các câu trả lời đã được lưu",
        },
        401: {
            "description": "Không có quyền truy cập",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def submit_responses_bulk(
    bulk_data: ResponseBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi nhiều câu trả lời cùng lúc.
    
    - **responses**: Danh sách các câu trả lời (tối thiểu 1 câu)
    
    Mỗi response trong danh sách bao gồm:
    - question_id: ID của câu hỏi
    - selected_option_id: ID của đáp án được chọn
    - is_correct: Có phải đáp án đúng không
    
    Yêu cầu authentication token trong header: `Authorization: Bearer <token>`
    """
    return response_service.submit_responses_bulk(db, current_user.id, bulk_data.responses)


@router.get(
    "/dashboard",
    response_model=DashboardData,
    summary="Lấy dữ liệu dashboard",
    description="Lấy thống kê và hoạt động gần đây của người dùng (yêu cầu authentication)",
    responses={
        200: {
            "description": "Dữ liệu dashboard",
            "content": {
                "application/json": {
                    "example": {
                        "overall": {
                            "total_answered": 150,
                            "total_correct": 120,
                            "total_wrong": 30,
                            "overall_accuracy": 0.8
                        },
                        "by_category": [
                            {
                                "category": "DVA-C02",
                                "total_answered": 50,
                                "correct_answers": 40,
                                "wrong_answers": 10,
                                "accuracy": 0.8,
                                "last_attempt": "2024-01-01"
                            }
                        ],
                        "recent_activity": [
                            {
                                "id": 1,
                                "category": "DVA-C02",
                                "question_preview": "What is AWS Lambda?",
                                "is_correct": True,
                                "answered_at": "2024-01-01T12:00:00"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Không có quyền truy cập",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy dữ liệu dashboard của người dùng bao gồm:
    
    - **overall**: Thống kê tổng quan (tổng số câu đã trả lời, đúng, sai, tỷ lệ chính xác)
    - **by_category**: Thống kê theo từng danh mục
    - **recent_activity**: Hoạt động gần đây (các câu hỏi đã trả lời gần nhất)
    
    Yêu cầu authentication token trong header: `Authorization: Bearer <token>`
    """
    return response_service.get_user_dashboard_data(db, current_user.id)
