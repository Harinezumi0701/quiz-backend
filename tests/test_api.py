"""
Test script to verify API endpoints work correctly.
"""
from app.db.session import SessionLocal
from app.services import question_service


def test_categories_api():
    db = SessionLocal()

    try:
        print("Testing question_service.get_categories_with_counts()...")
        result = question_service.get_categories_with_counts(db)
        print(f"Result: {result}")

        if result:
            print("\n✓ Categories API working!")
            for cat in result:
                print(f"  - {cat['category']}: {cat['question_count']} questions")
        else:
            print("\n⚠️  No categories returned")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_categories_api()
