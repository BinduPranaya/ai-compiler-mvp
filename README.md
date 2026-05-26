# AI Compiler MVP 🚀

A production-grade, multi-stage intelligent system that compiles natural language product specifications into complete, executable, and validated application blueprints.

## Architecture

The AI Compiler operates as a multi-stage compiler:
1. **Intent Extraction**: Parses user instructions into a structured core domain representation.
2. **System Design**: Translates user requirements into layout design guidelines and role-permission matrices.
3. **Schema Generation**: Builds unified application schemas including UI, DB (relational & indexing), API endpoints, and Auth systems.
4. **Validation & Repair Engine**: Runs semantic integrity checks (e.g. checking for unlinked foreign keys or orphaned API paths) and automatically heals discrepancies.
5. **Runtime Simulator Sandbox**: Launches an in-memory execution state so you can test mock API calls (`GET`, `POST`, `DELETE`) against your compiled design directly from the web dashboard.

---

## Folder Structure

```
ai-compiler-mvp/
├── app/
│   ├── main.py                   # FastAPI application
│   └── config.py                 # Configuration and settings loader
├── pipeline/
│   ├── orchestrator.py           # Runs all compiler stages
│   ├── stages.py                 # Core abstract pipeline stages
│   ├── intent/extractor.py       # Stage 1: Intent Extraction
│   ├── design/designer.py        # Stage 2: Visual System Design
│   ├── schemas/generator.py      # Stage 3: UI, DB, API & Auth Schema Generator
│   ├── validation/validator.py   # Stage 4a: Rules Integrity Checker
│   └── repair/repair_engine.py   # Stage 4b: Validation Repair Engine
├── models/
│   ├── intent_models.py          # Intermediate Intent Pydantic models
│   └── schema_models.py          # Final unified AST configuration schemas
├── runtime/
│   └── simulator.py              # Stateful in-memory database simulator
├── generators/
│   ├── frontend_generator.py     # Exports React code skeletons
│   ├── backend_generator.py      # Exports FastAPI code skeletons
│   └── db_generator.py           # Exports PostgreSQL DDL scripts
├── tests/
│   ├── test_pipeline.py          # Pipeline stage checks
│   ├── test_validation.py        # Validation & repair tests
│   └── test_cases/               # Preset normal & edge-case prompts
├── utils/
│   ├── helpers.py                # Logging & file helpers
│   └── mermaid.py                # Database ERD visualizer syntax builder
└── run.py                        # Quick bootloader
```

## Quick Start

1. Ensure Python 3.9+ is installed.
2. Clone or locate the directory and run:
   ```bash
   python run.py
   ```
3. Open your browser and navigate to:
   [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)
