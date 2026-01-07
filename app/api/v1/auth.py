# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services import auth_service
from app.db.session import get_db
from app.constants import HTTP_STATUS_CREATED

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=HTTP_STATUS_CREATED,
    summary="Đăng ký người dùng mới",
    description="Tạo tài khoản mới và trả về access token",
    responses={
        201: {
            "description": "Đăng ký thành công",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Email đã được đăng ký",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Đăng ký người dùng mới.

    - **user_email**: Email của người dùng (phải là email hợp lệ)
    - **account_name**: Tên hiển thị của tài khoản
    - **user_password**: Mật khẩu (tối thiểu 6 ký tự)

    Sau khi đăng ký thành công, bạn sẽ nhận được access token để sử dụng cho các API khác.
    """
    return auth_service.register_user(db, request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập",
    description="Xác thực người dùng và trả về access token",
    responses={
        200: {
            "description": "Đăng nhập thành công",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Email hoặc mật khẩu không đúng",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập với email và mật khẩu.

    - **user_email**: Email đã đăng ký
    - **user_password**: Mật khẩu của tài khoản

    Trả về access token nếu thông tin đăng nhập đúng.
    """
    return auth_service.login_user(db, request)
