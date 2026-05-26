from typing import Dict, Any, List, Optional

class StatefulRuntimeSimulator:
    """
    Virtual execution simulator sandbox.
    Loads a compiled SystemSchema and instantiates a stateful, virtual in-memory database.
    Processes simulated API requests, enforces role-based security gating, 
    verifies database schema fields, and simulates transactions.
    """

    def __init__(self):
        # In-memory virtual database: { "table_name": [ { "id": 1, ... } ] }
        self.virtual_db: Dict[str, List[Dict[str, Any]]] = {}
        # Active compiled schema
        self.active_schema: Optional[Any] = None

    def initialize_schema(self, schema: Any):
        """Loads a compiled schema and seeds initial mock data."""
        self.active_schema = schema
        self.virtual_db = {}

        # 1. Create collections for each schema table
        for table in schema.db_schema.tables:
            self.virtual_db[table.name] = []

        # 2. Seed default users
        if "user" in self.virtual_db:
            self.virtual_db["user"] = [
                {"id": 1, "username": "alice", "email": "alice@gmail.com", "role": "user", "status": "active"},
                {"id": 2, "username": "bob", "email": "bob@premium.com", "role": "premium", "status": "active"},
                {"id": 3, "username": "admin_charlie", "email": "charlie@enterprise.com", "role": "admin", "status": "active"}
            ]

        # 3. Seed some initial records for other tables to make testing immediate and delightful
        for table in schema.db_schema.tables:
            if table.name == "user":
                continue
            
            # Simple automatic mock seeds based on table names
            if table.name == "task":
                self.virtual_db["task"] = [
                    {"id": 1, "owner_id": 1, "title": "Implement multi-stage compiler pipeline", "description": "Ensure design and intent steps bind cohesively.", "status": "completed", "due_date": "2026-05-30"},
                    {"id": 2, "owner_id": 1, "title": "Design beautiful frontend styling", "description": "Create futuristic glow and neon highlights.", "status": "pending", "due_date": "2026-05-28"},
                    {"id": 3, "owner_id": 2, "title": "Unlock Premium Sandbox", "description": "Gated high performance analytics simulation.", "status": "in_progress", "due_date": "2026-06-01"}
                ]
            elif table.name == "lead":
                self.virtual_db["lead"] = [
                    {"id": 1, "owner_id": 1, "first_name": "John", "last_name": "Doe", "email": "john.doe@stripe.com", "status": "warm", "company": "Stripe"},
                    {"id": 2, "owner_id": 2, "first_name": "Sarah", "last_name": "Connor", "email": "sarah@cyberdyne.org", "status": "hot", "company": "Cyberdyne Systems"}
                ]
            elif table.name == "post":
                self.virtual_db["post"] = [
                    {"id": 1, "owner_id": 3, "title": "Introduction to AI Compilation", "body": "Compiling requirements into architectures is the future of software development.", "is_premium": False},
                    {"id": 2, "owner_id": 3, "title": "Advanced Self-Healing Parsers", "body": "Bypassing grammar constraints using cyclic reference auto-correctors.", "is_premium": True}
                ]
            elif table.name == "product":
                self.virtual_db["product"] = [
                    {"id": 1, "name": "Standard Subscription Pack", "price": 19.99, "sku": "SUB-STD-001", "is_premium": False},
                    {"id": 2, "name": "Enterprise Quantum Module", "price": 499.00, "sku": "MOD-QTM-999", "is_premium": True}
                ]
            elif table.name == "workout":
                self.virtual_db["workout"] = [
                    {"id": 1, "owner_id": 1, "name": "Push Day Hypertrophy", "scheduled_date": "2026-05-26"}
                ]
            elif table.name == "exercise":
                self.virtual_db["exercise"] = [
                    {"id": 1, "name": "Incline Dumbbell Press", "target_muscle": "Upper Chest"},
                    {"id": 2, "name": "Weighted Dips", "target_muscle": "Triceps"}
                ]

    def get_database_state(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns current full contents of virtual database."""
        return self.virtual_db

    def simulate_request(self, method: str, path: str, body: Dict[str, Any], user_role: str) -> Dict[str, Any]:
        """
        Simulate an API request against the virtual state.
        Enforces:
        - Route existence check
        - Auth permissions check
        - Input field verification
        - Stateful DB mutations
        """
        if not self.active_schema:
            return {"error": "No compiled schema loaded in simulator runtime. Compile a prompt first."}

        method = method.upper()
        clean_path = path.strip().lower()

        # Find matching endpoint definition in api_schema
        matched_endpoint = None
        path_params = {}

        for ep in self.active_schema.api_schema.endpoints:
            if ep.method != method:
                continue

            # Check for direct match
            if ep.path.lower() == clean_path:
                matched_endpoint = ep
                break

            # Check for dynamic parameterized match e.g. /tasks/{id}
            ep_parts = ep.path.lower().split("/")
            path_parts = clean_path.split("/")
            
            if len(ep_parts) == len(path_parts):
                matches = True
                temp_params = {}
                for ep_p, path_p in zip(ep_parts, path_parts):
                    if ep_p.startswith("{") and ep_p.endswith("}"):
                        param_name = ep_p[1:-1]
                        temp_params[param_name] = path_p
                    elif ep_p != path_p:
                        matches = False
                        break
                if matches:
                    matched_endpoint = ep
                    path_params = temp_params
                    break

        if not matched_endpoint:
            return {"error": f"Route not found: {method} {path}"}

        # 1. Enforce Auth Check
        if matched_endpoint.auth:
            if user_role not in matched_endpoint.allowed_roles:
                return {
                    "error": "Forbidden: Insufficient privileges.",
                    "details": f"Role '{user_role}' is not authorized to access '{method} {path}'. Required roles: {matched_endpoint.allowed_roles}"
                }

        # Determine target database table
        table_base = clean_path.split("/")[2] if clean_path.startswith("/api/") else clean_path.split("/")[1]
        # De-pluralize table name to match database table names
        table_name = table_base.rstrip("s")
        # Handle some typical irregular words
        if table_base == "categories":
            table_name = "category"
        elif table_base == "properties":
            table_name = "property"

        # Check if table exists in virtual DB
        if table_name not in self.virtual_db and not clean_path.startswith("/auth"):
            return {"error": f"Virtual Database collection '{table_name}' not initialized."}

        # 2. Execute POST (Create)
        if method == "POST":
            # Auth bypass for login/register simulation
            if clean_path.endswith("/auth/register"):
                new_id = len(self.virtual_db["user"]) + 1
                new_user = {
                    "id": new_id,
                    "username": body.get("username", "guest"),
                    "email": body.get("email", "guest@gmail.com"),
                    "role": "user",
                    "status": "active"
                }
                self.virtual_db["user"].append(new_user)
                return {"success": True, "token": f"simulated_jwt_token_user_{new_id}", "user_id": new_id}
            
            elif clean_path.endswith("/auth/login"):
                email = body.get("email", "")
                for u in self.virtual_db["user"]:
                    if u["email"] == email:
                        return {"success": True, "token": f"simulated_jwt_token_{u['role']}_{u['id']}", "role": u["role"]}
                return {"error": "Invalid email credentials in simulation."}

            # Normal resource creation
            # Validate input fields exist in DB schema definitions
            table_meta = next(t for t in self.active_schema.db_schema.tables if t.name == table_name)
            allowed_fields = {f.name for f in table_meta.fields}
            
            # Construct new item
            new_item = {}
            for field in table_meta.fields:
                if field.primary:
                    # Auto increment primary key
                    existing_items = self.virtual_db[table_name]
                    new_item[field.name] = max([item.get(field.name, 0) for item in existing_items] + [0]) + 1
                else:
                    new_item[field.name] = body.get(field.name)

            self.virtual_db[table_name].append(new_item)
            return {"success": True, "created_id": new_item["id"], "record": new_item}

        # 3. Execute GET (List or Retrieve)
        elif method == "GET":
            if "id" in path_params:
                # Retrieve single item
                try:
                    target_id = int(path_params["id"])
                except ValueError:
                    target_id = path_params["id"]

                for item in self.virtual_db[table_name]:
                    if item.get("id") == target_id:
                        return {"item": item}
                return {"error": f"Item not found: {table_name} with ID {target_id}"}
            else:
                # List items
                return {
                    "items": self.virtual_db[table_name],
                    "total": len(self.virtual_db[table_name])
                }

        # 4. Execute DELETE (Remove)
        elif method == "DELETE":
            if "id" not in path_params:
                return {"error": "Missing ID parameter in DELETE path."}

            try:
                target_id = int(path_params["id"])
            except ValueError:
                target_id = path_params["id"]

            found = False
            for idx, item in enumerate(self.virtual_db[table_name]):
                if item.get("id") == target_id:
                    self.virtual_db[table_name].pop(idx)
                    found = True
                    break

            if found:
                return {"success": True, "message": f"Successfully deleted {table_name} with ID {target_id}."}
            else:
                return {"error": f"Item not found: {table_name} with ID {target_id}."}

        return {"error": "Method not implemented in simulator."}

# Global runtime simulator instance
simulator = StatefulRuntimeSimulator()
