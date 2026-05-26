from typing import Any

class BackendCodeGenerator:
    """
    Python FastAPI REST API Code Generator.
    Translates a compiled SystemSchema into runnable Python backend server code.
    """

    def generate(self, schema: Any) -> str:
        lines = []
        lines.append(f"\"\"\"")
        lines.append(f"FastAPI Backend Application for {schema.app_name}")
        lines.append(f"Generated at: {schema.generated_at}")
        lines.append(f"\"\"\"\n")
        lines.append("from fastapi import FastAPI, Depends, HTTPException, status")
        lines.append("from fastapi.security import OAuth2PasswordBearer")
        lines.append("from pydantic import BaseModel, EmailStr")
        lines.append("from typing import List, Optional, Dict, Any")
        lines.append("import uvicorn")
        lines.append("\napp = FastAPI(")
        lines.append(f"    title=\"{schema.app_name} API\",")
        lines.append(f"    description=\"API documentation for {schema.app_name}. compiled from NLP description.\",")
        lines.append("    version=\"1.0.0\"")
        lines.append(")")
        lines.append("\noauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"/api/auth/login\")")
        lines.append("\n# ========================================================")
        lines.append("# DATA TRANSFER MODELS (PYDANTIC SCHEMAS)")
        lines.append("# ========================================================")
        
        # 1. Generate Pydantic Models for each database table
        for table in schema.db_schema.tables:
            tbl_cap = table.name.capitalize()
            lines.append(f"\nclass {tbl_cap}Base(BaseModel):")
            
            field_added = False
            for field in table.fields:
                if field.primary:
                    continue
                
                # Simple type converter
                t_str = "str"
                if field.type == "integer":
                    t_str = "int"
                elif field.type == "float":
                    t_str = "float"
                elif field.type == "boolean":
                    t_str = "bool"

                if field.name == "email":
                    t_str = "str"  # Can be expanded to EmailStr
                    
                opt_tag = "Optional[" if field.foreign or field.unique else ""
                end_tag = "] = None" if field.foreign or field.unique else ""
                lines.append(f"    {field.name}: {opt_tag}{t_str}{end_tag}")
                field_added = True
            
            if not field_added:
                lines.append("    pass")
                
            lines.append(f"\nclass {tbl_cap}Create({tbl_cap}Base):")
            lines.append("    pass")
            
            lines.append(f"\nclass {tbl_cap}({tbl_cap}Base):")
            lines.append("    id: int")
            lines.append("\n    class Config:")
            lines.append("        from_attributes = True")

        lines.append("\n# ========================================================")
        lines.append("# SECURITY & AUTH DEPENDENCY")
        lines.append("# ========================================================")
        lines.append("""
def get_current_user_role(token: str = Depends(oauth2_scheme)) -> str:
    # Decodes JWT and extracts user access privileges
    # Simulated auth decoder
    if token.startswith("simulated_jwt_token_admin"):
        return "admin"
    elif token.startswith("simulated_jwt_token_premium"):
        return "premium"
    return "user"
""")

        lines.append("\n# ========================================================")
        lines.append("# ENDPOINTS IMPLEMENTATION")
        lines.append("# ========================================================")

        # 2. Generate API Endpoints
        for ep in schema.api_schema.endpoints:
            # Skip dynamic parameters brackets for Python decorators
            python_path = ep.path.replace("{id}", "{record_id}")
            
            lines.append(f"\n@app.{ep.method.lower()}(\"{schema.api_schema.base_url}{python_path}\")")
            
            fn_name = ep.path.replace("/", "_").replace("{id}", "by_id").strip("_")
            fn_name = f"{ep.method.lower()}_{fn_name}"
            
            params = []
            if "record_id" in python_path:
                params.append("record_id: int")
                
            if ep.method == "POST" and ep.body:
                # Deduce target resource model
                res_name = ep.path.split("/")[-1].rstrip("s")
                if res_name == "categorie":
                    res_name = "category"
                elif res_name == "propertie":
                    res_name = "property"
                
                # Check model existence
                pyd_model = f"{res_name.capitalize()}Create"
                if any(t.name == res_name for t in schema.db_schema.tables):
                    params.append(f"payload: {pyd_model}")
                else:
                    params.append("payload: Dict[str, Any]")

            if ep.auth:
                params.append("role: str = Depends(get_current_user_role)")

            params_str = ", ".join(params)
            lines.append(f"def {fn_name}({params_str}):")
            
            # Add role restriction assertions
            if ep.auth and ep.allowed_roles:
                lines.append(f"    if role not in {ep.allowed_roles}:")
                lines.append(f"        raise HTTPException(")
                lines.append(f"            status_code=status.HTTP_403_FORBIDDEN,")
                lines.append(f"            detail=\"Role is not authorized to access this resource\"")
                lines.append(f"        )")
                
            lines.append(f"    # TODO: Implement database query hooks")
            lines.append(f"    return {ep.response if ep.response else '{\"success\": True}'}")

        lines.append("\nif __name__ == \"__main__\":")
        lines.append("    uvicorn.run(app, host=\"127.0.0.1\", port=8000)")
        return "\n".join(lines)
