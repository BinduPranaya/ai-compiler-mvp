import os
import json

def seed_test_cases():
    test_cases_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(test_cases_dir, exist_ok=True)

    cases = {
        "case_01_todo.json": {
            "name": "Task Manager SaaS",
            "prompt": "Create a secure Task Manager with custom category tags. Basic users are limited to 10 tasks. Premium users get unlimited tasks, custom folders, and sharing features.",
            "category": "Standard"
        },
        "case_02_crm.json": {
            "name": "Enterprise CRM SaaS",
            "prompt": "Build a Sales Pipeline CRM SaaS to track company leads, deals values, and sales cycles. Premium users unlock detailed deal flow charts and conversions analytics.",
            "category": "Standard"
        },
        "case_03_blog.json": {
            "name": "Developer Blog & Publishing",
            "prompt": "Build a Developer Markdown Blog platform. Authors can publish articles and toggle is_premium paywalls. Readers upgrade to premium to access paywalled content.",
            "category": "Standard"
        },
        "case_04_ecommerce.json": {
            "name": "Subscription E-Commerce",
            "prompt": "Create a Subscription E-Commerce Store with product catalogs, shopping carts, checkout orders, and recurring subscriptions. Premium members get 20% discount on standard products.",
            "category": "Standard"
        },
        "case_05_fitness.json": {
            "name": "Gym Workout Tracker",
            "prompt": "Build a Gym Workout Tracker. Log workouts, sets, reps, and exercise target muscle categories. Premium users unlock custom routine builders.",
            "category": "Standard"
        },
        "case_06_aigen.json": {
            "name": "AI Content Assistant",
            "prompt": "Create an AI Writing Assistant platform. Track text prompt logs, document items, and credit usage balance. Basic users limited to 5 AI requests daily.",
            "category": "Standard"
        },
        "case_07_medical.json": {
            "name": "Doctor Scheduling System",
            "prompt": "Build a Doctor Scheduler booking system. Patients book appointments on doctor calendars. Protected medical_records readable by patients and doctors only.",
            "category": "Standard"
        },
        "case_08_realestate.json": {
            "name": "Real Estate Broker Platform",
            "prompt": "Create a Real Estate Listings platform. Agents upload properties, and visitors submit leads queries. Premium featured listings are pinned at the top.",
            "category": "Standard"
        },
        "case_09_events.json": {
            "name": "Event Ticket Portal",
            "prompt": "Build an Event Management and Ticket Ticketing platform. Assign seats, select ticket types, and manage attendee lists. VIP tickets gated.",
            "category": "Standard"
        },
        "case_10_cyclic_edge.json": {
            "name": "Cyclic Reference Edge Case",
            "prompt": "Create a cyclic schema validation test with Node_A referencing Node_B, and Node_B referencing Node_A.",
            "category": "Edge Case"
        },
        "case_11_orphaned_edge.json": {
            "name": "Orphaned UI API Edge Case",
            "prompt": "Build a simple app that has custom UI page categories but no matching API endpoint collections to verify UI-API alignment validation rules.",
            "category": "Edge Case"
        },
        "case_12_missing_pk_edge.json": {
            "name": "Missing Primary Key Edge Case",
            "prompt": "Generate a database model layout where the task table has no primary key field defined to test validator PK injector healing.",
            "category": "Edge Case"
        }
    }

    for filename, content in cases.items():
        filepath = os.path.join(test_cases_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)
            
    print(f"Successfully seeded {len(cases)} test cases.")

if __name__ == "__main__":
    seed_test_cases()
