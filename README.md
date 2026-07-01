<div align="center">

<img src="profile.png" 
     width="160" 
     alt="Sai Sri Laxmi"/>

<br/>
<br/>

### Hi, I'm Sai Sri Laxmi 👋

**B.Tech · IIT Bombay**

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sai-sri-laxmi/)
[![Email](https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:saisrilaxmiryakam@gmail.com)

</div>

## About

My work spans three connected areas. I study **trustworthy NLP** — how
structural properties of language carry information about intent independent of
vocabulary.
I build **agentic and RAG systems** — multi-agent pipelines, dynamic query
decomposition, and runtime hallucination detection for table-grounded LLM answers.
And I research **LLM alignment** — specifically how rewrite-based feedback can
substitute for scarce human preference data in reward model training.

Across all three areas I am drawn to the same question: when does a system
actually know what it is doing, and when is it pattern-matching without
understanding? I want to build systems that are honest about that distinction.

---

## Current Research

### Token-Level Entropy for Hinglish Toxicity Detection
*Manuscript in preparation*

Standard toxicity classifiers fail under lexical evasion: users who replace slurs with misspellings or cross-language equivalents defeat vocabulary-based filters entirely. This work asks whether **structural** properties of code-mixed text — specifically Shannon entropy over token-level language distributions — provide a complementary signal immune to this attack.

**Stack:** Python · scikit-learn · wordfreq · scipy · Logistic Regression · TF-IDF

---

## Projects

### 🔍 RecIntel — AI-Native Recruitment Intelligence
Intelligent recruitment pipeline using LLMs to extract, score, and rank candidates from unstructured resume and JD text. Combines semantic search with structured extraction.

**Stack:** Python · LangChain · FAISS · Hugging Face Transformers · ChromaDB

---

### 🧠 Table Guard - Runtime Hallucination Detection
Real-time system for detecting hallucinated content in LLM outputs using entropy-based uncertainty estimation and retrieval grounding. Flags responses where model confidence diverges from retrieved evidence.

**Stack:** Python · PyTorch · Hugging Face · RAG · ChromaDB

---

### 🤖 Deep Research Agent - Agentic RAG
Multi-agent research system that dynamically spawns N parallel researcher agents at runtime using LangGraph. A critic agent evaluates coverage across agent outputs and triggers additional research passes where gaps exist. Async background tasks with SQLite checkpointing for fault-tolerant state persistence across long-running sessions.

**Stack:** Python · LangGraph · SQLite · async Python

---

## Research Interests

```
Trustworthy AI              →  robustness, calibration, scope-aware systems
Large Language Models       →  hallucination, alignment, uncertainty estimation  
Code-Mixed NLP              →  sociolinguistics, structural features
Multimodal AI               →  vision-language reasoning
Retrieval-Augmented Gen     →  grounding, faithfulness, dynamic retrieval
```

---

## Tech Stack

**Languages**
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

**ML / NLP**
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗_Transformers-FFD21E?style=flat-square)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

**RAG / Retrieval**
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-0467DF?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=flat-square)

**Infra**
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

---

## Publications

**In preparation:**
> *Token-Level Language Entropy as a Robust Structural Signal for Hinglish Toxicity Detection*

---

## Currently

- Writing up entropy-based toxicity detection manuscript for submission
- Building Kavach: open-source Hinglish toxicity shield
- Exploring multimodal reasoning under distribution shift

---

<div align="center">

*Interested in robust NLP, code-mixed language, or trustworthy AI systems?*

[![LinkedIn](https://img.shields.io/badge/Let's_connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sai-sri-laxmi/)

</div>
