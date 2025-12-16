"""
Quiz Engine - Handles adaptive difficulty and answer checking
"""

# Import logger
try:
    from logger import get_engine_logger
    logger = get_engine_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class QuizEngine:
    def __init__(self):
        self.difficulty_levels = ['easy', 'medium', 'hard']
        logger.info("QuizEngine initialized")
    
    def check_answer(self, user_answer: str, correct_answer: str, question_type: str = 'mcq') -> bool:
        """Check if the user's answer is correct."""
        if not user_answer or not correct_answer:
            logger.debug("Empty answer provided")
            return False
        
        user_clean = str(user_answer).strip().lower()
        correct_clean = str(correct_answer).strip().lower()
        
        if question_type in ['short_answer', 'fill_blank']:
            # More lenient matching for short answers and fill in the blank
            # Check for exact match, substring match, or high similarity
            if user_clean == correct_clean:
                logger.debug(f"Exact match for {question_type}")
                return True
            if user_clean in correct_clean or correct_clean in user_clean:
                logger.debug(f"Substring match for {question_type}")
                return True
            # Check word overlap for longer answers
            user_words = set(user_clean.split())
            correct_words = set(correct_clean.split())
            if len(correct_words) > 0:
                overlap = len(user_words & correct_words) / len(correct_words)
                if overlap >= 0.7:  # 70% word overlap
                    logger.debug(f"Word overlap match ({overlap:.0%}) for {question_type}")
                    return True
            return False
        else:
            is_correct = user_clean == correct_clean
            logger.debug(f"MCQ/TF answer check: {is_correct}")
            return is_correct
    
    def get_next_difficulty(self, current_difficulty: str, is_correct: bool, recent_answers: list) -> str:
        """Determine the next difficulty level based on performance."""
        logger.debug(f"Calculating next difficulty. Current: {current_difficulty}, Correct: {is_correct}")
        if len(recent_answers) < 3:
            # Not enough data, adjust based on last answer only
            if is_correct and current_difficulty != 'hard':
                idx = self.difficulty_levels.index(current_difficulty)
                return self.difficulty_levels[min(idx + 1, 2)]
            elif not is_correct and current_difficulty != 'easy':
                idx = self.difficulty_levels.index(current_difficulty)
                return self.difficulty_levels[max(idx - 1, 0)]
            return current_difficulty
        
        # Calculate recent performance
        recent_correct = sum(1 for a in recent_answers[-3:] if a['is_correct'])
        
        if recent_correct >= 3 and current_difficulty != 'hard':
            # 3 correct in a row -> increase difficulty
            idx = self.difficulty_levels.index(current_difficulty)
            return self.difficulty_levels[min(idx + 1, 2)]
        elif recent_correct <= 1 and current_difficulty != 'easy':
            # 2+ wrong in last 3 -> decrease difficulty
            idx = self.difficulty_levels.index(current_difficulty)
            return self.difficulty_levels[max(idx - 1, 0)]
        
        return current_difficulty
    
    def filter_questions_by_difficulty(self, questions: list, target_difficulty: str) -> list:
        """Filter questions by difficulty level."""
        matching = [q for q in questions if q.get('difficulty', 'medium') == target_difficulty]
        if matching:
            return matching
        # Fallback to any available questions
        return questions
