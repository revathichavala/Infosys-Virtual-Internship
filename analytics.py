"""
Analytics - Performance tracking and visualization
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import streamlit as st

# Import logger
try:
    from logger import get_analytics_logger
    logger = get_analytics_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class QuizAnalytics:
    def __init__(self):
        self.history_file = 'quiz_history.json'
        logger.info("QuizAnalytics initialized")
    
    def calculate_results(self, answers: List[Dict]) -> Dict:
        """Calculate quiz results from answers."""
        logger.info(f"Calculating results for {len(answers)} answers")
        if not answers:
            logger.warning("No answers to calculate")
            return {
                'total': 0,
                'correct': 0,
                'incorrect': 0,
                'accuracy': 0,
                'avg_response_time': 0,
                'topic_performance': {},
                'difficulty_performance': {}
            }
        
        total = len(answers)
        correct = sum(1 for a in answers if a['is_correct'])
        incorrect = total - correct
        accuracy = round((correct / total) * 100) if total > 0 else 0
        
        logger.info(f"Quiz results: {correct}/{total} ({accuracy}% accuracy)")
        # Calculate average response time
        response_times = [a.get('response_time', 0) for a in answers]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Topic performance
        topic_performance = {}
        for answer in answers:
            topic = answer.get('topic', 'General')
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if answer['is_correct']:
                topic_performance[topic]['correct'] += 1
        
        # Difficulty performance
        difficulty_performance = {}
        for answer in answers:
            diff = answer.get('difficulty', 'medium')
            if diff not in difficulty_performance:
                difficulty_performance[diff] = {'correct': 0, 'total': 0}
            difficulty_performance[diff]['total'] += 1
            if answer['is_correct']:
                difficulty_performance[diff]['correct'] += 1
        
        return {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            'topic_performance': topic_performance,
            'difficulty_performance': difficulty_performance
        }
    
    def plot_accuracy_pie(self, results: Dict):
        """Plot accuracy pie chart."""
        if not PLOTLY_AVAILABLE:
            st.write(f"Correct: {results['correct']}, Incorrect: {results['incorrect']}")
            return
        
        fig = go.Figure(data=[go.Pie(
            labels=['Correct', 'Incorrect'],
            values=[results['correct'], results['incorrect']],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444']
        )])
        
        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_topic_performance(self, answers: List[Dict]):
        """Plot topic performance bar chart."""
        if not PLOTLY_AVAILABLE:
            st.write("Topic performance visualization requires plotly")
            return
        
        topic_stats = {}
        for answer in answers:
            topic = answer.get('topic', 'General')[:20]
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if answer['is_correct']:
                topic_stats[topic]['correct'] += 1
        
        topics = list(topic_stats.keys())
        accuracies = [
            (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            for stats in topic_stats.values()
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=topics,
                y=accuracies,
                marker_color='#667eea'
            )
        ])
        
        fig.update_layout(
            xaxis_title="Topic",
            yaxis_title="Accuracy (%)",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_difficulty_progression(self, answers: List[Dict]):
        """Plot difficulty progression over time."""
        if not PLOTLY_AVAILABLE:
            st.write("Difficulty progression visualization requires plotly")
            return
        
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        
        question_nums = list(range(1, len(answers) + 1))
        difficulties = [
            difficulty_map.get(a.get('difficulty', 'medium'), 2) 
            for a in answers
        ]
        correct_markers = [
            'green' if a['is_correct'] else 'red' 
            for a in answers
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=question_nums,
            y=difficulties,
            mode='lines+markers',
            line=dict(color='#667eea', width=2),
            marker=dict(size=10, color=correct_markers),
            name='Difficulty'
        ))
        
        fig.update_layout(
            xaxis_title="Question Number",
            yaxis_title="Difficulty Level",
            yaxis=dict(
                tickmode='array',
                tickvals=[1, 2, 3],
                ticktext=['Easy', 'Medium', 'Hard']
            ),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def get_recommendations(self, answers: List[Dict]) -> List[Dict]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Analyze topic performance
        topic_stats = {}
        for answer in answers:
            topic = answer.get('topic', 'General')
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if answer['is_correct']:
                topic_stats[topic]['correct'] += 1
        
        for topic, stats in topic_stats.items():
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            if accuracy >= 80:
                recommendations.append({
                    'type': 'strength',
                    'topic': topic,
                    'message': f"Excellent performance in {topic}! ({accuracy:.0f}% accuracy)"
                })
            elif accuracy < 50:
                recommendations.append({
                    'type': 'weakness',
                    'topic': topic,
                    'message': f"Consider reviewing {topic} - current accuracy is {accuracy:.0f}%"
                })
        
        # Overall recommendations
        total_accuracy = sum(1 for a in answers if a['is_correct']) / len(answers) * 100 if answers else 0
        
        if total_accuracy >= 90:
            recommendations.append({
                'type': 'strength',
                'topic': 'Overall',
                'message': "Outstanding performance! Consider trying harder difficulty levels."
            })
        elif total_accuracy < 60:
            recommendations.append({
                'type': 'weakness',
                'topic': 'Overall',
                'message': "Focus on understanding core concepts before attempting more questions."
            })
        
        return recommendations
    
    def save_to_history(self, results: Dict, answers: List[Dict]):
        """Save quiz results to history file."""
        history = []
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'num_questions': len(answers),
            'accuracy': results['accuracy']
        }
        
        history.append(entry)
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_history(self) -> List[Dict]:
        """Get quiz history."""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def clear_history(self):
        """Clear all quiz history."""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
    
    def plot_history_trend(self, history: List[Dict]):
        """Plot accuracy trend over quiz attempts."""
        if not PLOTLY_AVAILABLE or not history:
            st.write("Trend visualization requires plotly and history data")
            return
        
        # Extract data
        quiz_nums = list(range(1, len(history) + 1))
        accuracies = [h.get('accuracy', 0) for h in history]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=quiz_nums,
            y=accuracies,
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10, color='#764ba2'),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)',
            name='Accuracy'
        ))
        
        # Add trend line if enough data
        if len(history) >= 3:
            import numpy as np
            z = np.polyfit(quiz_nums, accuracies, 1)
            p = np.poly1d(z)
            trend_color = '#10b981' if z[0] > 0 else '#ef4444'
            fig.add_trace(go.Scatter(
                x=quiz_nums,
                y=[p(x) for x in quiz_nums],
                mode='lines',
                line=dict(color=trend_color, width=2, dash='dash'),
                name='Trend'
            ))
        
        fig.update_layout(
            xaxis_title="Quiz Number",
            yaxis_title="Accuracy (%)",
            yaxis=dict(range=[0, 105]),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
