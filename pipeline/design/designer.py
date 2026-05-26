from typing import Dict, Any, List
from pipeline.stages import BaseStage

class SystemDesigner(BaseStage):
    """
    Stage 2: System Design.
    Translates extracted intent into structured design guidelines, defining:
    - High-level architecture (e.g., Client-Server, REST, In-Memory DB)
    - Roles and permissions matrix
    - User flows and pages requirements
    - Aesthetic layout tokens (colors, components, responsiveness)
    """

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["logs"].append("Stage 2: Designing system architecture and page matrices...")
        
        intent = context.get("intent")
        if not intent:
            context["logs"].append("Stage 2 ERROR: No intent found in context.")
            return context

        # 1. Map architecture based on intent
        architecture = "Three-Tier Web Application: React SPA Frontend + Python FastAPI REST API Backend + Relational DB / Stateful Simulator Sandbox."
        
        # 2. Build roles and permissions matrix
        # All roles are guaranteed to contain user, premium, admin
        roles_matrix = {
            "user": {
                "read": "Allowed for general public elements and own records.",
                "write": "Allowed for creating own records only.",
                "delete": "Restricted.",
                "special": "None."
            },
            "premium": {
                "read": "Allowed for all public and premium-paywalled elements.",
                "write": "Allowed for unlimited creations.",
                "delete": "Allowed for own records.",
                "special": "Unlock premium features, metrics dashboard, and live analytics."
            },
            "admin": {
                "read": "Full audit capability (read everything).",
                "write": "Full write control.",
                "delete": "Full administrative override (delete anything).",
                "special": "Manage users, inspect billing reports, and configure system rules."
            }
        }

        # 3. Assemble User Flows based on domain workflows
        user_flows = []
        for wf in intent.workflows:
            user_flows.append(wf)
        if not user_flows:
            user_flows = ["Access landing page", "Submit item creation form", "View data listing"]

        # 4. Map intent entities to UI Page structures
        pages = []
        # A dashboard/home is always required
        pages.append({
            "name": "Dashboard",
            "path": "/",
            "layout": "sidebar-grid",
            "protected": False,
            "allowed_roles": ["user", "premium", "admin"]
        })
        
        # Add dynamic management/listing pages for each extracted entity (except user)
        for entity in intent.entities:
            if entity == "user":
                continue
            pages.append({
                "name": f"{entity.replace('_', ' ').capitalize()}s Center",
                "path": f"/{entity}s",
                "layout": "split-view",
                "protected": True,
                "allowed_roles": ["user", "premium", "admin"]
            })

        # Add a premium landing page if monetization mentions premium
        if "premium" in intent.monetization.lower() or "subscription" in intent.monetization.lower() or "unlimited" in intent.monetization.lower():
            pages.append({
                "name": "Billing Hub",
                "path": "/billing",
                "layout": "cards-container",
                "protected": True,
                "allowed_roles": ["user", "premium", "admin"]
            })

        # Add an Admin Panel
        pages.append({
            "name": "Admin Console",
            "path": "/admin",
            "layout": "control-panel",
            "protected": True,
            "allowed_roles": ["admin"]
        })

        # Pack everything into context design
        context["design"] = {
            "architecture": architecture,
            "roles_matrix": roles_matrix,
            "user_flows": user_flows,
            "pages": pages,
            "layout_theme": "Modern Dark Mode - Glassmorphism Theme with deep purple, teal glow, and clean borders."
        }

        context["logs"].append(f"Stage 2 SUCCESS: System designed with {len(pages)} UI pages and {len(roles_matrix)} roles mapped.")
        return context
