import json
import os
import random
from pathlib import Path


class Table:
    """
    Represents a single table.
    Supports: Columns, Primary Key Constraints, Indexing, and Auto-Generation.
    """
    def __init__(self, name, columns, primary_key=None):
        self.name = name
        self.columns = columns
        self.primary_key = primary_key
        self.rows = [] 
        self.primary_key_index = set() 

    def validate_and_insert(self, values):
        if len(values) != len(self.columns):
            raise ValueError(f"Schema mismatch: Expected {len(self.columns)} columns.")

        row = {}
        for (col_name, col_type), val in zip(self.columns.items(), values):
            
            # === AUTO-GENERATION LOGIC ===
            if val == "AUTO" and col_name == self.primary_key:
                unique_id = None
                for _ in range(50): 
                    candidate = random.randint(1000, 9999)
                    if candidate not in self.primary_key_index:
                        unique_id = candidate
                        break
                if unique_id is None:
                    raise ValueError("System Busy: Could not generate unique ID.")
                val = unique_id

            try:
                # === TYPE CONVERSION ===
                if col_type == "float":
                    row[col_name] = float(val)
                elif col_type == "int":
                    row[col_name] = int(float(val))
                else:
                    row[col_name] = str(val)
            except ValueError:
                raise ValueError(f"Type Error: Column '{col_name}' expects {col_type}.")

        if self.primary_key:
            pk_val = row[self.primary_key]
            if pk_val in self.primary_key_index:
                raise ValueError(f"Duplicate Key Error: {pk_val} already exists.")
            self.primary_key_index.add(pk_val)

        self.rows.append(row)
        return row 

    def delete(self, pk_value):
        if not self.primary_key: raise ValueError("Delete requires a Primary Key.")
        initial_len = len(self.rows)
        pk_type = self.columns[self.primary_key]
        if pk_type == "int": pk_value = int(float(pk_value))
        self.rows = [row for row in self.rows if row[self.primary_key] != pk_value]
        if len(self.rows) < initial_len:
            self.primary_key_index.remove(pk_value)
            return True
        return False

    def update(self, pk_value, col_name, new_value):
        if not self.primary_key: raise ValueError("Update requires a Primary Key.")
        pk_type = self.columns[self.primary_key]
        if pk_type == "int": pk_value = int(float(pk_value))
        for row in self.rows:
            if row[self.primary_key] == pk_value:
                target_type = self.columns.get(col_name)
                if not target_type: raise ValueError(f"Column {col_name} not found.")
                try:
                    if target_type == "float": row[col_name] = float(new_value)
                    elif target_type == "int": row[col_name] = int(float(new_value))
                    else: row[col_name] = str(new_value)
                    return True
                except ValueError: raise ValueError(f"Type Error: Cannot convert '{new_value}'")
        return False

class Database:
    def __init__(self, location=None):
        self.tables = {}
        
              
        base_dir = Path(__file__).resolve().parent.parent
        self.location = base_dir / "data" / "ganji_ledger.json"
        
        # Ensure the folder exists
        self.location.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert back to string for the open() function
        self.location = str(self.location)

    def create_table(self, name, columns, primary_key=None):
        if name in self.tables: return f"Error: Table {name} exists."
        self.tables[name] = Table(name, columns, primary_key)
        return f"Table '{name}' created."

    def join_tables(self, table1, table2, key1, key2):
        if table1 not in self.tables or table2 not in self.tables: return "Error: Tables not found."
        t1, t2 = self.tables[table1], self.tables[table2]
        results = []
        for r1 in t1.rows:
            for r2 in t2.rows:
                if str(r1.get(key1)) == str(r2.get(key2)): results.append({**r1, **r2})
        return results

    def execute_query(self, query):
        tokens = query.replace(",", " ").strip().split()
        if not tokens: return ""
        command = tokens[0].upper()

        try:
            if command == "CREATE":
                name = tokens[2]
                start, end = query.find("(")+1, query.find(")")
                cols = {p.split()[0]: p.split()[1] for p in query[start:end].split(",")}
                pk = tokens[tokens.index("PK")+1] if "PK" in tokens else None
                return self.create_table(name, cols, pk)
            elif command == "INSERT":
                name = tokens[2]
                start, end = query.find("(")+1, query.find(")")
                vals = [v.strip() for v in query[start:end].split(",")]
                row = self.tables[name].validate_and_insert(vals)
                return f"Inserted. ID: {row.get(self.tables[name].primary_key)}"
            elif command == "SELECT":
                if "JOIN" in tokens:
                    t1, t2 = tokens[3], tokens[5]
                    idx = tokens.index("ON")
                    return self.join_tables(t1, t2, tokens[idx+1], tokens[idx+3])
                else: return self.tables[tokens[3]].rows
            elif command == "UPDATE":
                if self.tables[tokens[1]].update(tokens[tokens.index("WHERE")+3], tokens[3], tokens[5]): return "Update Success."
                return "Update Failed."
            elif command == "DELETE":
                if self.tables[tokens[2]].delete(tokens[tokens.index("WHERE")+3]): return "Delete Success."
                return "Delete Failed."
            elif command == "SAVE":
                self.save_to_disk()
                return "Saved."
            else: return "Unknown Command."
        except Exception as e: return f"Error: {e}"

    def save_to_disk(self):
        dump = {n: {"columns": t.columns, "pk": t.primary_key, "rows": t.rows} for n, t in self.tables.items()}
        with open(self.location, "w") as f: json.dump(dump, f, indent=4)

    def load_from_disk(self):
        if not os.path.exists(self.location): return
        with open(self.location, "r") as f:
            try:
                data = json.load(f)
                for n, meta in data.items():
                    t = Table(n, meta["columns"], meta["pk"])
                    t.rows = meta["rows"]
                    if t.primary_key: t.primary_key_index = {r[t.primary_key] for r in t.rows}
                    self.tables[n] = t
            except: pass