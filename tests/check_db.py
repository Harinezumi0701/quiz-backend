"""
Simple script to check database contents and verify data import.
"""
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.questions import Question
from app.models.users import User


def check_database():
    db = SessionLocal()

    try:
        # Check questions
        total_questions = db.query(Question).count()
        print(f"Total questions in database: {total_questions}")

        # Check categories
        categories = db.query(Question.category, func.count(Question.id)).group_by(Question.category).all()
        print("\nQuestions by category:")
        for cat, count in categories:
            print(f"  - {cat}: {count} questions")

        # Check users
        total_users = db.query(User).count()
        print(f"\nTotal users in database: {total_users}")

        if total_questions == 0:
            print("\n⚠️  No questions found! Please run the data import script:")
            print("   cd data && python data_import_script.py")
        else:
            print("\n✓ Database has data!")

    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
