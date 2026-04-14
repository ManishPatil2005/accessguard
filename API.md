# API.md - AccessGuard REST API Documentation

## HTTP Endpoints

### Public Endpoints

#### GET /
**Description**: Home page  
**Response**: HTML (home.html)  
**Status Code**: 200 OK

#### GET /register
**Description**: Registration form page  
**Response**: HTML (register.html)  
**Status Code**: 200 OK

#### POST /register
**Description**: Register new user  
**Request**:
```form
email=user@example.com
password=SecurePassword123
role=user  # or "admin"
```
**Status Codes**:
- 201 Created (Success)
- 400 Bad Request (Validation error)
- 409 Conflict (Email exists)

**Response**: HTML with success/error message

#### GET /login
**Description**: Login form page  
**Response**: HTML (login.html)  
**Status Code**: 200 OK

#### POST /login
**Description**: Authenticate user  
**Request**:
```form
email=user@example.com
password=SecurePassword123
```
**Status Codes**:
- 303 See Other (Redirect to /welcome or /dashboard)
- 401 Unauthorized (Invalid credentials)
- 423 Locked (Account locked)

**Response**: Redirect or HTML with error message

#### GET /logout
**Description**: Clear session  
**Status Code**: 303 See Other  
**Response**: Redirect to /login

### Protected Endpoints (Authentication Required)

#### GET /welcome
**Description**: User landing page  
**Required**: Valid session with role=user  
**Status Code**: 200 OK  
**Response**: HTML (welcome.html)

#### GET /dashboard
**Description**: Admin security dashboard  
**Required**: Valid session with role=admin  
**Status Code**: 200 OK  
**Response**: HTML (dashboard.html)  
**Content**:
- Locked accounts list
- Login audit log

#### POST /unlock/{email}
**Description**: Unlock user account (admin only)  
**Required**: Valid session with role=admin  
**Parameters**:
- email: User email to unlock

**Status Codes**:
- 303 See Other (Redirect to /dashboard)
- 401 Unauthorized (Not logged in)
- 403 Forbidden (Not admin)
- 404 Not Found (Email doesn't exist)

**Response**: Redirect with success message

### System Endpoints

#### GET /docs
**Description**: Swagger API documentation  
**Status Code**: 200 OK  
**Response**: Interactive API documentation

---

## Error Codes Reference

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 303 | See Other | Follow redirect |
| 400 | Bad Request | Check input validation |
| 401 | Unauthorized | Login required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Email already exists |
| 423 | Locked | Account locked (3 strikes) |
| 500 | Server Error | Contact support |

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
