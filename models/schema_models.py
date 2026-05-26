from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# UI Components Schema
class UIPageComponent(BaseModel):
    name: str
    type: str
    props: Optional[Dict[str, Any]] = None

class UIPageSchema(BaseModel):
    name: str
    path: str
    components: List[str] = Field(..., description="Array of components in this page")
    layout: str
    protected: bool = False
    allowed_roles: List[str] = Field(default_factory=list)

class UISchema(BaseModel):
    pages: List[UIPageSchema]

# DB Schema
class DBFieldSchema(BaseModel):
    name: str
    type: str
    primary: bool = False
    unique: bool = False
    foreign: Optional[str] = None  # Format: "tablename.fieldname"

class DBTableSchema(BaseModel):
    name: str
    fields: List[DBFieldSchema]
    indexes: List[str] = Field(default_factory=list)

class DBSchema(BaseModel):
    tables: List[DBTableSchema]
    relations: Dict[str, Any] = Field(default_factory=dict)

# API Schema
class APIEndpointSchema(BaseModel):
    path: str
    method: str  # GET, POST, PUT, DELETE
    body: Optional[Dict[str, Any]] = Field(default_factory=dict)
    query: Optional[Dict[str, Any]] = Field(default_factory=dict)
    response: Optional[Dict[str, Any]] = Field(default_factory=dict)
    auth: bool = True
    allowed_roles: List[str] = Field(default_factory=list)
    validation: List[str] = Field(default_factory=list)

class APISchema(BaseModel):
    base_url: str = "/api"
    endpoints: List[APIEndpointSchema]

# Auth System Schema
class AuthSystemSchema(BaseModel):
    provider: str = "jwt"
    roles: List[str] = ["user", "premium", "admin"]
    permissions: Dict[str, List[str]] = Field(default_factory=dict)
    premium_gating: Dict[str, Any] = Field(default_factory=dict)

# Unified System Schema
class SystemSchema(BaseModel):
    app_name: str
    version: str = "1.0.0"
    generated_at: str
    intent_summary: str
    ui_schema: UISchema
    db_schema: DBSchema
    api_schema: APISchema
    auth_system: AuthSystemSchema
    business_logic: Dict[str, Any] = Field(default_factory=dict)
