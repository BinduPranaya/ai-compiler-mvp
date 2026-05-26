from typing import Dict, Any, List, Set

class SchemaValidator:
    """
    Stage 4a: Validation.
    Executes deep semantic and structural validations across UI, DB, API, and Auth schemas:
    1. Primary Key Check: Every table must have a primary key field.
    2. Foreign Key Integrity: Every foreign key reference must point to a real table and field.
    3. Cyclic Reference Check: Detects circular references between tables.
    4. UI-API Path Gaps: Checks if UI components expect API routes that don't exist.
    5. Auth and Security: Ensures endpoints have appropriate roles mapped.
    """

    def validate(self, schema: Any) -> Dict[str, Any]:
        report = {
            "status": "PASSED",
            "errors": [],
            "warnings": [],
            "metrics": {
                "tables_checked": len(schema.db_schema.tables),
                "endpoints_checked": len(schema.api_schema.endpoints),
                "pages_checked": len(schema.ui_schema.pages)
            }
        }

        self._check_primary_keys(schema, report)
        self._check_foreign_keys(schema, report)
        self._check_cyclic_dependencies(schema, report)
        self._check_ui_api_alignment(schema, report)
        self._check_auth_boundaries(schema, report)

        if report["errors"]:
            report["status"] = "FAILED"

        return report

    def _check_primary_keys(self, schema: Any, report: Dict[str, Any]):
        for table in schema.db_schema.tables:
            has_pk = any(field.primary for field in table.fields)
            if not has_pk:
                report["errors"].append({
                    "rule": "PRIMARY_KEY_EXISTS",
                    "table": table.name,
                    "message": f"Table '{table.name}' does not have a primary key field defined."
                })

    def _check_foreign_keys(self, schema: Any, report: Dict[str, Any]):
        table_names = {t.name for t in schema.db_schema.tables}
        table_fields = {t.name: {f.name for f in t.fields} for t in schema.db_schema.tables}

        for table in schema.db_schema.tables:
            for field in table.fields:
                if field.foreign:
                    parts = field.foreign.split(".")
                    if len(parts) != 2:
                        report["errors"].append({
                            "rule": "FOREIGN_KEY_FORMAT",
                            "table": table.name,
                            "field": field.name,
                            "message": f"Foreign key format in '{table.name}.{field.name}' is invalid. Must be 'target_table.target_field'."
                        })
                        continue

                    target_table, target_field = parts[0], parts[1]
                    if target_table not in table_names:
                        report["errors"].append({
                            "rule": "FOREIGN_KEY_TARGET_TABLE",
                            "table": table.name,
                            "field": field.name,
                            "message": f"Foreign key '{field.foreign}' references non-existent table '{target_table}'."
                        })
                    elif target_field not in table_fields[target_table]:
                        report["errors"].append({
                            "rule": "FOREIGN_KEY_TARGET_FIELD",
                            "table": table.name,
                            "field": field.name,
                            "message": f"Foreign key '{field.foreign}' references table '{target_table}' but field '{target_field}' does not exist."
                        })

    def _check_cyclic_dependencies(self, schema: Any, report: Dict[str, Any]):
        # Build adjacency list of dependencies
        adj = {}
        for table in schema.db_schema.tables:
            adj[table.name] = set()
            for field in table.fields:
                if field.foreign:
                    target_table = field.foreign.split(".")[0]
                    if target_table != table.name:  # Ignore self-references
                        adj[table.name].add(target_table)

        # Detect cycle in directed graph using DFS
        visited = {}  # 0 = unvisited, 1 = visiting, 2 = visited
        for table in adj:
            visited[table] = 0

        cycle_path = []

        def dfs(node: str) -> bool:
            visited[node] = 1
            cycle_path.append(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    continue
                if visited[neighbor] == 1:
                    cycle_path.append(neighbor)
                    return True
                if visited[neighbor] == 0:
                    if dfs(neighbor):
                        return True
            visited[node] = 2
            cycle_path.pop()
            return False

        for table in adj:
            if visited[table] == 0:
                if dfs(table):
                    cycle_idx = cycle_path.index(cycle_path[-1])
                    cycle_nodes = cycle_path[cycle_idx:]
                    report["errors"].append({
                        "rule": "NO_CYCLIC_DEPENDENCIES",
                        "cycle": " -> ".join(cycle_nodes),
                        "message": f"Circular dependency cycle detected in database relations: {' -> '.join(cycle_nodes)}"
                    })
                    break

    def _check_ui_api_alignment(self, schema: Any, report: Dict[str, Any]):
        # Map existing API endpoints methods and paths
        api_paths = {(ep.method, ep.path.lower()) for ep in schema.api_schema.endpoints}

        # Check if UI components mention specific entity pages but APIs are missing
        for page in schema.ui_schema.pages:
            path_cleaned = page.path.replace("/", "").replace("s", "")
            if path_cleaned and path_cleaned not in ["", "billing", "admin"]:
                # This is a resource list page, check if GET /api/{resource}s exists
                expected_api = ("/api", f"/{path_cleaned}s")
                # Normalize api check: search for GET endpoints matching /{path_cleaned}s
                found = False
                for ep in schema.api_schema.endpoints:
                    if ep.method == "GET" and ep.path.endswith(f"/{path_cleaned}s"):
                        found = True
                        break
                
                if not found:
                    report["warnings"].append({
                        "rule": "UI_API_GAPS",
                        "page": page.name,
                        "message": f"UI Page '{page.name}' manages the collection '{path_cleaned}s' but no matching GET endpoint is exposed in the API Schema."
                    })

    def _check_auth_boundaries(self, schema: Any, report: Dict[str, Any]):
        for ep in schema.api_schema.endpoints:
            if ep.auth and not ep.allowed_roles:
                report["errors"].append({
                    "rule": "AUTH_ROLES_MAPPED",
                    "endpoint": f"{ep.method} {ep.path}",
                    "message": f"Endpoint '{ep.method} {ep.path}' is protected by Auth, but allowed_roles is empty. Nobody will be able to access it."
                })
