import pytest
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.intent.extractor import IntentExtractor
from pipeline.design.designer import SystemDesigner
from pipeline.schemas.generator import SchemaGenerator
from models.intent_models import IntentModel
from models.schema_models import SystemSchema

def test_stage1_intent_extractor():
    extractor = IntentExtractor()
    context = {"prompt": "Create a task manager with premium folders", "logs": []}
    context = extractor.run(context)
    
    assert "intent" in context
    assert isinstance(context["intent"], IntentModel)
    assert context["intent"].core_domain == "Task Management SaaS"
    assert "task" in context["intent"].entities

def test_stage2_system_designer():
    extractor = IntentExtractor()
    designer = SystemDesigner()
    
    context = {"prompt": "Create a simple blog post app", "logs": []}
    context = extractor.run(context)
    context = designer.run(context)
    
    assert "design" in context
    assert "pages" in context["design"]
    assert len(context["design"]["pages"]) > 0
    assert "roles_matrix" in context["design"]

def test_stage3_schema_generator():
    extractor = IntentExtractor()
    designer = SystemDesigner()
    generator = SchemaGenerator()
    
    context = {"prompt": "Create a Sales CRM app", "logs": []}
    context = extractor.run(context)
    context = designer.run(context)
    context = generator.run(context)
    
    assert "schema" in context
    assert isinstance(context["schema"], SystemSchema)
    
    schema = context["schema"]
    assert schema.app_name == "EnterpriseSalesCRMSaaSApp"
    assert len(schema.db_schema.tables) > 1
    assert any(t.name == "lead" for t in schema.db_schema.tables)

def test_pipeline_orchestrator():
    orchestrator = PipelineOrchestrator()
    context = orchestrator.compile("Build a workout logger and custom exercise templates")
    
    assert context["schema"] is not None
    assert context["validation_report"]["status"] == "PASSED"
    assert context["metrics"]["compilation_time_ms"] > 0
