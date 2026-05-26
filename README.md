# AI Compiler MVP 🚀

A production-grade, multi-stage intelligent system that compiles natural language product specifications into complete, executable, and validated application blueprints.
A compiler-style AI system that transforms natural language application requirements into structured, validated, executable application blueprints.

Live Demo

Add your deployed URL here:

https://your-app.onrender.com
Overview

AI Compiler MVP is an execution-aware AI orchestration system designed to convert high-level product requirements into structured application schemas through a deterministic multi-stage pipeline.

Instead of relying on a single monolithic generation step, the system separates:

intent understanding
architectural planning
schema generation
validation
repair
runtime simulation

into isolated compiler-style stages.

The project prioritizes:

reliability
schema consistency
repairability
execution awareness
modular orchestration

over raw generation speed.

Architecture
User Prompt
     ↓
Intent Extraction
     ↓
System Design
     ↓
Schema Generation
     ↓
Validation Engine
     ↓
Repair Engine
     ↓
Runtime Simulation
Core Features
Multi-Stage Compiler Pipeline

The system follows a deterministic compiler-style architecture with isolated execution stages:

Intent Extraction
System Design
Schema Generation
Validation
Repair
Runtime Simulation
Structured Schema Generation

The pipeline generates:

UI Schemas
Database Schemas
API Schemas
Authentication Models
Business Logic Rules
RBAC Policies
Validation Engine

Cross-layer validation checks:

API ↔ Database consistency
Foreign key integrity
Role-based access consistency
Schema completeness
Endpoint validation
Repair Engine

Automatically repairs recoverable inconsistencies:

Missing references
Broken mappings
Invalid schema links
Incomplete structures

This creates a self-healing workflow instead of brittle one-shot generation.

Runtime Simulation Sandbox

Validated schemas are executed inside an in-memory runtime sandbox.

Supports:

GET / POST simulations
Role-based access testing
Database state updates
Runtime execution verification
Example Generated Outputs

The system generates structured executable artifacts such as:

UI Schema
{
  "pages": [
    {
      "name": "Dashboard",
      "path": "/",
      "protected": true
    }
  ]
}
Database Schema
{
  "tables": [
    {
      "name": "task",
      "fields": [
        {
          "name": "id",
          "type": "integer"
        }
      ]
    }
  ]
}
API Schema
{
  "path": "/tasks",
  "method": "POST",
  "auth": true
}
Reliability Strategy

The project prioritizes reliability through:

deterministic intermediate schemas
validation before execution
modular stage isolation
runtime-aware generation
repairable execution flows

The goal is to reduce hallucinated or inconsistent runtime configurations.

Engineering Tradeoffs

The primary engineering tradeoff in this project is balancing:

reliability
execution correctness
latency
orchestration complexity

A deeper validation-oriented pipeline improves consistency and repairability but increases orchestration overhead and response time.

For this MVP, reliability and execution awareness were prioritized over generation speed.

Tech Stack
Python
FastAPI
Pydantic
JSON Schema Validation
Render Deployment
HTML/CSS/JavaScript Frontend
