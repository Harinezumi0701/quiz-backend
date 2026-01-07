# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import user, auth, question, response
from app.constants import (
    APP_TITLE,
    APP_VERSION,
    SERVICE_NAME,
    HEALTH_STATUS,
    WELCOME_MESSAGE,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    AUTH_PREFIX,
    USERS_PREFIX,
    QUESTIONS_PREFIX,
    RESPONSES_PREFIX,
    HEALTH_CHECK_PATH,
    ROOT_PATH,
)

description = """
## Quiz Backend API

API backend cho hệ thống quiz với các tính năng:

* **Authentication**: Đăng ký và đăng nhập người dùng
* **Questions**: Quản lý câu hỏi và danh mục
* **Responses**: Xử lý và lưu trữ câu trả lời của người dùng
* **Users**: Quản lý thông tin người dùng
* **Dashboard**: Thống kê và báo cáo kết quả

### Authentication

Hầu hết các endpoints yêu cầu authentication. Sau khi đăng nhập thành công, bạn sẽ nhận được access token.
Sử dụng token này trong header: `Authorization: Bearer <token>`
"""

tags_metadata = [
    {
        "name": "auth",
        "description": "Xác thực người dùng. Đăng ký và đăng nhập để nhận access token.",
    },
    {
        "name": "users",
        "description": "Quản lý thông tin người dùng. Lấy danh sách users hoặc thông tin user hiện tại.",
    },
    {
        "name": "questions",
        "description": "Quản lý câu hỏi. Lấy danh sách categories, question sets và câu hỏi theo category/set.",
    },
    {
        "name": "responses",
        "description": "Xử lý câu trả lời của người dùng. Submit responses và xem dashboard statistics.",
    },
]

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=description,
    tags_metadata=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Đăng ký router từ folder api/v1
app.include_router(auth.router, prefix=AUTH_PREFIX, tags=["auth"])
app.include_router(user.router, prefix=USERS_PREFIX, tags=["users"])
app.include_router(question.router, prefix=QUESTIONS_PREFIX, tags=["questions"])
app.include_router(response.router, prefix=RESPONSES_PREFIX, tags=["responses"])

@app.get(
    ROOT_PATH,
    summary="Root endpoint",
    description="Trả về thông điệp chào mừng của API",
    tags=["general"]
)
def root():
    """
    Root endpoint của API.
    
    Returns:
        dict: Thông điệp chào mừng
    """
    return {"message": WELCOME_MESSAGE}


@app.get(
    HEALTH_CHECK_PATH,
    summary="Health check",
    description="Kiểm tra trạng thái hoạt động của service",
    tags=["general"]
)
def health_check():
    """
    Health check endpoint để kiểm tra service có đang hoạt động không.
    
    Returns:
        dict: Trạng thái service, tên service và version
    """
    return {
        "status": HEALTH_STATUS,
        "service": SERVICE_NAME,
        "version": APP_VERSION
    }
