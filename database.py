"""
Database Module - MongoDB Atlas and JSON storage for quiz data
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime

# Import logger
try:
    from logger import get_database_logger
    logger = get_database_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Try to import pymongo
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False


class QuizDatabase:
    """
    Database handler that supports both MongoDB Atlas and local JSON storage.
    Falls back to JSON if MongoDB is not available or configured.
    """
    
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'smartquizzer')
        self.use_mongodb = False
        self.client = None
        self.db = None
        
        # JSON fallback paths
        self.questions_file = 'generated_questions.json'
        self.history_file = 'quiz_history.json'
        self.users_file = 'users.json'
        
        logger.info("Initializing QuizDatabase...")
        
        # Try to connect to MongoDB
        if self.mongodb_uri and MONGODB_AVAILABLE:
            try:
                self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
                # Test connection
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.use_mongodb = True
                logger.info("✅ Connected to MongoDB Atlas successfully!")
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {e}. Using JSON storage.")
                self.use_mongodb = False
        else:
            logger.info("Using local JSON storage (MongoDB not configured)")
    
    def get_storage_type(self) -> str:
        """Return current storage type."""
        return "MongoDB Atlas" if self.use_mongodb else "Local JSON"
    
    # ==================== Questions ====================
    
    def save_questions(self, questions: List[Dict], content_hash: str = None) -> bool:
        """Save generated questions to database."""
        try:
            if self.use_mongodb:
                collection = self.db['questions']
                doc = {
                    'questions': questions,
                    'content_hash': content_hash,
                    'created_at': datetime.now(),
                    'num_questions': len(questions)
                }
                collection.insert_one(doc)
            else:
                # JSON storage
                data = self._load_json(self.questions_file)
                data.append({
                    'questions': questions,
                    'content_hash': content_hash,
                    'created_at': datetime.now().isoformat(),
                    'num_questions': len(questions)
                })
                self._save_json(self.questions_file, data)
            return True
        except Exception as e:
            print(f"Error saving questions: {e}")
            return False
    
    def get_questions_by_hash(self, content_hash: str) -> Optional[List[Dict]]:
        """Retrieve cached questions by content hash."""
        try:
            if self.use_mongodb:
                collection = self.db['questions']
                doc = collection.find_one({'content_hash': content_hash})
                return doc['questions'] if doc else None
            else:
                data = self._load_json(self.questions_file)
                for entry in reversed(data):
                    if entry.get('content_hash') == content_hash:
                        return entry['questions']
                return None
        except Exception as e:
            print(f"Error retrieving questions: {e}")
            return None
    
    def get_all_questions(self) -> List[Dict]:
        """Get all saved question sets."""
        try:
            if self.use_mongodb:
                collection = self.db['questions']
                return list(collection.find({}, {'_id': 0}).sort('created_at', -1))
            else:
                return self._load_json(self.questions_file)
        except Exception as e:
            print(f"Error getting questions: {e}")
            return []
    
    # ==================== Quiz History ====================
    
    def save_quiz_attempt(self, results: Dict, answers: List[Dict], user_id: str = "default") -> bool:
        """Save a quiz attempt to history."""
        try:
            entry = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat() if not self.use_mongodb else datetime.now(),
                'results': results,
                'answers': answers,
                'accuracy': results.get('accuracy', 0),
                'num_questions': len(answers),
                'total_time': sum(a.get('response_time', 0) for a in answers)
            }
            
            if self.use_mongodb:
                collection = self.db['quiz_history']
                collection.insert_one(entry)
            else:
                data = self._load_json(self.history_file)
                data.append(entry)
                self._save_json(self.history_file, data)
            return True
        except Exception as e:
            print(f"Error saving quiz attempt: {e}")
            return False
    
    def get_quiz_history(self, user_id: str = "default", limit: int = 50) -> List[Dict]:
        """Get quiz history for a user."""
        try:
            if self.use_mongodb:
                collection = self.db['quiz_history']
                cursor = collection.find(
                    {'user_id': user_id}, 
                    {'_id': 0}
                ).sort('timestamp', -1).limit(limit)
                return list(cursor)
            else:
                data = self._load_json(self.history_file)
                user_history = [d for d in data if d.get('user_id', 'default') == user_id]
                return user_history[-limit:]
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def clear_quiz_history(self, user_id: str = "default") -> bool:
        """Clear quiz history for a user."""
        try:
            if self.use_mongodb:
                collection = self.db['quiz_history']
                collection.delete_many({'user_id': user_id})
            else:
                data = self._load_json(self.history_file)
                data = [d for d in data if d.get('user_id', 'default') != user_id]
                self._save_json(self.history_file, data)
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def get_user_stats(self, user_id: str = "default") -> Dict:
        """Get aggregated stats for a user."""
        history = self.get_quiz_history(user_id, limit=1000)
        
        if not history:
            return {
                'total_quizzes': 0,
                'total_questions': 0,
                'avg_accuracy': 0,
                'best_accuracy': 0,
                'total_time': 0
            }
        
        total_quizzes = len(history)
        total_questions = sum(h.get('num_questions', 0) for h in history)
        accuracies = [h.get('accuracy', 0) for h in history]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        best_accuracy = max(accuracies) if accuracies else 0
        total_time = sum(h.get('total_time', 0) for h in history)
        
        return {
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'avg_accuracy': round(avg_accuracy, 1),
            'best_accuracy': best_accuracy,
            'total_time': round(total_time, 1)
        }
    
    # ==================== Topic Performance ====================
    
    def get_topic_performance(self, user_id: str = "default") -> Dict[str, Dict]:
        """Get performance breakdown by topic."""
        history = self.get_quiz_history(user_id, limit=1000)
        
        topic_stats = {}
        for attempt in history:
            for answer in attempt.get('answers', []):
                topic = answer.get('topic', 'General')
                if topic not in topic_stats:
                    topic_stats[topic] = {'correct': 0, 'total': 0}
                topic_stats[topic]['total'] += 1
                if answer.get('is_correct'):
                    topic_stats[topic]['correct'] += 1
        
        # Calculate accuracy for each topic
        for topic in topic_stats:
            stats = topic_stats[topic]
            stats['accuracy'] = round(
                (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0,
                1
            )
        
        return topic_stats
    
    # ==================== Helper Methods ====================
    
    def _load_json(self, filepath: str) -> List:
        """Load data from JSON file."""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_json(self, filepath: str, data: List):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()


# Singleton instance
_db_instance = None

def get_database() -> QuizDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = QuizDatabase()
    return _db_instance
