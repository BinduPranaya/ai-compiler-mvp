import re
from typing import Dict, Any, List
from pipeline.stages import BaseStage
from models.intent_models import IntentModel
from app.config import settings

class IntentExtractor(BaseStage):
    """
    Stage 1: Intent Extraction.
    Analyzes the user's natural language input to determine:
    - Core domain
    - Key features
    - Target database entities
    - Roles and permissions
    - Monetization & premium gating
    - Typical workflows
    - Implicit and explicit assumptions
    """

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = context.get("prompt", "").strip()
        context["logs"].append("Stage 1: Extracting intent from user description...")

        # 1. Check if LLM integration is available
        if settings.OPENAI_API_KEY or settings.GEMINI_API_KEY:
            try:
                intent_data = self._extract_using_llm(prompt)
                context["intent"] = intent_data
                context["logs"].append("Stage 1 SUCCESS: Dynamic intent extracted via LLM.")
                return context
            except Exception as e:
                context["logs"].append(f"LLM extraction failed: {str(e)}. Falling back to Rule-Based Extractor.")

        # 2. Rule-Based / Template heuristic matching
        intent_data = self._extract_using_heuristics(prompt)
        context["intent"] = intent_data
        context["logs"].append("Stage 1 SUCCESS: Intent extracted using Rule-Based Engine.")
        return context

    def _extract_using_llm(self, prompt: str) -> IntentModel:
        # Placeholder for dynamic LLM integration. In real execution, this uses openai/google-generativeai client
        # with a structural Pydantic output block.
        raise NotImplementedError("LLM API client not initialized. Using rules engine.")

    def _extract_using_heuristics(self, prompt: str) -> IntentModel:
        prompt_lower = prompt.lower()
        
        # Default fallback intent structure
        domain = "Generic Application"
        features = ["User registration", "Search records", "Dashboard analytics"]
        entities = ["user", "item"]
        roles = ["user", "premium", "admin"]
        monetization = "Standard application model. No gated features requested."
        workflows = ["Sign up and create an account", "Manage records in the database"]
        assumptions = ["Relational DB fits best", "JWT token based security", "Local storage is acceptable"]

        # Template Match 1: Todo / Task Manager
        if "task" in prompt_lower or "todo" in prompt_lower or "to-do" in prompt_lower:
            domain = "Task Management SaaS"
            features = ["Task creation", "Subtask management", "Status workflows", "Category labeling"]
            entities = ["user", "task", "category"]
            monetization = "Premium users get unlimited task folders and collaborative sharing. Basic users capped at 10 tasks."
            workflows = ["Register account", "Create a main task with a due date", "Upgrade to premium to unlock folder sharing"]
            assumptions = ["Tasks belong to exactly one user", "Categories can be shared across tasks"]

        # Template Match 2: CRM SaaS
        elif "crm" in prompt_lower or "customer" in prompt_lower or "sales" in prompt_lower:
            domain = "Enterprise Sales CRM SaaS"
            features = ["Lead tracking", "Pipeline management", "Interactive analytics", "Revenue metrics"]
            entities = ["user", "lead", "deal", "company"]
            monetization = "Premium gating on advanced deals pipeline analytics and company lead imports. Admin manages sales team permissions."
            workflows = ["Create lead", "Convert lead to active deal", "Track revenue in visual pipeline"]
            assumptions = ["Leads are assigned to a single sales rep", "Deals must be associated with a valid lead"]

        # Template Match 3: Blog / Portfolio
        elif "blog" in prompt_lower or "portfolio" in prompt_lower or "article" in prompt_lower:
            domain = "Developer Blog & Publishing Platform"
            features = ["Markdown editing", "Tag system", "Comment management", "Social analytics"]
            entities = ["user", "post", "comment", "tag"]
            monetization = "Premium gating on posts (paywall system). Only premium users read premium posts. Admins moderate comments."
            workflows = ["Author drafts a blog post", "Publish post", "Reader adds comment", "Upgrade reader to premium to view paywalled content"]
            assumptions = ["Post can have multiple tags", "Author is a user with admin or premium creator role"]

        # Template Match 4: E-commerce
        elif "shop" in prompt_lower or "store" in prompt_lower or "commerce" in prompt_lower:
            domain = "Subscription E-Commerce Store"
            features = ["Product catalog", "Cart workflow", "Subscription plans", "Order checkout"]
            entities = ["user", "product", "order", "subscription"]
            monetization = "Premium subscriptions unlock 20% discount on products and free shipping."
            workflows = ["Add product to cart", "Submit checkout with subscription upgrade", "View running active order tracker"]
            assumptions = ["An order consists of multiple products", "Subscriptions recur monthly"]

        # Template Match 5: Gym Tracker
        elif "gym" in prompt_lower or "workout" in prompt_lower or "fitness" in prompt_lower:
            domain = "Fitness and Workout Log Tracker"
            features = ["Workout logging", "Custom routine builder", "Progress trackers", "Calorie counts"]
            entities = ["user", "workout", "exercise", "log_entry"]
            monetization = "Premium gating on custom routine builders and visual performance metrics."
            workflows = ["Select workout routine", "Log workout repetitions and sets", "View progress charts"]
            assumptions = ["Log entries reference a specific user and exercise"]

        # Template Match 6: AI Content Generator
        elif "ai" in prompt_lower or "content" in prompt_lower or "generator" in prompt_lower:
            domain = "AI Automated Writing Platform"
            features = ["Prompt generation", "Revision history", "Template directories", "API integrations"]
            entities = ["user", "prompt_log", "document", "credit_usage"]
            monetization = "Premium users get unlimited AI credits. Basic users are limited to 5 AI requests per day."
            workflows = ["Create standard document prompt", "Generate text via system mock", "Review credit quota depletion"]
            assumptions = ["Each document generation subtracts credits from credit_usage table"]

        # Template Match 7: Hospital Appointment
        elif "hospital" in prompt_lower or "doctor" in prompt_lower or "appointment" in prompt_lower:
            domain = "Medical Appointment Scheduler"
            features = ["Doctor timetables", "Appointment booking", "Patient files", "Medical logs"]
            entities = ["user", "doctor", "appointment", "medical_record"]
            monetization = "Premium subscription enables video consultations and tele-health features."
            workflows = ["Patient schedules appointment", "Doctor completes session and updates patient medical_record"]
            assumptions = ["A medical record is strictly confidential and readable only by authorized doctors and the specific patient"]

        # Template Match 8: Real Estate Listing
        elif "estate" in prompt_lower or "listing" in prompt_lower or "property" in prompt_lower:
            domain = "Real Estate Listing and Broker Platform"
            features = ["Property listing uploads", "Interactive filtering", "Lead generation forms", "Broker maps"]
            entities = ["user", "property", "lead_query", "agent"]
            monetization = "Premium gating: only premium listings are shown at the top of the search grid. Premium users access broker contacts."
            workflows = ["Upload property details", "Submit lead query", "Feature a premium listing to boost organic visibility"]
            assumptions = ["Properties are owned by exactly one agent"]

        # Template Match 9: Event Booking
        elif "event" in prompt_lower or "booking" in prompt_lower or "ticket" in prompt_lower:
            domain = "Event Ticketing & Management"
            features = ["Event listing", "Seat allocations", "Barcode generation", "Attendee lists"]
            entities = ["user", "event", "ticket", "venue"]
            monetization = "Premium tickets grant access to VIP zones. Platform fee applied on standard ticket checkouts."
            workflows = ["Create public event listing", "Purchase standard/premium ticket", "Verify VIP entry status at venue"]
            assumptions = ["Tickets reference a valid user, event, and seat"]

        # Template Match 10: Cyclic Reference Edge Case (For tests & self-healing)
        elif "cyclic" in prompt_lower:
            domain = "Edge Case Sandbox - Cyclic Schema"
            features = ["Cyclic dependencies test", "Verification integrity checking"]
            entities = ["node_a", "node_b"]
            monetization = "Free testing platform."
            workflows = ["Instantiate cyclic models", "Trigger compiler repair engine"]
            assumptions = ["Intentionally broken database relationships for validation test"]

        # Dynamic extraction fallback (heuristics) if not matching standard templates
        else:
            # Extract nouns or camelCase items from the user prompt to guess entities
            words = re.findall(r'\b[A-Za-z]{4,}\b', prompt)
            matched_entities = []
            for w in words:
                if w.lower() in ["user", "post", "task", "project", "ticket", "product", "order", "invoice", "client", "group"]:
                    matched_entities.append(w.lower())
            if matched_entities:
                entities = list(set(["user"] + matched_entities))
            
            # Check for premium keywords
            if "premium" in prompt_lower or "subscribe" in prompt_lower or "paywall" in prompt_lower:
                monetization = "Premium roles are gated from accessing specific actions and database tables."
                
            domain = f"{prompt.split('.')[0][:40]} Application"
            features = [f"Manage {e.capitalize()}s" for e in entities if e != "user"] + ["Role authorization", "Responsive viewports"]

        # Construct Pydantic object
        return IntentModel(
            core_domain=domain,
            key_features=features,
            entities=entities,
            roles=roles,
            monetization=monetization,
            workflows=workflows,
            assumptions=assumptions
        )
