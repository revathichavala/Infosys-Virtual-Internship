"""
Question Generator - Uses AI to generate quiz questions
"""

import os
import json
import random
from typing import List, Dict, Optional

# Import logger
try:
    from logger import get_generator_logger
    logger = get_generator_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Try to import OpenAI, fall back to sample questions if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class QuestionGenerator:
    def __init__(self):
        logger.info("Initializing QuestionGenerator...")
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        self.use_groq = False
        self.use_gemini = None
        
        # Priority: Groq > Gemini > OpenAI
        if self.groq_api_key and OPENAI_AVAILABLE:
            logger.info("Using Groq API for question generation")
            self.client = OpenAI(
                api_key=self.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.use_groq = True
        elif self.gemini_api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_gemini = True
        elif self.openai_api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.use_gemini = False
        else:
            self.use_gemini = None  # Use sample questions
    
    def extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from the content using AI."""
        if not (self.use_groq or self.use_gemini is not None):
            # Fallback: extract keywords manually
            return self._extract_keywords_simple(content)
        
        prompt = f"""Analyze the following content and extract the 5-10 most important key concepts, topics, or terms.
Return ONLY a JSON array of strings. Example: ["Machine Learning", "Neural Networks", "Data Processing"]

Content:
{content[:3000]}

Return ONLY the JSON array:"""

        try:
            if self.use_groq:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You extract key concepts. Return only valid JSON array."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                response_text = response.choices[0].message.content
            elif self.use_gemini:
                response = self.model.generate_content(prompt)
                response_text = response.text
            else:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You extract key concepts. Return only valid JSON array."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                response_text = response.choices[0].message.content
            
            # Parse JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                concepts = json.loads(response_text[json_start:json_end])
                return concepts[:10]
        except Exception as e:
            print(f"Concept extraction failed: {e}")
        
        return self._extract_keywords_simple(content)
    
    def _extract_keywords_simple(self, content: str) -> List[str]:
        """Simple keyword extraction without AI."""
        import re
        # Extract capitalized phrases and common patterns
        words = content.split()
        # Get words that start with capital letter and are > 4 chars
        keywords = set()
        for i, word in enumerate(words[:500]):
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if len(clean_word) > 4 and clean_word[0].isupper():
                keywords.add(clean_word)
        return list(keywords)[:8]
    
    def generate_questions(
        self, 
        content: str, 
        num_questions: int = 10,
        question_types: List[str] = None
    ) -> List[Dict]:
        """Generate quiz questions from content."""
        if question_types is None:
            question_types = ['MCQ', 'True/False']
        
        # Try AI generation first
        if self.use_groq or self.use_gemini is not None:
            try:
                return self._generate_with_ai(content, num_questions, question_types)
            except Exception as e:
                print(f"AI generation failed: {e}")
        
        # Fallback to sample questions
        return self._generate_sample_questions(content, num_questions, question_types)
    
    def _generate_with_ai(
        self, 
        content: str, 
        num_questions: int,
        question_types: List[str]
    ) -> List[Dict]:
        """Generate questions using AI."""
        
        type_instructions = {
            'MCQ': 'multiple choice questions with 4 options',
            'True/False': 'true/false questions',
            'Fill in the Blank': 'fill in the blank questions (use ___ for the blank)',
            'Short Answer': 'short answer questions'
        }
        
        types_str = ', '.join([type_instructions.get(t, t) for t in question_types])
        
        prompt = f"""Analyze the following content and generate {num_questions} quiz questions.
Generate a mix of: {types_str}

For each question, provide:
- question: The question text (for fill in the blank, use ___ to indicate the blank)
- answer: The correct answer
- distractors: For MCQ, provide 3 wrong but plausible options (array). Empty array for other types.
- difficulty: easy, medium, or hard
- topic: The main topic/concept being tested
- type: mcq, true_false, fill_blank, or short_answer

Content to analyze:
{content[:4000]}

Return ONLY a valid JSON array of questions. Example format:
[
  {{
    "question": "What is the main concept discussed?",
    "answer": "Correct answer here",
    "distractors": ["Wrong option 1", "Wrong option 2", "Wrong option 3"],
    "difficulty": "medium",
    "topic": "Main Topic",
    "type": "mcq"
  }}
]"""

        if self.use_groq:
            # Use Groq API (fast inference)
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a quiz generator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            response_text = response.choices[0].message.content
        elif self.use_gemini:
            response = self.model.generate_content(prompt)
            response_text = response.text
        else:
            # Use OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quiz generator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            response_text = response.choices[0].message.content
        
        # Parse JSON from response
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                questions = json.loads(json_str)
                return questions
        except json.JSONDecodeError:
            pass
        
        return self._generate_sample_questions(content, num_questions, question_types)
    
    def _generate_sample_questions(
        self, 
        content: str, 
        num_questions: int,
        question_types: List[str]
    ) -> List[Dict]:
        """Generate sample questions when AI is not available."""
        
        # Extract some keywords from content for context
        words = content.split()[:50]
        topic = ' '.join(words[:5]) if words else "General Knowledge"
        
        sample_questions = []
        difficulties = ['easy', 'medium', 'hard']
        
        mcq_templates = [
            {
                "question": "Which of the following best describes the main concept discussed in the material?",
                "answer": "A comprehensive understanding of the topic",
                "distractors": ["A basic overview", "An unrelated concept", "A contradictory idea"],
                "type": "mcq"
            },
            {
                "question": "What is the primary purpose of studying this material?",
                "answer": "To gain knowledge and understanding",
                "distractors": ["Entertainment only", "Memorization without understanding", "To pass time"],
                "type": "mcq"
            },
            {
                "question": "According to the content, what approach is most effective?",
                "answer": "A systematic and thorough approach",
                "distractors": ["A random approach", "Ignoring key details", "Surface-level reading"],
                "type": "mcq"
            }
        ]
        
        tf_templates = [
            {
                "question": "The material provides comprehensive coverage of the topic.",
                "answer": "True",
                "distractors": [],
                "type": "true_false"
            },
            {
                "question": "Understanding the basics is essential before moving to advanced concepts.",
                "answer": "True",
                "distractors": [],
                "type": "true_false"
            },
            {
                "question": "The concepts discussed are only applicable in theoretical scenarios.",
                "answer": "False",
                "distractors": [],
                "type": "true_false"
            }
        ]
        
        short_templates = [
            {
                "question": "What is the key takeaway from this material?",
                "answer": "Understanding and applying the concepts",
                "distractors": [],
                "type": "short_answer"
            },
            {
                "question": "Briefly describe the main topic covered.",
                "answer": "The fundamental concepts and their applications",
                "distractors": [],
                "type": "short_answer"
            }
        ]
        
        fill_blank_templates = [
            {
                "question": "The main purpose of studying this material is to gain ___ of the subject.",
                "answer": "understanding",
                "distractors": [],
                "type": "fill_blank"
            },
            {
                "question": "A ___ approach is recommended when learning new concepts.",
                "answer": "systematic",
                "distractors": [],
                "type": "fill_blank"
            },
            {
                "question": "Effective learning requires both ___ and practice.",
                "answer": "theory",
                "distractors": [],
                "type": "fill_blank"
            }
        ]
        
        all_templates = []
        if 'MCQ' in question_types:
            all_templates.extend(mcq_templates)
        if 'True/False' in question_types:
            all_templates.extend(tf_templates)
        if 'Short Answer' in question_types:
            all_templates.extend(short_templates)
        if 'Fill in the Blank' in question_types:
            all_templates.extend(fill_blank_templates)
        
        if not all_templates:
            all_templates = mcq_templates
        
        for i in range(num_questions):
            template = random.choice(all_templates).copy()
            template['difficulty'] = random.choice(difficulties)
            template['topic'] = topic[:30]
            sample_questions.append(template)
        
        return sample_questions
