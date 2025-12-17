# 🧠 SmartQuizzer - Adaptive AI-Based Quiz Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]https://infosys-virtual-internship-32srcncakjzdmr4kptul2y.streamlit.app/
> 🔗 **Live Demo:** [Click here to try the app]
https://infosys-virtual-internship-32srcncakjzdmr4kptul2y.streamlit.app/

An AI-powered adaptive quiz generator that analyzes study materials and automatically generates relevant quiz questions using NLP and LLMs. Built with Streamlit for an interactive web experience.

## 🎯 Features

### Core Features
- **AI-Powered Question Generation**: Uses Gemini/GPT/Groq to generate diverse question types
- **Multiple Question Types**: MCQ, True/False, Fill-in-the-Blank, Short Answer
- **Adaptive Difficulty**: Adjusts question difficulty based on user performance in real-time
- **Key Concept Extraction**: AI identifies and displays main topics before quiz starts
- **Countdown Timer**: Configurable per-question timer with visual alerts

### Input Options
- 📄 **PDF Files**: Upload and extract text from PDF documents
- 📝 **Text Files**: Upload .txt files
- ✍️ **Pasted Text**: Paste notes or study material directly
- 🔗 **URL Articles**: Fetch content from online articles

### Analytics & Insights
- 📊 **Performance Analytics**: Accuracy breakdown, topic performance charts
- 📈 **Difficulty Progression**: Visual tracking of adaptive difficulty changes
- 💡 **Personalized Recommendations**: AI-driven suggestions based on weak areas
- 📜 **Quiz History**: Track all past attempts with trend analysis
- ⏱️ **Response Time Analysis**: Per-question timing metrics

### Data Storage
- 💾 **Local JSON Storage**: Default lightweight storage
- 🌐 **MongoDB Atlas**: Optional cloud database integration for persistence

## 🛠️ Skills Demonstrated

- Python Scripting
- Natural Language Processing (NLP)
- Large Language Models (LLMs)
- Prompt Engineering
- Streamlit Web Application Development
- MongoDB/JSON Data Storage
- Data Visualization (Plotly)
- API Integration (OpenAI/Google Gemini/Groq)

## 🌍 Domain

- Education Technology (EdTech)
- E-Learning & Assessment Systems
- Artificial Intelligence & NLP
- Adaptive Learning Platforms

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smartquizzer.git
cd smartquizzer
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# AI Provider (choose one or more)
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key

# Optional: MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=smartquizzer
```

**Get API Keys:**
- [Google Gemini](https://makersuite.google.com/app/apikey)
- [OpenAI](https://platform.openai.com/api-keys)
- [Groq](https://console.groq.com/keys) (Free, fast inference)

> **Note**: The app works without API keys using sample questions.

## 🚀 Running the App

```bash
streamlit run app.py
```

Access at `http://localhost:8501`

## 📁 Project Structure

```
SmartQuizzer/
├── app.py                    # Main Streamlit application
├── quiz_engine.py            # Adaptive difficulty & answer checking
├── question_generator.py     # AI question generation & concept extraction
├── analytics.py              # Performance analytics & visualization
├── database.py               # MongoDB & JSON storage handler
├── utils.py                  # File handling & URL fetching
├── requirements.txt          # Python dependencies
├── Procfile                  # Heroku deployment
├── runtime.txt               # Python version
├── setup.sh                  # Deployment setup
└── README.md                 # Documentation
```

## 🎮 How to Use

1. **📚 Upload Content**: Upload PDF/text, paste content, or enter article URL
2. **⚙️ Configure Settings**: Set question count, types, and timer duration
3. **🔑 Review Concepts**: See AI-extracted key concepts before starting
4. **🎯 Take Quiz**: Answer questions with adaptive difficulty & timer
5. **📊 View Results**: Analyze performance with detailed charts
6. **📜 Track History**: Review past attempts and track improvement

## 🔧 Adaptive Algorithm

```python
# Difficulty adjustment logic
if last_3_correct >= 3:
    difficulty = increase()  # easy → medium → hard
elif last_3_correct <= 1:
    difficulty = decrease()  # hard → medium → easy
```

## 📊 Example Question Output

```json
{
  "question": "What is the primary function of neural networks?",
  "answer": "Pattern recognition and learning from data",
  "distractors": ["Data storage", "Network security", "File compression"],
  "difficulty": "medium",
  "topic": "Machine Learning",
  "type": "mcq"
}
```

## 🌐 Deployment Options

### Streamlit Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in dashboard

### Heroku
```bash
heroku create smartquizzer-app
git push heroku main
```

### HuggingFace Spaces
1. Create Space with Streamlit SDK
2. Upload files and configure secrets

### AWS EC2
1. Launch t2.micro instance
2. Install dependencies
3. Run: `streamlit run app.py --server.port 8501`

## 📈 Analytics Visualizations

- **Accuracy Pie Chart**: Correct vs incorrect breakdown
- **Topic Performance Bar Chart**: Performance by subject area
- **Difficulty Progression Line Chart**: How difficulty changed during quiz
- **History Trend Chart**: Accuracy improvement over time

## 🔒 Data Privacy

- Local JSON storage by default (no external data transfer)
- MongoDB optional for cloud persistence
- No personal data collected beyond quiz attempts

## 📝 License

MIT License - Free to use and modify.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

## 📧 Support

Open an issue on GitHub for questions or bug reports.
