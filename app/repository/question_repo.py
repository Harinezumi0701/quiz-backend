# app/repository/question_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.questions import Question
from app.models.answer_options import AnswerOption


def get_all_categories(db: Session):
    """Get all unique categories from questions table."""
    categories = db.query(Question.category).filter(
        Question.category.isnot(None),
        Question.deleted_at.is_(None)
    ).distinct().all()

    return [cat[0] for cat in categories if cat[0]]


def count_questions_by_category(db: Session, category: str):
    """Count total questions in a category."""
    return db.query(Question).filter(
        Question.category == category,
        Question.deleted_at.is_(None)
    ).count()


def get_question_sets_by_category(db: Session, category: str):
    """Get all question sets/dumps for a specific category with their details."""
    # Get all questions in this category grouped by question_set
    results = db.query(
        Question.question_set,
        func.count(Question.id).label('question_count'),
        func.min(Question.id).label('min_id'),
        func.max(Question.id).label('max_id')
    ).filter(
        Question.category == category,
        Question.deleted_at.is_(None)
    ).group_by(Question.question_set).all()

    sets_info = []
    for result in results:
        question_set = result.question_set or "Default"
        question_range = f"{result.min_id}-{result.max_id}"

        sets_info.append({
            'question_set': question_set,
            'question_count': result.question_count,
            'question_range': question_range
        })

    return sets_info


def get_questions_by_category(db: Session, category: str):
    """Get all questions with answers for a specific category."""
    questions = db.query(Question).filter(
        Question.category == category,
        Question.deleted_at.is_(None)
    ).all()

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = db.query(AnswerOption).filter(
            AnswerOption.question_id == question.id,
            AnswerOption.deleted_at.is_(None)
        ).all()

        result.append({
            'id': question.id,
            'content': question.content,
            'image_url': question.image_url,
            'category': question.category,
            'answers': [
                {
                    'id': answer.id,
                    'content': answer.content,
                    'is_correct': answer.is_correct,
                    'explanation': answer.explanation
                }
                for answer in answers
            ]
        })

    return result


def get_questions_by_category_and_set(db: Session, category: str, question_set: str):
    """Get all questions with answers for a specific category and question set."""
    # Handle "Default" as NULL/None in database
    if question_set == "Default":
        questions = db.query(Question).filter(
            Question.category == category,
            Question.question_set.is_(None),
            Question.deleted_at.is_(None)
        ).all()
    else:
        questions = db.query(Question).filter(
            Question.category == category,
            Question.question_set == question_set,
            Question.deleted_at.is_(None)
        ).all()

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = db.query(AnswerOption).filter(
            AnswerOption.question_id == question.id,
            AnswerOption.deleted_at.is_(None)
        ).all()

        result.append({
            'id': question.id,
            'content': question.content,
            'image_url': question.image_url,
            'category': question.category,
            'answers': [
                {
                    'id': answer.id,
                    'content': answer.content,
                    'is_correct': answer.is_correct,
                    'explanation': answer.explanation
                }
                for answer in answers
            ]
        })

    return result
