from engine import Database
import sys

def start_repl():
    print("==========================================")
    print("      GANJI MERCHANT DB - CLI MODE        ")
    print("      v1.0.0 | Pesapal Challenge '26     ")
    print("==========================================")
    
    # Initialize Database
    # We don't need to load here, because we load inside the loop now.
    db = Database()
    
    print("System loaded. Type 'EXIT' to quit.")

    while True:
        try:
            user_input = input("GanjiDB> ").strip()
            if not user_input: continue

            command = user_input.upper().split()[0]

            if command == "EXIT":
                print("Exiting...")
                break
            
            # === NO CACHE LOGIC ===
            # We force a reload from disk BEFORE executing the command.
            # This ensures we always see the latest data from the Web App.
            db.load_from_disk()

            # Execute the query
            result = db.execute_query(user_input)
            
            # === AUTO-SAVE LOGIC ===
            # If we modified data, we save it back to disk immediately.
            if command in ["CREATE", "INSERT", "UPDATE", "DELETE"]:
                if "Error" not in str(result): 
                    db.save_to_disk()
                    if isinstance(result, str):
                        result += " (Saved to disk)"

            # Formatting Results
            if isinstance(result, list):
                if not result:
                    print("No records found.")
                else:
                    print(f"\nFound {len(result)} records:")
                    print("-" * 40)
                    if result:
                        headers = list(result[0].keys())
                        print(" | ".join(headers).upper())
                        print("-" * 40)
                        for row in result:
                            vals = [str(val) for val in row.values()]
                            print(" | ".join(vals))
                    print("-" * 40 + "\n")
            else:
                print(f"-> {result}")

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        except Exception as e:
            print(f"REPL Error: {e}")

if __name__ == "__main__":
    start_repl()