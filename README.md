# 📚 AcademicAnalyser

**AI-Powered PDF Learning & Quiz Evaluation System**

> *"Upload. Learn. Test. Improve."*

---

## 🌟 Overview

AcademicAnalyser is an intelligent academic assistant that transforms PDF study materials into interactive learning experiences. Using Google Gemini AI and Streamlit, it provides:

- 📄 **Smart Summarization** - Get concise summaries of lengthy PDFs
- 🎯 **Topic Extraction** - Identify the most important concepts
- 📝 **Auto Quiz Generation** - Create custom quizzes automatically
- 📊 **Performance Analysis** - Detailed mistake analysis and scoring
- 📚 **Personalized Revision** - AI-generated study plans based on weak areas

---

## 🚀 Features

### Complete Learning Pipeline

```
PDF Upload → Text Extraction → Summary Generation → Topic Identification
                              ↓
Quiz Generation → Take Quiz → Evaluation → Score Report
                              ↓
Mistake Analysis → Weak Topic Detection → Revision Plan
```

### Key Capabilities

- ✅ **PDF Processing** - Extract and clean text from academic PDFs
- ✅ **AI Summarization** - Generate structured summaries using Gemini AI
- ✅ **Smart Topic Detection** - Identify exam-relevant topics automatically
- ✅ **Dynamic Quiz Creation** - Generate 5, 10, or 20 MCQs with explanations
- ✅ **Intelligent Evaluation** - Compare answers and calculate scores
- ✅ **Detailed Feedback** - Explanations for every incorrect answer
- ✅ **Weak Area Analysis** - Identify knowledge gaps by topic
- ✅ **Custom Revision Plans** - Personalized study recommendations

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit |
| **PDF Processing** | pdfplumber, PyPDF2 |
| **AI Engine** | Google Gemini API (gemini-1.5-flash) |
| **Language** | Python 3.10+ |
| **Environment** | python-dotenv |

---

## 📋 Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- pip (Python package manager)

---

## ⚙️ Installation

### 1. Navigate to the Project

```bash
cd AcademicAnalyser
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key:

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create or sign in to your Google account
3. Generate an API key
4. Copy and paste it into `.env`

---

## 🚀 How to Run

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 📖 User Guide

### Step-by-Step Workflow

**1️⃣ Upload PDF**
- Click "Choose a PDF file"
- Select your study material (notes, textbook, paper)
- Click "Process PDF"

**2️⃣ View Summary**
- AI generates a concise summary
- Review key points and concepts
- Continue to topics

**3️⃣ Review Important Topics**
- System extracts 10-15 key topics
- Exam-relevant concepts highlighted
- Proceed to quiz setup

**4️⃣ Configure Quiz**
- Choose quiz size: 5, 10, or 20 questions
- Click "Generate Quiz"
- Wait for AI to create questions

**5️⃣ Take Quiz**
- Answer multiple choice questions
- Navigate using Previous/Next buttons
- Submit when complete

**6️⃣ View Results**
- See your score and grade
- Review detailed mistake analysis
- Identify weak topics
- Get personalized revision plan

---

## 📁 Project Structure

```
AcademicAnalyser/
│
├── app.py                      # Main Streamlit application
│
├── modules/                    # Core functionality modules
│   ├── __init__.py
│   ├── pdf_reader.py          # PDF upload & text extraction
│   ├── text_cleaner.py        # Text preprocessing
│   ├── summary.py             # AI summary generation
│   ├── topic_extractor.py     # Important topics identification
│   ├── quiz_generator.py      # Quiz creation with Gemini
│   ├── evaluator.py           # Answer evaluation & scoring
│   ├── mistake_analysis.py    # Mistake breakdown & weak topics
│   └── recommendation.py      # Revision plan generation
│
├── prompts/                    # AI prompt templates
│   ├── summary_prompt.txt
│   ├── topic_prompt.txt
│   ├── quiz_prompt.txt
│   └── revision_prompt.txt
│
├── data/                       # Sample PDFs (optional)
│   └── sample_pdfs/
│
├── .env                        # Environment variables (create this)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```
