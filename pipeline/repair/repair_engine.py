from typing import Dict, Any, List
from models.schema_models import DBFieldSchema, DBTableSchema

class RepairEngine:
    """
    Stage 4b: Repair Engine (Self-Healing).
    Evaluates validation errors and applies auto-healing rules:
    - PRIMARY_KEY_EXISTS: Automatically injects a primary key `id` field.
    - FOREIGN_KEY_TARGET_TABLE: Resolves missing target tables by creating skeleton structures.
    - NO_CYCLIC_DEPENDENCIES: Breaks circular dependency graphs (e.g., node_a -> node_b -> node_a) 
      by removing the circular foreign key references and mapping them as non-relational or nullable fields.
    - AUTH_ROLES_MAPPED: Injects default roles ['user', 'premium', 'admin'] into protected endpoints that miss access lists.
    """

    def heal(self, schema: Any, errors: List[Dict[str, Any]], logs: List[str]) -> Any:
        logs.append(f"Stage 4b: Repair Engine analyzing {len(errors)} compilation errors...")

        # Keep track of repairs to avoid infinite loops
        repairs_made = []

        # Process each error type
        for err in errors:
            rule = err.get("rule")
            
            # Heal 1: Missing Primary Keys
            if rule == "PRIMARY_KEY_EXISTS":
                tbl_name = err.get("table")
                for table in schema.db_schema.tables:
                    if table.name == tbl_name:
                        # Add primary key
                        table.fields.insert(0, DBFieldSchema(name="id", type="integer", primary=True))
                        repair_msg = f"Auto-Heal: Injected primary key 'id' into table '{tbl_name}'."
                        logs.append(repair_msg)
                        repairs_made.append(repair_msg)

            # Heal 2: Broken Foreign Key Target Tables
            elif rule == "FOREIGN_KEY_TARGET_TABLE":
                tbl_name = err.get("table")
                fld_name = err.get("field")
                for table in schema.db_schema.tables:
                    if table.name == tbl_name:
                        for field in table.fields:
                            if field.name == fld_name and field.foreign:
                                target_table = field.foreign.split(".")[0]
                                # Create target table skeleton
                                schema.db_schema.tables.append(DBTableSchema(
                                    name=target_table,
                                    fields=[
                                        DBFieldSchema(name="id", type="integer", primary=True),
                                        DBFieldSchema(name="name", type="string")
                                    ],
                                    indexes=[]
                                ))
                                repair_msg = f"Auto-Heal: Created skeleton table '{target_table}' because '{tbl_name}.{fld_name}' referenced it."
                                logs.append(repair_msg)
                                repairs_made.append(repair_msg)

            # Heal 3: Circular Table References
            elif rule == "NO_CYCLIC_DEPENDENCIES":
                cycle = err.get("cycle", "")
                nodes = cycle.split(" -> ")
                if len(nodes) >= 2:
                    # Break the cycle by changing the foreign key constraint of the last link to simple integer field
                    broken_table = nodes[-2]  # The table initiating the back-link
                    target_table = nodes[-1]  # The table being linked to
                    
                    healed = False
                    for table in schema.db_schema.tables:
                        if table.name == broken_table:
                            for field in table.fields:
                                if field.foreign and field.foreign.startswith(target_table):
                                    field.foreign = None  # Remove foreign key constraint, keep as plain integer
                                    healed = True
                                    repair_msg = f"Auto-Heal: Broke circular relation by removing foreign key constraint on '{broken_table}.{field.name}' pointing to '{target_table}'."
                                    logs.append(repair_msg)
                                    repairs_made.append(repair_msg)
                                    break
                        if healed:
                            break

            # Heal 4: Protected API endpoint with empty roles
            elif rule == "AUTH_ROLES_MAPPED":
                ep_sig = err.get("endpoint", "")
                for ep in schema.api_schema.endpoints:
                    if f"{ep.method} {ep.path}" == ep_sig:
                        ep.allowed_roles = ["user", "premium", "admin"]
                        repair_msg = f"Auto-Heal: Injected default roles list to protected endpoint '{ep_sig}'."
                        logs.append(repair_msg)
                        repairs_made.append(repair_msg)

        context_repairs = getattr(schema, "_repairs_made", [])
        context_repairs.extend(repairs_made)
        schema._repairs_made = context_repairs

        return schema
