# SMA Test Portal

A lightweight, serverless, client-side Computer Based Test (CBT) portal built specifically for **JEE Main**, **JEE Advanced**, and **NEET** aspirants. The platform delivers timed online assessments with NTA-style UI layouts, client-side KaTeX LaTeX rendering, automated score evaluation, detailed solution keys, and predictive All India Rank (AIR) analytics.

---

## Key Features

* **NTA Examination Engine**: Full-screen capable, interactive question palette tracking Visited, Answered, Unanswered, and Marked for Review states.
* **Math & Chemistry Formula Rendering**: Inline and display math rendered using fast, client-side KaTeX with support for equations, matrix notation, and reaction arrows.
* **Automated Scoring & Solution Analysis**: Instant evaluation supporting:
  * Single-Choice Questions ($+4, -1$)
  * Multiple-Choice Questions with Multi-Correct Combinations ($+4, -2$)
  * Numerical Integer/Decimal Value Questions ($+4, 0$)
* **Instant Rank & Percentile Predictor**: Scaled score normalization mapped against statistical performance curves for JEE Main (out of 300), JEE Advanced (out of 360), and NEET (out of 720).
* **Dedicated Landing Hubs**: Category-specific hubs (`index.html`, `jee-main.html`, `jee-advanced.html`, and `neet.html`) powered by dynamic JSON manifest filtering.
* **One-Command Publishing Pipeline**: Automated Python publishing script (`publish_test.py`) that generates self-contained assessment pages, updates search metadata/manifests, and stages targeted Git commits to GitHub.
* **Adaptive Light & Dark Themes**: System-aware styling powered by Tailwind CSS.

---

## Directory Architecture

```text
sma-test-portal/
├── index.html                  # Central Portal Landing Page
├── jee-main.html               # Dedicated JEE Main Hub
├── jee-advanced.html           # Dedicated JEE Advanced Hub
├── neet.html                   # Dedicated NEET Hub
├── publish_test.py             # CLI Tool to build, sync, and deploy tests
├── .gitignore                  # Git ignore rules (e.g., temporary folders)
├── assets/
│   └── tests-manifest.json     # Master test registry / database
└── tests/
    └── <test-folder-name>/     # Individual test workspace
        ├── test.json           # Question bank, options, answers, & metadata
        ├── index.html          # Auto-generated interactive exam interface
        ├── result.html         # Auto-generated scorecard & step-by-step solutions
        └── images/             # Optional directory for diagrams (q1.png, etc.)
