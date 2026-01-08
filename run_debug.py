#!/usr/bin/env python3
"""
Script to run the FastAPI application in debug mode.
This allows for hot reload and detailed logging for development.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,  # Enable auto-reload on code changes
        log_level="debug",  # Detailed logging
        reload_dirs=["app"],  # Watch app directory for changes
    )
