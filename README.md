# Ganji Merchant DB
## Pesapal Junior Dev Challenge '26 Submission

Ganji Merchant DB is a lightweight, localized Relational Database Management System (RDBMS) built entirely from scratch in Python. It is designed to simulate a transaction ledger for Small and Medium Enterprises (SMEs) in Kenya, demonstrating core database engineering concepts without relying on external SQL libraries.

### Features

1.  **Custom Storage Engine**
    - Implements a row-oriented storage model using Python dictionaries.
    - Persists data to disk using JSON serialization (`data/ganji_ledger.json`).

2.  **Indexing & Optimization**
    - Uses Hash Indexing (Python Sets) for Primary Key constraints.
    - Achieves O(1) time complexity for duplicate checks, ensuring data integrity for financial transactions.

3.  **Full CRUD & Relational Support**
    - Supports Create (INSERT), Read (SELECT), Update, and Delete operations.
    - Implements Inner Joins to combine data across tables (e.g., joining Users and Orders).

4.  **SQL-Like Query Parser**
    - A custom string tokenizer that parses raw text commands into executable Python logic.
    - Enforces strict type checking (Integers vs Strings).

5.  **Dual Interfaces**
    - **CLI REPL**: An interactive command-line tool for Database Administrators.
    - **Web Portal**: A Flask-based dashboard for Merchants to record sales.

---

### Project Structure
```
Ganji_Merchant_DB/
├── src/
│   ├── engine.py           # Core database logic (Storage, Parsing, Indexing)
│   ├── repl.py             # Interactive Command Line Interface
│   └── app.py              # Web Application (Flask)
├── data/
│   └── ganji_ledger.json   # Persistent storage file (Auto-generated)
├── requirements.txt        # Project dependencies
└── README.md               # Documentation
```
---

### Installation

1.  **Clone the project**
    Navigate to the project directory:
    ```bash
    cd Ganji_Merchant_DB
    ```

2.  **Set up a Virtual Environment** (Recommended)
    It is best practice to run Python projects in an isolated environment.

    *Windows:*
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    *Mac/Linux:*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    The core engine is built with standard Python libraries. Flask is required only for the Web Interface.
    ```bash
    pip install -r requirements.txt
    ```

---

### Usage

#### 1. The Web Interface (Merchant View)
To launch the Merchant Portal:
    ```bash
    python src/app.py
    ```

Open your web browser to: http://127.0.0.1:5000

Click "Reset & Initialize Database System" to create the necessary tables.

Use the form to record transactions and view the ledger.

#### 2. The CLI REPL (Admin View)
To interact directly with the database engine using SQL commands:

    ```bash
    python src/repl.py
    ```
Type EXIT to close the session.

Supported SQL Syntax
The custom parser supports the following commands:

1. **Create Table Defines a new table with typed columns and an optional Primary Key (PK).**

    ```SQL

    CREATE TABLE users (id int, name str, role str) PK id
    ```
2. **Insert Data Adds a new row. The parser validates data types against the schema.**

    ```SQL

    INSERT INTO users VALUES (101, Alice, Admin)
    ```
3. **Select Data Retrieves all rows from a table.**

    ```SQL

    SELECT * FROM users
    ```
4. **Update Data Updates a specific column for a row identified by the Primary Key.**

    ```SQL

    UPDATE users SET role = Manager WHERE id = 101
    ```
5. **Delete Data Removes a row identified by the Primary Key.**

    ```SQL

    DELETE FROM users WHERE id = 101
    ```
6. **Join Tables Performs an Inner Join between two tables based on a common key.**

    ```SQL

    SELECT * FROM users JOIN orders ON id = user_id
    ```

7. **System Commands**

    **SAVE:** Forces a write operation to the JSON file on disk.

    **EXIT:** Closes the REPL.

#### Architecture Design Decisions
### Storage (JSON)

**Decision:** Used JSON for serialization instead of binary files.

**Reasoning:** JSON is human-readable, making it easier to debug and verify data persistence during development.

### Indexing (Python Sets)

**Decision:** Used Python's internal Set data structure for Primary Keys.

**Reasoning:** Sets provide O(1) average time complexity for lookups. This allows the system to instantly reject duplicate IDs without scanning the entire table.

### Joins (Nested Loop)

**Decision:** Implemented a Nested Loop Join algorithm.

**Reasoning:** While O(N*M) in complexity, it is the most straightforward implementation of Relational Algebra for a custom engine, demonstrating the fundamental logic of data combination.

### Credits
**Author:** Ray Basweti w/ Gemini

**Frameworks:** Flask (Used for the Web Interface layer only).

**Inspiration:** Pesapal's mission to provide seamless payment solutions for businesses.
