<div align="center">

<h1>📝 QuizForge — LLM-Powered MCQ Generator</h1>

<p><strong>Turn any document into ready-to-use multiple-choice quizzes with Llama 3.1, LangChain, and a two-stage generate-and-review pipeline.</strong></p>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-SequentialChain-1C3C3C?style=flat-square)](https://langchain.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Llama_3.1--8B-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Fireworks](https://img.shields.io/badge/Inference-Fireworks_AI-FF6B35?style=flat-square)](https://fireworks.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

<br/>

<p>
Upload a PDF or TXT, pick a subject + difficulty, get a clean CSV of quiz questions back —<br/>
each one <strong>generated AND reviewed</strong> by Llama 3.1 before it reaches you.
</p>

</div>

---

## 🌟 What Makes This Project Different

LangChain MCQ generators are everywhere. This one earns its place through four engineering choices:

- 🔗 **Two-stage SequentialChain** — generation and review are *separate* LLM passes; the second pass critiques the first and fixes unsuitable questions before the user ever sees them
- 📐 **Structured output enforcement** — strict JSON schema injected into the prompt (`RESPONSE_JSON`) makes the LLM output parseable every time, no regex cleanup needed
- 📦 **Production packaging** — proper `src/mcqgenerator/` Python package with `setup.py`, logging module, and utility separation — not a notebook dump
- ⚡ **Modern stack** — Llama 3.1 8B Instruct served via Fireworks AI (sub-second inference), not a local quantized model running at 2 tokens/second

---

## 🗺️ The Two-Stage Pipeline

```
┌──────────────────────────────────────────────┐
│       User uploads PDF / TXT + settings      │
│   (subject, difficulty, number of MCQs)      │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │   Stage 1 — Quiz Chain   │  Llama 3.1 generates N MCQs
        │   PromptTemplate +       │  with strict JSON schema
        │   LLMChain               │  Output → quiz (JSON string)
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │  Stage 2 — Review Chain  │  Llama 3.1 critiques the quiz
        │  Same LLM, new prompt    │  for difficulty + suitability
        │  Rewrites unsuitable Qs  │  Output → review + corrections
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │   JSON parsing → table   │  Structured to: MCQ | Choices | Correct
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │   Streamlit UI + CSV     │  Preview + one-click download
        └──────────────────────────┘
```

The `SequentialChain` orchestrates both stages — Stage 1's output feeds Stage 2 as input, all in one call from the Streamlit app.

---

## 💬 Example: Generative AI Quiz

**Input:** `data.txt` (an article on Generative AI evolution, GANs, transformers, diffusion models)
**Settings:** Subject = *Generative AI*, Difficulty = *intermediate*, Number = *2*

**Output:**

| # | Question | Choices | Correct |
|---|---|---|---|
| 1 | What is the primary difference between Generative AI and traditional AI systems? | a) Generative AI can only analyze data, while traditional AI can classify data · b) Generative AI can create new content, while traditional AI can only analyze data · c) Generative AI is faster but less accurate · d) Generative AI is only used for image generation | **b** |
| 2 | Which Generative AI model is known for its ability to generate realistic images and videos? | a) Transformers · b) Diffusion Models · c) Variational Autoencoders (VAEs) · d) Generative Adversarial Networks (GANs) | **d** |

Plus a written review pass evaluating whether the difficulty matches "intermediate."

---

## 🔬 How It Works

### Stage 1 — Quiz Generation Prompt

The LLM is given the source text plus a strict instruction to return *only* valid JSON matching a schema:

```python
TEMPLATE_QUIZ = """
{system_msg}
Context: {text}
Your task is to write exactly {number} multiple-choice questions based on the
above content. The questions should be appropriate for {subject} students and
written in a {difficulty} difficulty.
Return ONLY a JSON object matching the format shown in RESPONSE_JSON below.
Do not include any extra explanation.

### RESPONSE_JSON
{response_json}
"""
```

The `RESPONSE_JSON` (loaded from `Response.json`) gives the model a concrete schema to mimic:

```json
{
  "1": {
    "mcq": "multiple choice question",
    "options": {"a": "choice", "b": "choice", "c": "choice", "d": "choice"},
    "correct": "correct answer"
  }
}
```

This pattern — show the model the exact output shape — is dramatically more reliable than describing the format in prose.

### Stage 2 — Review Chain

The generated quiz is fed back into the LLM with a new prompt:

```python
TEMPLATE_REVIEW = """
{system_msg}
Below is a quiz for {subject} students. Review its difficulty in no more
than 50 words. If any question is not suitable, rewrite only the problem
parts in a suitable difficulty.

Quiz:
{quiz}
"""
```

This catches questions that are too easy, too obscure, or off-topic — a critical safety net for educational content.

### SequentialChain Orchestration

Both chains are wired together so a single call produces both outputs:

```python
combined_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["system_msg", "text", "number", "subject",
                     "difficulty", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)
```

---

## 📁 Repository Structure

```
mcq-generator/
├── src/
│   └── mcqgenerator/
│       ├── __init__.py
│       ├── MCQgenerator.py    # SequentialChain definition
│       ├── utils.py           # read_file, get_table_data
│       └── logger.py          # Logging setup
├── app.py                     # Streamlit web interface
├── mcq.ipynb                  # Pipeline development notebook
├── test.py                    # Logging test
├── data.txt                   # Sample input (Generative AI article)
├── Response.json              # JSON schema template
├── quiz.csv                   # Sample output
├── requirements.txt
├── setup.py
└── .env                       # HUGGING_FACE_API_KEY (git-ignored)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Llama 3.1 8B Instruct (via HuggingFace Inference + Fireworks AI) |
| **Orchestration** | LangChain `LLMChain` + `SequentialChain` + `PromptTemplate` |
| **Web UI** | Streamlit |
| **PDF Parsing** | PyPDF2 |
| **Data Handling** | Pandas |
| **Env Management** | python-dotenv |
| **Packaging** | setuptools |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/houdhoudGH/mcq-generator.git
cd mcq-generator
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file:
```
HUGGING_FACE_API_KEY=your-hf-token
```

Get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

### 4. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` 🚀

### 5. Use it
1. Upload a PDF or TXT file
2. Pick subject, difficulty, and number of MCQs
3. Click **Generate MCQs**
4. Download the result as CSV

---

## 🔮 Roadmap

The app ships as a working two-stage RAG-style generator. Five directions for production hardening:

- **Containerization** — Dockerfile + `docker-compose.yml` for one-command deployment
- **CI/CD** — GitHub Actions workflow for automated testing and linting
- **Question variety** — extend beyond MCQs to true/false, fill-in-the-blank, and short-answer
- **Difficulty calibration** — quantitative difficulty scoring instead of free-text labels
- **Multilingual** — generate quizzes in Arabic, French, English from the same source
- **Export formats** — Anki deck, Kahoot CSV, Google Forms import

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

### 🎓 About This Project

QuizForge explores **multi-stage LLM orchestration** — using a generate-then-critique pipeline
to produce educational content more reliable than a single-shot prompt could deliver.

<br>

**Made with 💜 by Gheffari Nour El Houda**

<sub>Master 2 Data Science & NLP · AI Engineer</sub>

<br>

<sub>LangChain · Llama 3.1 · HuggingFace · Streamlit · Fireworks AI</sub>

<br>

<sub>If you found this useful, consider giving the repo a ⭐</sub>

</div>
