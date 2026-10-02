the flow of the version 2 of this project.
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

I have an existing project called **TalentLens-AI**, an AI-powered resume screening and job matching system.

I want to upgrade the current V1 implementation into **Version 2**. Do NOT redesign the entire project from scratch. First understand the existing codebase and preserve the working components wherever possible.

### Current V1 functionality

The current system:

1. Accepts a Resume PDF.
2. Extracts text using **PyMuPDF**.
3. Uses **Groq LLM (Llama 3.3 70B)** to convert the resume into structured JSON.
4. Accepts a Job Description.
5. Uses the LLM to convert the JD into structured JSON.
6. Uses Pydantic models for structured data.
7. Performs basic rule-based matching between resume and JD.
8. Currently calculates a score primarily from:

   * Skill match
   * Experience match

### Goal of V2

Upgrade the system into a **Hybrid AI Resume–JD Matching System** that combines traditional rule-based matching with semantic similarity using embeddings.

The architecture should be:

Resume PDF + Job Description
↓
Resume/JD Parsing
↓
Structured JSON
↓
┌───────────────────────┐
│    Matching Engine    │
└───────────┬───────────┘
│
┌────────┴────────┐
↓                 ↓
Rule-Based Match    Semantic Match
│                 │
│          Sentence Transformers
│                 │
└────────┬────────┘
↓
Hybrid Scoring
↓
Candidate Analysis
↓
┌────────────┼────────────┐
↓            ↓            ↓
Skill Gap     Job Fit    Explainability
│            │            │
└────────────┼────────────┘
↓
LLM Recommendation
↓
Final Report

### 1. Keep the existing parsing pipeline

Continue using:

* PyMuPDF for PDF extraction
* Groq LLM for structured extraction
* Pydantic for schemas

Do not unnecessarily replace these components.

The resume should be converted into structured information such as:

* Skills
* Education
* Experience
* Projects
* Responsibilities/achievements where useful

The JD should contain:

* Required skills
* Preferred skills
* Experience requirements
* Responsibilities
* Qualifications

### 2. Implement semantic matching

Add **Sentence Transformers** for generating embeddings.

The system should generate embeddings for relevant resume and JD information.

For example:

Resume:
"Built REST APIs using Flask and worked with SQL databases."

JD:
"Experience with backend development, Python APIs and relational databases."

The system should recognize their semantic similarity even when the exact keywords differ.

Use cosine similarity or an equivalent similarity metric.

Do not blindly embed the entire resume and entire JD as one string if a more meaningful section-level comparison is possible.

Prefer comparing relevant sections such as:

* Resume skills ↔ JD skills
* Resume experience ↔ JD experience/responsibilities
* Resume projects ↔ JD responsibilities/requirements

### 3. Build a Hybrid Matching Engine

Combine:

**A. Rule-based matching**

* Exact/normalized skill matching
* Required skill matching
* Experience matching

**B. Semantic matching**

* Embedding similarity
* Section-level semantic similarity

Create a transparent scoring system.

For example:

```text
Final Score =
    Rule-Based Skill Score
    + Semantic Similarity Score
    + Experience Score
```

The weights should be configurable rather than hardcoded throughout the code.

Do not let the LLM arbitrarily invent the final score.

### 4. Add Skill Gap Analysis

The system should identify:

```text
Matched Skills
Missing Required Skills
Missing Preferred Skills
Related/Partially Matched Skills
```

For example:

```text
Matched:
- Python
- SQL
- Machine Learning

Missing:
- Docker
- Kubernetes

Related:
- Flask → Backend/API development
```

Use normalization and semantic similarity where appropriate.

### 5. Add Job Fit Analysis

Generate a structured analysis containing:

* Overall match score
* Skill match
* Semantic relevance
* Experience match
* Relevant projects
* Major gaps

The analysis should be based on evidence extracted from the resume and JD.

### 6. Add Explainable Recommendations

Use the LLM only after the deterministic/semantic analysis is complete.

Give the LLM the structured matching results and ask it to generate:

* Why the candidate matches
* Why the candidate does not match certain requirements
* Important skill gaps
* Resume improvement suggestions
* Skills/projects the candidate could develop

The LLM should NOT independently calculate the candidate score.

### 7. Create a clean final output

The final result should look approximately like:

```text
TALENTLENS-AI REPORT

Overall Match: 78%

Skill Match: 82%
Semantic Match: 76%
Experience Match: 70%

MATCHED SKILLS
✓ Python
✓ SQL
✓ Machine Learning

MISSING SKILLS
✗ Docker
✗ Kubernetes

RELEVANT EXPERIENCE
...

JOB FIT
...

KEY GAPS
...

RECOMMENDATIONS
1. ...
2. ...
3. ...
```

### 8. Code architecture

Refactor the project into clear modules instead of putting everything in one file.

A possible structure:

```text
TalentLens-AI/
│
├── data/
│
├── src/
│   ├── parser/
│   │   ├── resume_parser.py
│   │   └── jd_parser.py
│   │
│   ├── models/
│   │   ├── resume.py
│   │   └── job_description.py
│   │
│   ├── embeddings/
│   │   └── embedding_model.py
│   │
│   ├── matching/
│   │   ├── rule_matcher.py
│   │   ├── semantic_matcher.py
│   │   └── hybrid_matcher.py
│   │
│   ├── analysis/
│   │   ├── skill_gap.py
│   │   └── job_fit.py
│   │
│   ├── recommendations/
│   │   └── recommendation_generator.py
│   │
│   └── pipeline.py
│
├── tests/
├── requirements.txt
├── .env
└── README.md
```

You may modify this structure if the existing project architecture suggests a better organization.

### Important implementation requirements

1. First inspect my existing codebase and explain what needs to change.
2. Do not rewrite working code unnecessarily.
3. Implement V2 incrementally.
4. Keep the system modular so that it can later be converted into a **Multi-Agent System (V3)**.
5. Keep scoring transparent and reproducible.
6. Keep LLM responsibilities separate from deterministic matching.
7. Add error handling for malformed LLM JSON and missing resume/JD fields.
8. Do not introduce unnecessary frameworks.
9. Explain each major implementation decision.
10. Provide the code changes file-by-file.
11. Include a small test/example showing the same resume and JD being evaluated through the new V2 pipeline.

The final V2 should be a **hybrid resume screening system**, not a multi-agent system. 

### Embedding Model and Fallback

Use `sentence-transformers/all-MiniLM-L6-v2` as the primary semantic embedding model.

Use cosine similarity for comparing resume and JD embeddings.

The embedding component must be isolated behind an `EmbeddingModel` interface/class so it can be replaced later without changing the matching engine.

If the embedding model cannot be loaded or inference fails:

1. Log the error with sufficient context.
2. Continue processing instead of crashing the entire pipeline.
3. Fall back to the existing rule-based matching system.
4. Recalculate the final score without the semantic component.
5. Set `semantic_matching_available = false`.
6. Clearly indicate in the final report that semantic matching was unavailable.
7. Never replace a failed embedding score with `0`, since that would unfairly penalize the candidate.

If embeddings are available:
`semantic_matching_available = true`

The embedding model name and scoring weights must be configurable through configuration/environment variables rather than hardcoded throughout the application.

ask follow up questions if needed , do takes decisions autonomously , take my approval of major changes except the folder structure .
use this model only : "openai/gpt-oss-120b"