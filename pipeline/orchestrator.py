import json
import os
import time
from typing import Dict, Any, List

from pipeline.intent.extractor import IntentExtractor
from pipeline.design.designer import SystemDesigner
from pipeline.schemas.generator import SchemaGenerator
from pipeline.validation.validator import SchemaValidator
from pipeline.repair.repair_engine import RepairEngine
from app.config import settings

class PipelineOrchestrator:
    """
    Main orchestrator coordinating all compilation stages:
    1. Intent Extraction
    2. System Design 
    3. Schema Generation
    4. Validation & Repair Loop
    5. Save & Dump
    """

    def __init__(self):
        self.extractor = IntentExtractor()
        self.designer = SystemDesigner()
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()
        self.repair_engine = RepairEngine()

    def compile(self, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # Initialize compilation context
        context = {
            "prompt": prompt,
            "logs": ["AI Compiler Booted..."],
            "intent": None,
            "design": None,
            "schema": None,
            "validation_report": None,
            "repairs_made": [],
            "metrics": {}
        }

        try:
            # Stage 1: Intent Extraction
            context = self.extractor.run(context)

            # Stage 2: System Design
            context = self.designer.run(context)

            # Stage 3: Schema Generation
            context = self.generator.run(context)

            # Stage 4: Validation & Repair Loop
            schema = context["schema"]
            if schema:
                # Track repairs inside schema class
                schema._repairs_made = []
                
                validation_report = self.validator.validate(schema)
                context["logs"].append(f"Initial Validation completed. Status: {validation_report['status']}.")
                
                max_healing_rounds = 3
                round_num = 1
                
                while validation_report["status"] == "FAILED" and round_num <= max_healing_rounds:
                    context["logs"].append(f"Validation FAILED in Round {round_num}. Invoking Repair Engine...")
                    
                    # Apply repairs
                    schema = self.repair_engine.heal(schema, validation_report["errors"], context["logs"])
                    
                    # Re-validate
                    validation_report = self.validator.validate(schema)
                    context["logs"].append(f"Validation Round {round_num} Post-Heal Status: {validation_report['status']}")
                    
                    round_num += 1

                # Sync back repaired schema & list of completed repairs
                context["schema"] = schema
                context["repairs_made"] = getattr(schema, "_repairs_made", [])
                context["validation_report"] = validation_report
            else:
                context["logs"].append("Stage 4 ERROR: Skipping validation because Schema was not generated.")

            # Stage 5: Save compiled JSON
            if context["schema"]:
                self._save_blueprint(context["schema"])
                context["logs"].append(f"Stage 5 SUCCESS: Saved compiled blueprint to '{settings.OUTPUT_PATH}'.")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            context["logs"].append(f"FATAL COMPILER ERROR: {str(e)}\n{error_trace}")
            context["validation_report"] = {
                "status": "FATAL_ERROR",
                "errors": [{"message": str(e), "trace": error_trace}]
            }

        elapsed = time.time() - start_time
        context["metrics"]["compilation_time_ms"] = round(elapsed * 1000, 2)
        context["logs"].append(f"AI Compiler complete in {context['metrics']['compilation_time_ms']}ms.")

        return context

    def _save_blueprint(self, schema_instance: Any):
        # Convert schema to dict
        schema_dict = schema_instance.model_dump()
        
        # Ensure directories exist
        out_dir = os.path.dirname(settings.OUTPUT_PATH)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(settings.OUTPUT_PATH, "w") as f:
            json.dump(schema_dict, f, indent=2)
            
        # Also save a timestamped copy for version control/history
        timestamp = int(time.time())
        history_path = settings.OUTPUT_PATH.replace(".json", f"_{timestamp}.json")
        with open(history_path, "w") as f:
            json.dump(schema_dict, f, indent=2)
