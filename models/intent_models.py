from pydantic import BaseModel, Field
from typing import List, Optional

class IntentModel(BaseModel):
    core_domain: str = Field(..., description="The main business domain or industry segment of the app.")
    key_features: List[str] = Field(default_factory=list, description="Top key feature requirements.")
    entities: List[str] = Field(default_factory=list, description="Key database entity/object names extracted from user description.")
    roles: List[str] = Field(default=["user", "premium", "admin"], description="User personas/access roles.")
    monetization: str = Field(..., description="Details regarding premium gateways, fees, or features.")
    workflows: List[str] = Field(default_factory=list, description="High-level workflows or user sequences.")
    assumptions: List[str] = Field(default_factory=list, description="Implicit or explicit compilation assumptions made.")
