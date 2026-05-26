from typing import Any

class MermaidERDGenerator:
    """
    Utility to translate db_schema tables and foreign relations
    into standard Mermaid.js Entity-Relationship diagram syntax.
    """

    def generate(self, schema: Any) -> str:
        lines = ["erDiagram"]

        # 1. Define entities and fields
        for table in schema.db_schema.tables:
            lines.append(f"  {table.name} {{")
            for field in table.fields:
                f_type = field.type
                f_name = field.name
                
                # Append indicators
                indicators = ""
                if field.primary:
                    indicators = " PK"
                elif field.foreign:
                    indicators = " FK"
                    
                lines.append(f"    {f_type} {f_name}{indicators}")
            lines.append("  }")

        # 2. Define relationships
        # Standard: table_a ||--o{ table_b : "foreign_key"
        relations = schema.db_schema.relations
        for rel_name, rel in relations.items():
            from_t = rel.get("from_table")
            from_f = rel.get("from_field")
            to_t = rel.get("to_table")
            
            # Draw many-to-one arrow link
            lines.append(f"  {to_t} ||--o{{ {from_t} : \"{from_f}\"")

        # Catch dynamic loops for cyclic tests if relations list is empty
        if not relations:
            # Check fields manually
            for table in schema.db_schema.tables:
                for field in table.fields:
                    if field.foreign:
                        target_t = field.foreign.split(".")[0]
                        lines.append(f"  {target_t} ||--o{{ {table.name} : \"{field.name}\"")

        return "\n".join(lines)
