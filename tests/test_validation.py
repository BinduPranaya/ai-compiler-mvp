import pytest
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.validation.validator import SchemaValidator
from pipeline.repair.repair_engine import RepairEngine
from models.schema_models import SystemSchema, DBSchema, DBTableSchema, DBFieldSchema, UISchema, APISchema, AuthSystemSchema
import datetime

@pytest.fixture
def base_broken_schema():
    # Construct an intentionally broken schema
    db_schema = DBSchema(
        tables=[
            # Table 1: Missing primary key
            DBTableSchema(
                name="task",
                fields=[
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="status", type="string")
                ],
                indexes=[]
            ),
            # Table 2 & 3: Cyclic reference (node_a.b_id -> node_b.id and node_b.a_id -> node_a.id)
            DBTableSchema(
                name="node_a",
                fields=[
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="node_b_id", type="integer", foreign="node_b.id")
                ],
                indexes=[]
            ),
            DBTableSchema(
                name="node_b",
                fields=[
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="node_a_id", type="integer", foreign="node_a.id")
                ],
                indexes=[]
            )
        ],
        relations={}
    )

    ui_schema = UISchema(pages=[])
    api_schema = APISchema(endpoints=[])
    auth_system = AuthSystemSchema(provider="jwt", roles=["user", "premium", "admin"], permissions={}, premium_gating={})

    return SystemSchema(
        app_name="BrokenApp",
        generated_at=datetime.datetime.utcnow().isoformat() + "Z",
        intent_summary="Validation test",
        ui_schema=ui_schema,
        db_schema=db_schema,
        api_schema=api_schema,
        auth_system=auth_system
    )

def test_validation_errors_detection(base_broken_schema):
    validator = SchemaValidator()
    report = validator.validate(base_broken_schema)
    
    assert report["status"] == "FAILED"
    
    # Assert missing PK error exists
    pk_errors = [e for e in report["errors"] if e["rule"] == "PRIMARY_KEY_EXISTS"]
    assert len(pk_errors) == 1
    assert pk_errors[0]["table"] == "task"

    # Assert cyclic reference error exists
    cycle_errors = [e for e in report["errors"] if e["rule"] == "NO_CYCLIC_DEPENDENCIES"]
    assert len(cycle_errors) == 1
    assert "node_a" in cycle_errors[0]["cycle"]
    assert "node_b" in cycle_errors[0]["cycle"]

def test_repair_engine_heals_schema(base_broken_schema):
    validator = SchemaValidator()
    repair_engine = RepairEngine()
    
    # Run initial validation
    report = validator.validate(base_broken_schema)
    assert report["status"] == "FAILED"
    
    # Heal the schema
    logs = []
    healed_schema = repair_engine.heal(base_broken_schema, report["errors"], logs)
    
    # Re-validate healed schema
    post_heal_report = validator.validate(healed_schema)
    
    # Assert all healed successfully!
    assert post_heal_report["status"] == "PASSED"
    assert len(post_heal_report["errors"]) == 0
    
    # Check that PK was injected into task table
    task_table = next(t for t in healed_schema.db_schema.tables if t.name == "task")
    assert any(f.name == "id" and f.primary for f in task_table.fields)

    # Check that cyclic reference was broken
    node_b_table = next(t for t in healed_schema.db_schema.tables if t.name == "node_b")
    node_a_link_field = next(f for f in node_b_table.fields if f.name == "node_a_id")
    assert node_a_link_field.foreign is None  # FK constraint removed to heal the cycle
