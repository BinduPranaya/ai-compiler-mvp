import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from pipeline.orchestrator import PipelineOrchestrator
from runtime.simulator import simulator

from generators.db_generator import DatabaseCodeGenerator
from generators.backend_generator import BackendCodeGenerator

# FRONTEND GENERATOR REMOVED TEMPORARILY
# from generators.frontend_generator import FrontendCodeGenerator

from utils.mermaid import MermaidERDGenerator


app = FastAPI(
    title="AI Compiler MVP",
    description="Natural language → validated executable application schema",
    version="1.0.0"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Request Models
# =========================

class CompileRequest(BaseModel):
    prompt: str


class SimulateRequest(BaseModel):
    method: str
    path: str
    body: Optional[Dict[str, Any]] = None
    user_role: str = "user"


# =========================
# TEST CASES API
# =========================

@app.get("/api/test-cases")
def get_test_cases():

    test_cases_dir = os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ),
        "tests",
        "test_cases"
    )

    if not os.path.exists(test_cases_dir):
        return []

    cases = []

    for file in os.listdir(test_cases_dir):

        if file.endswith(".json") and file != "seeder.json":

            try:
                with open(
                        os.path.join(test_cases_dir, file),
                        "r",
                        encoding="utf-8"
                ) as f:

                    data = json.load(f)

                    cases.append({
                        "filename": file,
                        "name": data.get("name", file),
                        "prompt": data.get("prompt", ""),
                        "category": data.get("category", "Standard")
                    })

            except Exception:
                pass

    return sorted(cases, key=lambda x: x["filename"])


# =========================
# MAIN COMPILER PIPELINE
# =========================

@app.post("/api/compile")
def compile_prompt(req: CompileRequest):

    if not req.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty."
        )

    # Run multi-stage compiler pipeline
    orchestrator = PipelineOrchestrator()

    result = orchestrator.compile(req.prompt)

    schema = result.get("schema")

    generated_code = {}

    # =========================
    # Runtime Simulation
    # =========================

    if schema:

        simulator.initialize_schema(schema)

        db_gen = DatabaseCodeGenerator()

        be_gen = BackendCodeGenerator()

        erd_gen = MermaidERDGenerator()

        generated_code = {
            "db_ddl": db_gen.generate(schema),
            "backend": be_gen.generate(schema),
            "mermaid": erd_gen.generate(schema)
        }

    # =========================
    # Final Response
    # =========================

    return {
        "logs": result.get("logs", []),

        "schema": (
            schema.model_dump()
            if schema else None
        ),

        "validation": result.get(
            "validation_report",
            {}
        ),

        "repairs_made": result.get(
            "repairs_made",
            []
        ),

        "generated_code": generated_code,

        "metrics": result.get(
            "metrics",
            {}
        )
    }


# =========================
# REQUEST SIMULATOR
# =========================

@app.post("/api/simulate")
def simulate_endpoint(req: SimulateRequest):

    body = req.body or {}

    response = simulator.simulate_request(
        req.method,
        req.path,
        body,
        req.user_role
    )

    return {
        "response": response,
        "db_state": simulator.get_database_state()
    }


# =========================
# DATABASE STATE VIEWER
# =========================

@app.get("/api/db-state")
def get_db_state():

    return simulator.get_database_state()


# =========================
# STATIC FRONTEND
# =========================

frontend_path = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "frontend"
)

if os.path.exists(frontend_path):

    app.mount(
        "/static",
        StaticFiles(directory=frontend_path),
        name="static"
    )


# =========================
# ROOT ROUTE
# =========================

@app.get("/")
def serve_index():

    index_path = os.path.join(
        frontend_path,
        "index.html"
    )

    if os.path.exists(index_path):

        return FileResponse(index_path)

    return {
        "message": "AI Compiler MVP backend running successfully."
    }