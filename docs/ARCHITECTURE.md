# Architecture Overview — CO-ATTAIN PRO AI

## System Topology

```
+--------------------------------------------------------------+
|                     Modern Web Browser                       |
|        React 19 + Vite + TypeScript + Tailwind CSS v4        |
|  (Dynamic Charts, Responsive Modals, Interactive Matrices)   |
+------------------------------+-------------------------------+
                               | JSON API & File Streams
                               v
+--------------------------------------------------------------+
|                    FastAPI Backend (Py 3.13)                 |
|  - JWT Authentication & Argon2 Password Hashing             |
|  - Role-Based Access Control (RBAC Dependencies)             |
|  - Pydantic Validation & Structured Errors                  |
|  - Pure Calculation Engine (Decimal Precision)               |
|  - Gap Detection & Bloom Cognitive Taxonomy Engine           |
|  - ReportLab PDF & openpyxl Excel Generation Services        |
+------------------------------+-------------------------------+
                               | SQLAlchemy 2.x ORM
                               v
+--------------------------------------------------------------+
|                   Database Storage Engine                    |
|    - SQLite (Local Development with Foreign Keys Enabled)    |
|    - PostgreSQL (Production / Docker Deployment Ready)      |
+--------------------------------------------------------------+
```

## Security & Access Boundaries

1. **Password Security**: Argon2id cryptographic hashing with memory-hard parameters.
2. **Authorization**: Strict backend dependency checking (`require_roles`). Frontend UI buttons reflect permissions, but backend enforces them.
3. **Department Boundaries**: HOD users are constrained to their respective department's courses, faculty, and students.
4. **Student Privacy**: Student role is restricted strictly to read-only authorized individual academic evaluations.
5. **Spreadsheet Security**: Formula injection protection, strict data type parsing, and row-level rejection of invalid marks.
