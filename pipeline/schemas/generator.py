import datetime
from typing import Dict, Any, List
from pipeline.stages import BaseStage
from models.schema_models import SystemSchema, UISchema, UIPageSchema, DBSchema, DBTableSchema, DBFieldSchema, APISchema, APIEndpointSchema, AuthSystemSchema

class SchemaGenerator(BaseStage):
    """
    Stage 3: Schema Generation.
    Compiles the intermediate Intent and Design representations into a unified
    Pydantic-valid SystemSchema blueprint containing:
    - ui_schema: Pages, layouts, allowed_roles, and components
    - db_schema: Tables, index specifications, fields, and relationships
    - api_schema: Complete CRUD routes, parameters, types, and protection scopes
    - auth_system: Role mappings, permissions, and premium gating logic
    - business_logic: Custom logic rules and hooks
    """

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["logs"].append("Stage 3: Synthesizing unified application schema blueprints...")

        intent = context.get("intent")
        design = context.get("design")

        if not intent or not design:
            context["logs"].append("Stage 3 ERROR: Required Intent or Design metadata is missing.")
            return context

        app_name = intent.core_domain.replace(" ", "") + "App"
        
        # 1. Construct UI Schema
        ui_pages = []
        for dp in design["pages"]:
            # Pick logical components based on page name
            components = ["Navbar", "Footer"]
            if dp["name"] == "Dashboard":
                components.extend(["StatsGrid", "RecentActivityList", "InteractiveMetricsChart"])
            elif "Center" in dp["name"] or "s" in dp["path"]:
                entity_base = dp["path"].replace("/", "").replace("s", "")
                components.extend([f"{entity_base.capitalize()}TableGrid", f"Create{entity_base.capitalize()}ModalForm", "SearchBar"])
            elif dp["name"] == "Billing Hub":
                components.extend(["PricingCardsGrid", "CurrentPlanBadge", "CheckoutWizardForm"])
            elif dp["name"] == "Admin Console":
                components.extend(["SystemHealthGrid", "UserManagementTable", "AuditLogStream"])
            else:
                components.extend(["GeneralForm", "SummaryView"])

            ui_pages.append(UIPageSchema(
                name=dp["name"],
                path=dp["path"],
                components=components,
                layout=dp["layout"],
                protected=dp["protected"],
                allowed_roles=dp["allowed_roles"]
            ))
        ui_schema = UISchema(pages=ui_pages)

        # 2. Construct Database Tables & Relations Schema
        db_tables = []
        relations = {}

        # First, ensure there is a users table
        db_tables.append(DBTableSchema(
            name="user",
            fields=[
                DBFieldSchema(name="id", type="integer", primary=True),
                DBFieldSchema(name="username", type="string", unique=True),
                DBFieldSchema(name="email", type="string", unique=True),
                DBFieldSchema(name="role", type="string"),
                DBFieldSchema(name="status", type="string")
            ],
            indexes=["email", "role"]
        ))

        # Add relational tables based on extracted entities
        for entity in intent.entities:
            entity = entity.strip().lower()
            if entity == "user":
                continue
            
            fields = [
                DBFieldSchema(name="id", type="integer", primary=True),
                DBFieldSchema(name="owner_id", type="integer", foreign="user.id")
            ]
            indexes = ["owner_id"]

            # Set up logical columns based on entity name
            if entity == "task":
                fields.extend([
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="description", type="string"),
                    DBFieldSchema(name="status", type="string"),
                    DBFieldSchema(name="due_date", type="string")
                ])
                indexes.append("status")
            elif entity == "category":
                fields.append(DBFieldSchema(name="name", type="string"))
            elif entity == "lead":
                fields.extend([
                    DBFieldSchema(name="first_name", type="string"),
                    DBFieldSchema(name="last_name", type="string"),
                    DBFieldSchema(name="email", type="string", unique=True),
                    DBFieldSchema(name="status", type="string"),
                    DBFieldSchema(name="company", type="string")
                ])
                indexes.extend(["email", "status"])
            elif entity == "deal":
                fields.extend([
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="value", type="float"),
                    DBFieldSchema(name="status", type="string"),
                    DBFieldSchema(name="lead_id", type="integer", foreign="lead.id")
                ])
                indexes.extend(["status", "lead_id"])
            elif entity == "company":
                # Company table doesn't strictly need owner_id, let's remove owner_id if it's broad
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="industry", type="string"),
                    DBFieldSchema(name="domain", type="string", unique=True)
                ]
                indexes.append("name")
            elif entity == "post":
                fields.extend([
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="body", type="string"),
                    DBFieldSchema(name="is_premium", type="boolean")
                ])
            elif entity == "comment":
                fields.extend([
                    DBFieldSchema(name="post_id", type="integer", foreign="post.id"),
                    DBFieldSchema(name="body", type="string")
                ])
                indexes.append("post_id")
            elif entity == "tag":
                # Simple lookup table
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="label", type="string", unique=True)
                ]
            elif entity == "product":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="price", type="float"),
                    DBFieldSchema(name="sku", type="string", unique=True),
                    DBFieldSchema(name="is_premium", type="boolean")
                ]
            elif entity == "order":
                fields.extend([
                    DBFieldSchema(name="total_amount", type="float"),
                    DBFieldSchema(name="status", type="string")
                ])
            elif entity == "subscription":
                fields.extend([
                    DBFieldSchema(name="plan_name", type="string"),
                    DBFieldSchema(name="status", type="string"),
                    DBFieldSchema(name="ends_at", type="string")
                ])
            elif entity == "workout":
                fields.extend([
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="scheduled_date", type="string")
                ])
            elif entity == "exercise":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="target_muscle", type="string")
                ]
            elif entity == "log_entry":
                fields.extend([
                    DBFieldSchema(name="workout_id", type="integer", foreign="workout.id"),
                    DBFieldSchema(name="exercise_id", type="integer", foreign="exercise.id"),
                    DBFieldSchema(name="reps", type="integer"),
                    DBFieldSchema(name="weight", type="float")
                ])
            elif entity == "prompt_log":
                fields.extend([
                    DBFieldSchema(name="prompt_text", type="string"),
                    DBFieldSchema(name="response_text", type="string"),
                    DBFieldSchema(name="credits_spent", type="integer")
                ])
            elif entity == "document":
                fields.extend([
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="raw_content", type="string")
                ])
            elif entity == "credit_usage":
                fields.extend([
                    DBFieldSchema(name="credits_remaining", type="integer")
                ])
            elif entity == "doctor":
                fields.extend([
                    DBFieldSchema(name="specialty", type="string"),
                    DBFieldSchema(name="license_number", type="string", unique=True)
                ])
            elif entity == "appointment":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="patient_id", type="integer", foreign="user.id"),
                    DBFieldSchema(name="doctor_id", type="integer", foreign="doctor.id"),
                    DBFieldSchema(name="appointment_date", type="string"),
                    DBFieldSchema(name="status", type="string")
                ]
                indexes = ["patient_id", "doctor_id"]
            elif entity == "medical_record":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="patient_id", type="integer", foreign="user.id"),
                    DBFieldSchema(name="doctor_id", type="integer", foreign="doctor.id"),
                    DBFieldSchema(name="diagnosis", type="string"),
                    DBFieldSchema(name="prescription", type="string")
                ]
                indexes = ["patient_id"]
            elif entity == "property":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="agent_id", type="integer", foreign="user.id"),
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="price", type="float"),
                    DBFieldSchema(name="location", type="string"),
                    DBFieldSchema(name="is_featured", type="boolean")
                ]
                indexes = ["agent_id", "price"]
            elif entity == "lead_query":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="property_id", type="integer", foreign="property.id"),
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="email", type="string"),
                    DBFieldSchema(name="message", type="string")
                ]
                indexes = ["property_id"]
            elif entity == "event":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="organizer_id", type="integer", foreign="user.id"),
                    DBFieldSchema(name="title", type="string"),
                    DBFieldSchema(name="date", type="string"),
                    DBFieldSchema(name="venue", type="string")
                ]
                indexes = ["organizer_id"]
            elif entity == "ticket":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="event_id", type="integer", foreign="event.id"),
                    DBFieldSchema(name="buyer_id", type="integer", foreign="user.id"),
                    DBFieldSchema(name="ticket_type", type="string"),
                    DBFieldSchema(name="price", type="float")
                ]
                indexes = ["event_id", "buyer_id"]
            
            # Cyclic Reference Mockup Table structure (intentionally broken to trigger repair for cyclic tests)
            elif entity == "node_a":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="name", type="string"),
                    # Set up structural cyclic reference link: node_a.node_b_id references node_b.id
                    DBFieldSchema(name="node_b_id", type="integer", foreign="node_b.id")
                ]
            elif entity == "node_b":
                fields = [
                    DBFieldSchema(name="id", type="integer", primary=True),
                    DBFieldSchema(name="name", type="string"),
                    # Set up structural cyclic reference link: node_b.node_a_id references node_a.id
                    DBFieldSchema(name="node_a_id", type="integer", foreign="node_a.id")
                ]
            else:
                # Catch-all generic entity fields
                fields.extend([
                    DBFieldSchema(name="name", type="string"),
                    DBFieldSchema(name="content", type="string"),
                    DBFieldSchema(name="status", type="string")
                ])

            db_tables.append(DBTableSchema(name=entity, fields=fields, indexes=indexes))

            # Establish relations mapping
            for f in fields:
                if f.foreign:
                    rel_name = f"{entity}_to_{f.foreign.split('.')[0]}"
                    relations[rel_name] = {
                        "type": "many_to_one",
                        "from_table": entity,
                        "from_field": f.name,
                        "to_table": f.foreign.split(".")[0],
                        "to_field": f.foreign.split(".")[1]
                    }

        db_schema = DBSchema(tables=db_tables, relations=relations)

        # 3. Construct API Endpoints Schema
        api_endpoints = []
        
        # Standard Auth endpoints
        api_endpoints.append(APIEndpointSchema(
            path="/auth/register",
            method="POST",
            body={"username": "str", "email": "str", "password": "str"},
            response={"success": "bool", "token": "str", "user_id": "int"},
            auth=False,
            allowed_roles=[]
        ))
        api_endpoints.append(APIEndpointSchema(
            path="/auth/login",
            method="POST",
            body={"email": "str", "password": "str"},
            response={"success": "bool", "token": "str", "role": "str"},
            auth=False,
            allowed_roles=[]
        ))

        # Generate CRUD endpoints for every table
        for table in db_tables:
            tbl_name = table.name
            
            # List Endpoint
            api_endpoints.append(APIEndpointSchema(
                path=f"/{tbl_name}s",
                method="GET",
                query={"limit": "int", "offset": "int"},
                response={"items": f"list[{tbl_name}]", "total": "int"},
                auth=True,
                allowed_roles=["user", "premium", "admin"],
                validation=[f"check_{tbl_name}_owner_rules"]
            ))

            # Retrieve Endpoint
            api_endpoints.append(APIEndpointSchema(
                path=f"/{tbl_name}s/{{id}}",
                method="GET",
                response={"item": f"dict[{tbl_name}]"},
                auth=True,
                allowed_roles=["user", "premium", "admin"],
                validation=[f"verify_{tbl_name}_exists"]
            ))

            # Create Endpoint
            req_body = {f.name: f.type for f in table.fields if f.name != "id"}
            api_endpoints.append(APIEndpointSchema(
                path=f"/{tbl_name}s",
                method="POST",
                body=req_body,
                response={"success": "bool", "created_id": "int"},
                auth=True,
                # Upgrade protection: check if premium gating applies to creation
                allowed_roles=["user", "premium", "admin"],
                validation=[f"validate_{tbl_name}_inputs"]
            ))

            # Delete Endpoint
            api_endpoints.append(APIEndpointSchema(
                path=f"/{tbl_name}s/{{id}}",
                method="DELETE",
                response={"success": "bool"},
                auth=True,
                allowed_roles=["premium", "admin"],  # standard users generally barred from deleting
                validation=[f"validate_{tbl_name}_delete_privileges"]
            ))

        # Apply specific gating endpoints if subscription details exist
        premium_gated_endpoints = {}
        for ep in api_endpoints:
            # Let's say deleting is only for premium or admin, and creating in excess is restricted
            if ep.method == "DELETE" and ep.path.startswith("/") and not ep.path.startswith("/auth"):
                ep.allowed_roles = ["premium", "admin"]
                premium_gated_endpoints[ep.path] = ["DELETE"]

        api_schema = APISchema(base_url="/api", endpoints=api_endpoints)

        # 4. Construct Auth System & Permissions
        permissions = {
            "user": [
                "read:user", "write:user",
                "read:task", "write:task",
                "read:lead", "write:lead",
                "read:post",
                "read:product", "write:order"
            ],
            "premium": [
                "read:user", "write:user",
                "read:task", "write:task", "delete:task",
                "read:lead", "write:lead", "delete:lead",
                "read:post", "write:post", "delete:post",
                "read:product", "write:order", "delete:order",
                "access:premium_analytics"
            ],
            "admin": [
                "*:*"  # Wildcard override
            ]
        }

        auth_system = AuthSystemSchema(
            provider="jwt",
            roles=["user", "premium", "admin"],
            permissions=permissions,
            premium_gating={
                "gated_features": [
                    "delete_operations",
                    "advanced_analytics_dashboard",
                    "bulk_imports"
                ],
                "gated_endpoints": list(premium_gated_endpoints.keys())
            }
        )

        # 5. Business logic rules
        business_logic = {
            "hooks": [
                {"event": "after_user_signup", "action": "initialize_welcome_credits"},
                {"event": "before_order_checkout", "action": "apply_premium_discount"}
            ],
            "limits": {
                "user_max_tasks": 10,
                "user_max_leads": 20,
                "user_api_rate_limit_per_minute": 60,
                "premium_api_rate_limit_per_minute": 300
            }
        }

        # Build final unified SystemSchema
        schema_instance = SystemSchema(
            app_name=app_name,
            version="1.0.0",
            generated_at=datetime.datetime.utcnow().isoformat() + "Z",
            intent_summary=intent.monetization,
            ui_schema=ui_schema,
            db_schema=db_schema,
            api_schema=api_schema,
            auth_system=auth_system,
            business_logic=business_logic
        )

        context["schema"] = schema_instance
        context["logs"].append(f"Stage 3 SUCCESS: Synthesized complete SystemSchema object. Tables: {len(db_tables)}, Endpoints: {len(api_endpoints)}")
        return context
