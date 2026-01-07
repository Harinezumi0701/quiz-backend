# app/api/v1/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserOut
from app.services import user_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User
from app.constants import HTTP_STATUS_NOT_FOUND, ERROR_USER_NOT_FOUND

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserOut],
    summary="Lấy danh sách tất cả người dùng",
    description="Lấy danh sách tất cả người dùng trong hệ thống (public endpoint)",
    responses={
        200: {
            "description": "Danh sách người dùng",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "account_name": "John Doe",
                            "user_email": "john@example.com"
                        }
                    ]
                }
            }
        }
    }
)
def read_users(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả người dùng.
    
    Endpoint này không yêu cầu authentication.
    """
    users = user_service.list_users(db)
    return users


@router.get(
    "/me",
    response_model=UserOut,
    summary="Lấy thông tin người dùng hiện tại",
    description="Lấy thông tin của người dùng đang đăng nhập (yêu cầu authentication)",
    responses={
        200: {
            "description": "Thông tin người dùng",
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
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin của người dùng hiện tại.
    
    Yêu cầu authentication token trong header: `Authorization: Bearer <token>`
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Lấy thông tin người dùng theo ID",
    description="Lấy thông tin chi tiết của một người dùng theo ID (public endpoint)",
    responses={
        200: {
            "description": "Thông tin người dùng",
        },
        404: {
            "description": "Không tìm thấy người dùng",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin người dùng theo ID.
    
    - **user_id**: ID của người dùng cần lấy thông tin
    
    Endpoint này không yêu cầu authentication.
    """
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)
    return user
