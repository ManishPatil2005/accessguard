# GLOSSARY.md - Terminology & Definitions

## Authentication & Authorization

**Authentication**: Verifying who you are (login credentials)  
**Authorization**: Verifying what you can do (permissions)  
**Credential**: Email/password pair used for login  
**Session**: Active user connection, maintained with cookies  
**Role**: Permission level (admin, user)  
**Token**: String representing user identity (not used here)  
**MFA**: Multi-factor authentication (future)  

## Security Concepts

**Brute-Force Attack**: Trying all password combinations until one works  
**Lock Out**: Preventing further login attempts after multiple failures  
**Hash**: One-way function converting password to fixed-size string  
**Plaintext**: Data in readable form (opposite of encrypted)  
**Salt**: Random data mixed with password before hashing  
**Parameterized Query**: SQL with data separated from structure  
**SQL Injection**: Inserting malicious SQL as user input  
**RBAC**: Role-Based Access Control (admin/user roles)  
**OWASP**: Open Web Application Security Project (standards)  
**CVE**: Common Vulnerabilities and Exposures (vulnerability database)  

## Database Terms

**Primary Key**: Unique identifier for a row (email in Users table)  
**Foreign Key**: Link to another table's primary key  
**Index**: Data structure for fast lookups  
**Transaction**: Group of SQL operations (all-or-nothing)  
**Schema**: Structure of tables and columns  
**Denormalization**: Storing redundant data for performance  
**Audit Log**: Record of all changes (login_attempts table)  

## API Terms

**Endpoint**: URL that handles a specific request  
**HTTP Method**: GET (retrieve), POST (create), PUT (update), DELETE  
**Status Code**: Response number (200=OK, 401=unauthorized, 403=forbidden)  
**Request**: Message from client to server  
**Response**: Message from server to client  
**Header**: Metadata in request/response  
**Body**: Data in request/response  

## DevOps & Deployment

**Environment Variable**: Configuration setting (SECRET_KEY, DATABASE_URL)  
**Virtualenv**: Isolated Python environment per project  
**Docker**: Container system for packaging application  
**Nginx**: Reverse proxy (forwards requests to application)  
**SSL/TLS**: Encryption for web traffic (HTTPS)  
**Backup**: Copy of data for disaster recovery  
**Monitoring**: Watching system for errors/performance  
**Logging**: Recording events for analysis  

## FastAPI & Jinja2

**Endpoint Handler**: Function responding to HTTP request  
**Middleware**: Code running before/after each request  
**Template**: HTML file with placeholders ({{ variable }})  
**Context**: Dictionary of data passed to template  
**Variable Interpolation**: {{ variable }} in templates  
**Control Flow**: {% if %}, {% for %} in templates  

## Testing

**Test Case**: Specific scenario to validate  
**Pass**: Test succeeds (expected behavior)  
**Fail**: Test fails (unexpected behavior)  
**Edge Case**: Unusual input that might break code  
**Integration Test**: Testing multiple components together  
**Unit Test**: Testing single component in isolation  

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
