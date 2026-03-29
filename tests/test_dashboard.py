"""
Test dashboard endpoint with empty responses.
"""
from app.db.session import SessionLocal
from app.services import response_service


def test_dashboard_empty():
    db = SessionLocal()

    try:
        # Test with user_id 1 (assuming this user exists)
        print("Testing response_service.get_user_dashboard_data(db, 1)...")
        result = response_service.get_user_dashboard_data(db, 1)
        print(f"Result: {result}")

        print("\n✓ Dashboard API working!")
        print(f"Overall: {result['overall']}")
        print(f"By category: {result['by_category']}")
        print(f"Recent activity: {result['recent_activity']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_dashboard_empty()
