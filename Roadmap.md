# Data Engineering Career Roadmap — Zero to Professional (GCP Track)

**Starting point:** Basic Python  
**Target:** Job-ready Data Engineer, GCP-focused  
**Estimated timeline:** 6–8 months at 10–15 hrs/week (adjust to your pace)

This document is both your **study plan** and your **GitHub portfolio blueprint**. The core idea: hiring managers don't hire based on courses finished — they hire based on projects that prove you can build and reason about real pipelines. So every phase below pairs "learn X" with "ship a project that uses X," pushed to GitHub as you go.

---

## 1. How This Repo Should Be Structured

Don't cram everything into one repo. Use **one hub repo + separate project repos**. This is what an experienced recruiter/tech lead expects to see on a profile.

```
github.com/yourname/
│
├── data-engineering-journey/     ← THE HUB REPO (this file lives here)
│   ├── README.md                 ← Your roadmap, progress tracker, links to all projects
│   ├── notes/                    ← Phase-by-phase learning notes (markdown)
│   └── resources.md              ← Curated links you actually used
│
├── de-project-01-batch-etl/            ← Phase 4 project
├── de-project-02-gcp-warehouse/        ← Phase 5 project
├── de-project-03-spark-processing/     ← Phase 6 project
├── de-project-04-streaming-pipeline/   ← Phase 7 project
├── de-project-05-iac-cicd-pipeline/    ← Phase 8 project
└── de-capstone-realtime-analytics-platform/  ← Phase 10 flagship project
```

**Why separate repos:** each one gets pinned individually on your GitHub profile (you can pin 6), each has its own clean README/architecture diagram, and a recruiter skimming your profile sees 6 distinct, well-labeled proofs of skill instead of one messy folder.

---

## 2. The Learning Loop (repeat every phase)

This is the "process and flow" you asked about — follow this loop for every phase below:

1. **Learn** the concept (course/docs/book) — timebox it, don't over-consume theory.
2. **Mini-build**: a throwaway script/notebook just to prove you understand the mechanic.
3. **Real project**: apply it to an actual dataset solving an actual problem.
4. **Document**: write the README *as if explaining to a hiring manager* (problem → architecture → tech → how to run → what you'd improve).
5. **Push**: clean commits, `.gitignore`, no secrets, working code on `main`.
6. **Reflect**: 3–5 bullet points in `notes/phaseXX.md` in your hub repo — what broke, what you learned. This becomes interview material later.
7. **Revisit**: when you learn the next phase's tool, go back and upgrade an earlier project with it (e.g., add orchestration to your Phase 4 ETL once you learn Airflow). This shows growth in commit history, which recruiters do notice.

---

## 3. Phase-by-Phase Roadmap

### Phase 0 — Tooling Setup (~1 week)
- Git & GitHub workflow (branches, PRs, commit hygiene)
- Linux/bash basics, VS Code, virtual environments
- **Deliverable:** hub repo created, README skeleton in place

### Phase 1 — Python for Data Engineering (~2–3 weeks)
Since you already know basic Python, focus on the DE-specific parts:
- Working with files (CSV, JSON, Parquet), `pathlib`
- APIs: `requests`, pagination, auth, rate limiting
- Error handling, logging, writing reusable modules/packages
- `pytest` basics — DEs are expected to write testable code
- **Project:** a script that pulls data from a public API, cleans it, and writes it to local Parquet files with logging + tests.

### Phase 2 — SQL Mastery (~3 weeks)
- Core SQL, joins, subqueries
- Window functions, CTEs, query optimization, `EXPLAIN ANALYZE`
- Postgres locally (Docker container)
- **Project:** solve 30–40 SQL problems (StrataScratch/LeetCode DB) + write a document analyzing a real dataset with advanced SQL queries.

### Phase 3 — Data Modeling & Warehousing (~2 weeks)
- OLTP vs OLAP, normalization, star/snowflake schema
- Slowly Changing Dimensions (SCD Type 1/2)
- Kimball dimensional modeling basics
- **Project:** design and diagram a star schema for a sample e-commerce dataset; implement it in Postgres.

### Phase 4 — ETL/ELT + Orchestration (~3 weeks)
- ETL vs ELT, Airflow (DAGs, operators, scheduling, sensors)
- dbt basics (models, tests, docs) for the "T" in ELT
- **Project (`de-project-01-batch-etl`):** Airflow DAG that extracts from an API/DB → lands raw data → transforms with dbt → loads into a warehouse. This is your first real portfolio piece.

### Phase 5 — GCP Core Services (~4 weeks)
This is your cloud specialization:
- **BigQuery** (partitioning, clustering, cost control, SQL)
- **Cloud Storage** (data lake structuring — raw/staging/curated zones)
- **Cloud Composer** (managed Airflow on GCP)
- **Dataflow** (Apache Beam) for scalable batch/stream processing
- **Pub/Sub** basics, IAM & service accounts
- **Project (`de-project-02-gcp-warehouse`):** migrate/rebuild Phase 4's pipeline fully on GCP — GCS data lake → Dataflow/Beam transform → BigQuery warehouse, orchestrated by Cloud Composer.

### Phase 6 — Big Data Processing (~3 weeks)
- Apache Spark fundamentals (or deepen Beam/Dataflow if you want to stay GCP-native)
- Partitioning, shuffling, performance tuning basics
- **Project (`de-project-03-spark-processing`):** process a large (multi-GB) public dataset (e.g., NYC taxi data) with Spark on Dataproc, benchmark against a naive Pandas approach.

### Phase 7 — Streaming Pipelines (~3 weeks)
- Pub/Sub + Dataflow streaming, windowing, watermarks
- Kafka fundamentals (concepts transfer even if you deploy on GCP)
- **Project (`de-project-04-streaming-pipeline`):** simulate a real-time event stream (e.g., clickstream) → Pub/Sub → Dataflow streaming job → BigQuery, with a small dashboard (Looker Studio) showing live metrics.

### Phase 8 — IaC, Containers & CI/CD (~3 weeks)
- Docker (containerize your pipelines)
- Terraform for provisioning GCP resources
- GitHub Actions / Cloud Build for CI/CD (auto-deploy DAGs, run tests on push)
- **Project (`de-project-05-iac-cicd-pipeline`):** take any earlier project and make its infrastructure fully reproducible via Terraform + auto-deployed via GitHub Actions. This project alone signals "production-minded," which is rare among junior candidates.

### Phase 9 — Data Quality & Monitoring (~2 weeks)
- dbt tests, Great Expectations, schema validation
- Logging, alerting (email/Slack on pipeline failure), basic observability
- **Deliverable:** retrofit data quality checks + alerting into 2 of your existing projects (shows maturity, not just a standalone repo).

### Phase 10 — Capstone Project (~4–6 weeks)
**This is the flagship repo you lead with in interviews.** Combine everything:
- Ingest real-time + batch data (Pub/Sub + scheduled batch)
- Data lake (GCS) → processing (Dataflow/Spark) → warehouse (BigQuery)
- Orchestrated with Composer/Airflow, IaC via Terraform, CI/CD via GitHub Actions
- Data quality tests + monitoring/alerting
- A dashboard on top (Looker Studio) showing business-relevant metrics
- **Repo name:** `de-capstone-realtime-analytics-platform`
- Write a detailed architecture README with a diagram (use draw.io or Excalidraw) — this is the single most-viewed file in your entire portfolio.

### Phase 11 — Job Readiness (ongoing, run in parallel with Phase 8–10)
- Resume: quantify impact in project bullets ("processed X GB/day," "reduced pipeline runtime by X%")
- Polish all repo READMEs (see template below)
- SQL + Python + system design mock interviews
- LinkedIn posts documenting your build process (recruiters do look)
- Target roles: apply once Phase 4–5 projects are live; don't wait for the capstone to start applying

---

## 4. README Template for Every Project Repo

Use this exact structure for each project — consistency across repos looks professional:

```markdown
# Project Name

## Problem
What real-world problem does this solve? (1-2 sentences)

## Architecture
[diagram image]
Short explanation of data flow: source → processing → storage → consumption

## Tech Stack
- Language:
- Orchestration:
- Storage/Warehouse:
- Infra:

## How to Run
Step-by-step setup instructions (assume the reader has never seen this repo)

## Key Design Decisions
Why you chose X over Y (e.g., "chose partitioning by date because...")

## Results / What I'd Improve
Metrics if possible, plus honest next steps
```

---

## 5. Suggested Timeline Overview

| Phase | Focus | Duration | Repo |
|---|---|---|---|
| 0 | Setup | 1 wk | hub repo |
| 1 | Python for DE | 2–3 wk | mini-project (in hub) |
| 2 | SQL | 3 wk | mini-project (in hub) |
| 3 | Data Modeling | 2 wk | mini-project (in hub) |
| 4 | ETL + Airflow | 3 wk | project-01 |
| 5 | GCP Core | 4 wk | project-02 |
| 6 | Spark/Big Data | 3 wk | project-03 |
| 7 | Streaming | 3 wk | project-04 |
| 8 | IaC/CI-CD | 3 wk | project-05 |
| 9 | Data Quality | 2 wk | retrofit |
| 10 | Capstone | 4–6 wk | capstone |
| 11 | Job Prep | ongoing | resume/LinkedIn |

**Total: ~28–32 weeks (~6.5–7.5 months)**

---

## 6. Start Now

Your very next actions:
1. Create the `data-engineering-journey` hub repo with this file as its README.
2. Set up Phase 0 (Git, Docker, VS Code).
3. Start Phase 1 with the API-ingestion mini-project.

Come back to me at the end of each phase — I can review your project READMEs, help design the architecture diagrams, debug pipeline code, or mock-interview you on what you just built.