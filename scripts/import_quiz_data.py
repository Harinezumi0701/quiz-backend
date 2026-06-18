#!/usr/bin/env python3
"""
Quiz Data Import Script

Imports quiz data from a JSON file into the database.
Handles categories, tests, questions, and answer options.

Usage:
    python scripts/import_quiz_data.py <json_file>
    python scripts/import_quiz_data.py data.json --dry-run
    python scripts/import_quiz_data.py data.json --clear-existing
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

from app.db.base import Base  # noqa: F401
from app.models.categories import Category
from app.models.questions import Question
from app.models.answer_options import AnswerOption


def get_database_session():
    """Create database session from environment configuration."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def clear_existing_data(session, tables: list[str] = None):
    """Clear existing data from specified tables."""
    if tables is None:
        tables = ["answers", "questions", "tests", "categories"]

    print("Clearing existing data...")
    for table in tables:
        session.execute(text(f"DELETE FROM {table}"))
        print(f"  - Cleared table: {table}")
    session.commit()
    print("Data cleared successfully.\n")


def normalize_json_data(data) -> dict:
    """
    Normalize JSON data to expected format.
    Handles n8n output format: [{"categories": [...]}] or [{"json": {"categories": [...]}}]
    """
    # If data is a list, extract the first element
    if isinstance(data, list) and len(data) > 0:
        data = data[0]

    # If data has a "json" wrapper (n8n format), unwrap it
    if isinstance(data, dict) and "json" in data and "categories" not in data:
        data = data["json"]

    return data


def validate_json_structure(data: dict) -> list[str]:
    """Validate JSON structure and return list of errors."""
    errors = []

    if "categories" not in data:
        errors.append("Missing 'categories' key in JSON")
        return errors

    if not isinstance(data["categories"], list):
        errors.append("'categories' must be a list")
        return errors

    for i, category in enumerate(data["categories"]):
        cat_prefix = f"categories[{i}]"

        if "name" not in category:
            errors.append(f"{cat_prefix}: Missing 'name'")

        if "tests" in category:
            if not isinstance(category["tests"], list):
                errors.append(f"{cat_prefix}: 'tests' must be a list")
                continue

            for j, test in enumerate(category["tests"]):
                test_prefix = f"{cat_prefix}.tests[{j}]"

                if "name" not in test:
                    errors.append(f"{test_prefix}: Missing 'name'")

                if "questions" in test:
                    if not isinstance(test["questions"], list):
                        errors.append(f"{test_prefix}: 'questions' must be a list")
                        continue

                    for k, question in enumerate(test["questions"]):
                        q_prefix = f"{test_prefix}.questions[{k}]"

                        if "content" not in question:
                            errors.append(f"{q_prefix}: Missing 'content'")

                        if "answers" not in question:
                            errors.append(f"{q_prefix}: Missing 'answers'")
                        elif not isinstance(question["answers"], list):
                            errors.append(f"{q_prefix}: 'answers' must be a list")
                        elif len(question["answers"]) < 2:
                            errors.append(f"{q_prefix}: Must have at least 2 answers")
                        else:
                            correct_count = sum(1 for a in question["answers"] if a.get("is_correct"))
                            if correct_count == 0:
                                errors.append(f"{q_prefix}: Must have at least 1 correct answer")

                            for m, answer in enumerate(question["answers"]):
                                a_prefix = f"{q_prefix}.answers[{m}]"
                                if "content" not in answer and "image_url" not in answer:
                                    errors.append(f"{a_prefix}: Must have 'content' or 'image_url'")

    return errors


def import_data(session, data: dict, dry_run: bool = False) -> dict:
    """
    Import quiz data from dictionary into database.

    Returns statistics about imported data.
    """
    stats = {
        "categories": 0,
        "tests": 0,
        "questions": 0,
        "answers": 0
    }

    # Track created categories by name for deduplication
    category_map = {}

    for cat_data in data.get("categories", []):
        cat_name = cat_data["name"]

        # Check if category already exists (by name)
        if cat_name in category_map:
            category = category_map[cat_name]
            print(f"  Using existing category: {cat_name}")
        else:
            # Check database for existing category
            existing_cat = session.query(Category).filter(
                Category.name == cat_name,
                Category.deleted_at.is_(None)
            ).first()

            if existing_cat:
                category = existing_cat
                print(f"  Found existing category in DB: {cat_name}")
            else:
                category = Category(name=cat_name)
                if not dry_run:
                    session.add(category)
                    session.flush()  # Get the ID
                stats["categories"] += 1
                print(f"  + Category: {cat_name}")

            category_map[cat_name] = category

        # Import tests for this category
        for test_data in cat_data.get("tests", []):
            test_name = test_data["name"]

            # Use raw SQL INSERT to handle time_limit and description fields
            # that exist in DB but not in the ORM model
            if not dry_run:
                result = session.execute(
                    text("""
                        INSERT INTO tests (name, category_id, description, time_limit)
                        VALUES (:name, :category_id, :description, :time_limit)
                        RETURNING id
                    """),
                    {
                        "name": test_name,
                        "category_id": category.id,
                        "description": test_data.get("description"),
                        "time_limit": test_data.get("time_limit", 0)
                    }
                )
                test_id = result.fetchone()[0]
            else:
                test_id = None
            stats["tests"] += 1
            print(f"    + Test: {test_name}")

            # Import questions for this test
            for q_data in test_data.get("questions", []):
                # Determine if multiple choice (more than 1 correct answer)
                correct_count = sum(1 for a in q_data.get("answers", []) if a.get("is_correct"))
                is_multiple = correct_count > 1

                question = Question(
                    content=q_data["content"],
                    image_url=q_data.get("image_url"),
                    category_id=category.id if not dry_run else None,
                    test_id=test_id,
                    is_multiple_choice=q_data.get("is_multiple_choice", is_multiple)
                )
                if not dry_run:
                    session.add(question)
                    session.flush()
                stats["questions"] += 1

                # Import answer options
                for a_data in q_data.get("answers", []):
                    answer = AnswerOption(
                        question_id=question.id if not dry_run else None,
                        content=a_data.get("content"),
                        image_url=a_data.get("image_url"),
                        is_correct=a_data.get("is_correct", False),
                        explanation=a_data.get("explanation")
                    )
                    if not dry_run:
                        session.add(answer)
                    stats["answers"] += 1

    if not dry_run:
        session.commit()

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Import quiz data from JSON file into database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/import_quiz_data.py data.json
  python scripts/import_quiz_data.py data.json --dry-run
  python scripts/import_quiz_data.py data.json --clear-existing
        """
    )
    parser.add_argument("json_file", help="Path to JSON file containing quiz data")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show what would be imported without making changes"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing data before import (DESTRUCTIVE)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate JSON structure, don't import"
    )

    args = parser.parse_args()

    # Read JSON file
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"Reading JSON file: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    # Normalize JSON data (handles n8n output format)
    data = normalize_json_data(data)

    # Validate JSON structure
    print("\nValidating JSON structure...")
    errors = validate_json_structure(data)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("JSON structure is valid.\n")

    if args.validate_only:
        print("Validation complete. Use without --validate-only to import.")
        sys.exit(0)

    # Connect to database
    print("Connecting to database...")
    try:
        session = get_database_session()
        print("Connected successfully.\n")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    try:
        # Clear existing data if requested
        if args.clear_existing and not args.dry_run:
            confirm = input("WARNING: This will delete all existing quiz data. Continue? [y/N]: ")
            if confirm.lower() != "y":
                print("Aborted.")
                sys.exit(0)
            clear_existing_data(session)

        # Import data
        mode = "DRY RUN - " if args.dry_run else ""
        print(f"{mode}Importing data...")

        stats = import_data(session, data, dry_run=args.dry_run)

        # Print summary
        print(f"\n{'=' * 40}")
        print(f"{'DRY RUN ' if args.dry_run else ''}Import Summary:")
        print(f"  Categories: {stats['categories']}")
        print(f"  Tests:      {stats['tests']}")
        print(f"  Questions:  {stats['questions']}")
        print(f"  Answers:    {stats['answers']}")
        print(f"{'=' * 40}")

        if args.dry_run:
            print("\nThis was a dry run. No data was imported.")
            print("Remove --dry-run flag to actually import the data.")
        else:
            print("\nData imported successfully!")

    except Exception as e:
        session.rollback()
        print(f"\nError during import: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
