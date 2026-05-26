from typing import Any

class DatabaseCodeGenerator:
    """
    Relational Database DDL Script Generator.
    Converts a compiled DBSchema into a complete SQL schema script for databases like PostgreSQL.
    """

    def generate(self, schema: Any) -> str:
        sql_lines = []
        sql_lines.append(f"-- ========================================================")
        sql_lines.append(f"-- SQL DATABASE DDL SCRIPT FOR {schema.app_name.upper()}")
        sql_lines.append(f"-- Generated At: {schema.generated_at}")
        sql_lines.append(f"-- Version: {schema.version}")
        sql_lines.append(f"-- ========================================================\n")
        
        # 1. Generate Tables
        for table in schema.db_schema.tables:
            sql_lines.append(f"CREATE TABLE IF NOT EXISTS \"{table.name}\" (")
            fields_lines = []
            
            for field in table.fields:
                field_def = f"    \"{field.name}\" "
                
                # Type mapping
                if field.type == "integer":
                    field_def += "SERIAL" if field.primary else "INT"
                elif field.type == "float":
                    field_def += "DECIMAL(12, 2)"
                elif field.type == "boolean":
                    field_def += "BOOLEAN"
                else:
                    field_def += "VARCHAR(255)"

                # Constraints
                if field.primary:
                    field_def += " PRIMARY KEY"
                if field.unique and not field.primary:
                    field_def += " UNIQUE"
                if not field.primary:
                    # By default make foreign keys nullable for flexibility
                    field_def += " NULL" if field.foreign else " NOT NULL"

                fields_lines.append(field_def)
                
            # Append foreign keys separately
            for field in table.fields:
                if field.foreign:
                    target_tbl, target_fld = field.foreign.split(".")
                    fields_lines.append(f"    CONSTRAINT fk_{table.name}_{field.name} FOREIGN KEY (\"{field.name}\") REFERENCES \"{target_tbl}\" (\"{target_fld}\") ON DELETE CASCADE")

            sql_lines.append(",\n".join(fields_lines))
            sql_lines.append(");\n")

        # 2. Generate Indexes
        sql_lines.append("-- INDEX DEFINITIONS")
        for table in schema.db_schema.tables:
            for idx in table.indexes:
                sql_lines.append(f"CREATE INDEX IF NOT EXISTS idx_{table.name}_{idx} ON \"{table.name}\" (\"{idx}\");")
                
        sql_lines.append("\n-- END OF SCHEMA DDL SCRIPT")
        return "\n".join(sql_lines)
