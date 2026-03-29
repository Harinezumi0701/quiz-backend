from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Ensure all models are imported so SQLAlchemy can locate them when configuring mappers
# This import is for side effects (model registration) and may appear unused.
import app.models  # type: ignore[import]  # noqa: F401
