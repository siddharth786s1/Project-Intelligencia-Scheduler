# Authentication System Documentation

## Overview

This document provides an overview of the authentication system implemented in the Project Intelligencia Scheduler application. The system is based on JWT (JSON Web Tokens) and provides comprehensive user authentication and authorization capabilities.

## Components

### 1. AuthContext

The `AuthContext` provides a centralized way to manage authentication state across the application. It handles:

- User authentication (login)
- User registration
- Session management
- Error handling
- Role-based access control
- Institution management

Located in: `frontend/src/contexts/AuthContext.tsx`

### 2. AuthService

The `AuthService` handles the communication with the authentication API endpoints. It provides methods for:

- Login/logout
- Registration
- Token management (storage, refresh)
- User information retrieval

Located in: `frontend/src/services/authService.ts`

### 3. API Client

The API client is configured with interceptors that automatically:

- Add authentication tokens to requests
- Handle token expiration
- Refresh tokens when needed
- Redirect to login on authentication failures

Located in: `frontend/src/services/apiClient.ts`

## Authentication Flow

1. **Login Process**:
   - User enters credentials in the Login component
   - Credentials are passed to the AuthContext's login method
   - AuthService sends credentials to the API
   - On success, tokens are stored in localStorage
   - User data is fetched and stored in AuthContext
   - UI updates to show authenticated state

2. **Session Persistence**:
   - On application load, AuthContext checks for valid tokens
   - If tokens exist, user data is fetched
   - UI shows authenticated state if tokens are valid

3. **Token Refresh**:
   - When an API call returns 401 Unauthorized
   - The API client attempts to use the refresh token
   - If successful, the original request is retried
   - If unsuccessful, user is logged out and redirected to login

4. **Logout Process**:
   - User triggers logout action
   - Tokens are removed from localStorage
   - AuthContext clears user data
   - User is redirected to login

## Authorization System

The authentication system includes role-based access control:

- `hasRole(role)` method in AuthContext to check user roles
- Protection for routes based on user roles
- UI elements that adapt based on user permissions

## Multi-Institution Support

The system supports users who may belong to multiple institutions:

- Current institution is tracked in AuthContext
- Institution can be changed at runtime
- Institution ID is persisted across sessions
- API requests are filtered by the current institution

## Error Handling

Authentication errors are handled at multiple levels:

- API-level errors are captured and formatted
- Context-level error state for UI consumption
- Component-level error handling and display

## Integration Points

### Protected Routes

The `ProtectedRoute` component ensures that only authenticated users can access certain routes. It uses the AuthContext to check authentication status.

### Login & Register Components

These components provide the user interface for authentication and use the AuthContext to perform authentication actions.

### Layout Components

The layout components use authentication status to determine which UI elements to display, such as navigation menus that adapt to the user's role.

## Security Considerations

- Tokens are stored in localStorage for persistence
- Sensitive operations require fresh authentication
- Token expiration is handled properly
- HTTPS is used for all API communications
- Error messages don't reveal sensitive information

## Testing Authentication

When testing the authentication system:

1. Verify login with valid credentials works
2. Verify login with invalid credentials fails with appropriate message
3. Verify session persistence works when refreshing the page
4. Verify token refresh works when the access token expires
5. Verify protected routes redirect to login when not authenticated
6. Verify role-based access control works for different user types
