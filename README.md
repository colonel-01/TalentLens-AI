# TalentLens-AI (V2)

**TalentLens-AI** is a hybrid AI-powered resume screening and job description matching system. It combines deterministic rule-based matching with semantic text embeddings and explainable LLM insights to evaluate candidate fit without letting the LLM arbitrarily invent match scores.

---

## Architecture Flow

```text
                    TALENTLENS-AI — V2
                           │
                           ▼
                  ┌─────────────────┐
                  │  Input Layer    │
                  │ Resume PDF + JD │
                  └────────┬────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     ┌────────────────┐          ┌────────────────┐
     │ Resume Parser  │          │   JD Parser    │
     │   PyMuPDF      │          │    Groq LLM    │
     └───────┬────────┘          └───────┬────────┘
             │                           │
             ▼                           ▼
     ┌────────────────┐          ┌────────────────┐
     │ Resume JSON    │          │    JD JSON     │
     └───────┬────────┘          └───────┬────────┘
             │                           │
             └─────────────┬─────────────┘
                           ▼
                 ┌────────────────────┐
                 │   Matching Engine   │
                 └─────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      ┌─────────────────┐       ┌─────────────────┐
      │ Rule-Based      │       │ Semantic        │
      │ Matching        │       │ Matching        │
      │                 │       │                 │
      │ Skill overlap   │       │ Embeddings      │
      │ Experience      │       │ Sentence        │
      │                 │       │ Transformers    │
      └────────┬────────┘       └────────┬────────┘
               │                         │
               └───────────┬─────────────┘
                           ▼
                 ┌────────────────────┐
                 │   Hybrid Scoring   │
                 │                    │
                 │ Rule Score         │
                 │ Semantic Score     │
                 │ Experience Score   │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Candidate Analysis │
                 └─────────┬──────────┘
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
       ┌───────────┐ ┌────────────┐ ┌──────────────┐
       │ Skill Gap │ │ Job Fit    │ │ Explainable  │
       │ Analysis  │ │ Analysis   │ │ Insights     │
       └─────┬─────┘ └─────┬──────┘ └──────┬───────┘
             │             │               │
             └─────────────┼───────────────┘
                           ▼
                 ┌────────────────────┐
                 │ LLM Recommendation │
                 │     Generator      │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │   Final Report     │
                 │                    │
                 │ • Match Score      │
                 │ • Matched Skills   │
                 │ • Skill Gaps       │
                 │ • Job Fit          │
                 │ • Recommendations  │
                 └────────────────────┘
```

---

## Key Features

1. **Structured Parsing**
   - **Resume Extraction**: Text extraction using PyMuPDF followed by structured extraction using Groq (`openai/gpt-oss-120b`).
   - **Job Description Extraction**: Structured JSON extraction for title, required/preferred skills, education, experience, and responsibilities.

2. **Isolated Semantic Embeddings (`sentence-transformers/all-MiniLM-L6-v2`)**
   - Section-level comparisons (Skills $\leftrightarrow$ Skills, Projects $\leftrightarrow$ Responsibilities, Work history $\leftrightarrow$ Responsibilities).
   - Encapsulated behind an `EmbeddingModel` class.

3. **Graceful Fallback Handling**
   - If the embedding model fails to load or inference fails, the system logs the incident, falls back to rule-based matching, redistributes weights proportionally, and sets `semantic_matching_available = False`.
   - Candidates are **never** penalized with a `0` score for missing embeddings.

4. **Transparent Hybrid Scoring**
   - Configurable weights via environment variables:
     $$\text{Final Score} = (\text{Rule} \times w_{\text{rule}}) + (\text{Semantic} \times w_{\text{semantic}}) + (\text{Experience} \times w_{\text{exp}})$$

5. **Deep Candidate Analysis**
   - **Skill Gap Analysis**: Matched required/preferred skills, missing skills, and semantically related skills (e.g. Flask $\leftrightarrow$ Backend API development).
   - **Job Fit Analysis**: Evidence-based fit levels, relevant projects detection, and major gap identification.

6. **Explainable LLM Recommendations**
   - The LLM acts purely as a narrator *after* deterministic scores are finalized. It explains why a candidate matches, details missing requirements, and suggests actionable resume and skill improvements without recalculating scores.

---

## Project Structure

```text
resume_parser/
├── data/
│   ├── res.pdf                 # Input Resume PDF
│   └── report.json             # Generated JSON report
├── src/
│   ├── analysis/
│   │   ├── job_fit.py          # Evidence-based job fit analysis
│   │   └── skill_gap.py        # Exact and semantic skill gap analysis
│   ├── embeddings/
│   │   └── embedding_model.py  # Isolated SentenceTransformer wrapper with fallback
│   ├── matching/
│   │   ├── hybrid_matcher.py   # Weighted rule + semantic + experience scoring
│   │   ├── rule_matcher.py     # Skill overlap & experience checking
│   │   └── semantic_matcher.py # Section-level cosine similarity
│   ├── models/
│   │   ├── job_description.py  # Pydantic JD model
│   │   └── resume.py           # Pydantic Resume model
│   ├── parser/
│   │   ├── jd_parser.py        # Groq-powered JD parser
│   │   └── resume_parser.py    # PyMuPDF + Groq resume parser
│   ├── config.py               # Centralized settings & env validation
│   └── pipeline.py             # End-to-end pipeline execution & CLI
├── tests/
│   └── test_pipeline.py        # End-to-end integration test
├── .env                        # Environment configurations
├── pyproject.toml              # Dependencies and build settings
└── README.md
```

---

## Configuration (`.env`)

```ini
GROQ_API_KEY=your_groq_api_key

# Model Selection
LLM_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Scoring Weights (Must sum to 1.0)
WEIGHT_RULE=0.40
WEIGHT_SEMANTIC=0.35
WEIGHT_EXPERIENCE=0.25
```

---

## Installation & Running

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run the Full Pipeline
```bash
uv run python -m src.pipeline data/res.pdf
```

### 3. Run Validation Tests
```bash
uv run python -m tests.test_pipeline
```
