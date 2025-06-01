# Authentication

Authentication is the process of verifying user credentials (login/password) and issuing authorization tokens (access and refresh tokens). These tokens allow a user to interact with the system securely:

1. **Access Token**: 
   - This is a short-lived token, usually with an expiration time (e.g., 15 minutes or 1 hour).
   - It is sent in the HTTP header (`Authorization: Bearer <access_token>`) with every API request to authorize the user.
   - The access token ensures that the user can access certain endpoints without needing to send login credentials (username and password) repeatedly.

2. **Refresh Token**: 
   - This is a longer-lived token, usually with an expiration time in days or weeks (e.g., 7 or 30 days).
   - Its sole purpose is to obtain a new access token when the current one expires, without requiring the user to re-login.
   - When the access token expires, the refresh token is sent to a specific endpoint to request a fresh pair of tokens (new access and refresh tokens).

The flow of the authentication process involves:

### Step 1: Basic Authentication (Login)
The user provides their username and password to authenticate. This is done by making a POST request to the basic authentication endpoint. If successful, the system issues an access token and a refresh token.

**Example:**
Endpoint for basic authentication:  
[POST /auth/basic](https://staging.seller-1.ru/docs#/auth/basic_api_v1_auth_basic_post)

Request:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "your_access_token",
  "refresh_token": "your_refresh_token"
}
```

### Step 2: Token Refresh
When the access token expires, the user does not need to log in again. Instead, they use the refresh token to obtain a new access token and refresh token by making a POST request to the refresh-token endpoint.

**Example:**
Endpoint for refreshing tokens:  
[POST /auth/refresh-token](https://staging.seller-1.ru/docs#/auth/refresh_token_api_v1_auth_refresh_token_post)

Request:
```json
{
  "refresh_token": "your_refresh_token"
}
```

Response:
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token"
}
```


# Authorization


Authorization is the process of verifying a user's permissions to access specific resources or perform actions within a system. It ensures that the user has the necessary rights to perform the requested operation. This step happens **after** authentication.

### Key Elements:
1. **Access Token**:
   - The access token, which is provided during the authentication process, is used to authorize each API request.
   - The token is sent in the HTTP request headers for every request to protected resources.
   - Example of the HTTP header:
     ```
     Authorization: Bearer <access_token>
     ```

2. **Permission Validation**:
   - When an API request is received, the system extracts the access token from the request headers.
   - The token contains information about the user, such as their identity and roles/permissions.
   - The system validates the token and checks if the user has the appropriate permissions for the requested resource or action.
   - This check ensures that users only access data or execute operations they are authorized for, based on their role or permission set.

### Authorization Flow:

1. **Access Token in Header**:
   - The user sends an API request with their access token in the headers.
   
   **Example API Request:**
   ```http
   GET /api/resource
   Host: api.example.com
   Authorization: Bearer <access_token>
   ```

2. **System Extracts and Validates Token**:
   - Upon receiving the request, the system retrieves the access token from the `Authorization` header.
   - The token is validated to ensure it is not expired, has the correct format, and has not been tampered with.

3. **User Role and Permissions Check**:
   - Once the token is validated, the system checks the user's role and associated permissions.
   - Based on the user’s role (e.g., admin, editor, viewer), the system determines whether they have the required permissions to perform the requested action.
   - If the user is authorized, the system allows the request to proceed and responds with the requested data or action result.
   - If the user is **not** authorized, the system returns an appropriate error response (e.g., `403 Forbidden`).

   **Example Authorization Check:**
   - User role: `viewer`
   - Requested operation: `POST /api/resource`
   - If the user role (`viewer`) does not have permission to create new resources (`POST`), the request will be denied.

### Example Scenario:

1. A user with an access token tries to delete a resource:
   ```http
   DELETE /api/resource/123
   Host: api.example.com
   Authorization: Bearer <access_token>
   ```

2. The system retrieves the access token, validates it, and checks the user's permissions.
   - If the user does **not** have permission to delete resources (e.g., they are only allowed to view or edit resources), the system returns a `403 Forbidden` response:
     ```json
     {
       "error": "You do not have permission to delete this resource."
     }
     ```
   - If the user does have the necessary permissions, the system proceeds with deleting the resource.

### Key Points to Remember:
- **Authentication** verifies who the user is (using credentials and tokens).
- **Authorization** checks what the user is allowed to do (based on roles and permissions).
- The access token carries the user's identity and permissions and is validated with every request.
- Unauthorized actions are blocked to ensure security and data protection.

This ensures that users can only perform actions they are authorized to, and the system enforces security by verifying permissions for each API request.


# RBAC
Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles assigned to users within an organization. In RBAC, permissions are assigned to specific roles, and users are granted roles, thereby acquiring the permissions associated with those roles. This approach simplifies management of user permissions and enhances security by ensuring that users can only perform actions that are appropriate for their role.


# Session

The user session appears after passing authentication. Session data is stored in Redis. 

Session data:

* `expires` - session expiration time;
* `refresh_token` - refresh token, used for [session refresh](#session-refresh);
* `access_token` - access token, used for [request authorization](Authorization.md) user;
* `user` - user data, the data set is determined by the `getForSession` method
* `blocked` - flag, blocking the user;
* `email` - email address, if known;
* `id` - user identifier;
* `name` - username, if known;
* `phone` - the user's phone number.


### Session update

Some time before the expiration (possibly after) the action of the tokens, they need to be updated.
The update is done using the `/api/session/refresh` method,
The method requires two parameters to be passed:

* `refresh_token_hash` - hmac from refresh token for session refresh;
* `id` - session id (see [session data](#user-session)).

Since passing `refresh_token` directly is not secure, hmac is passed instead of a token
obtained by the sha256 algorithm, `user_id` is used as a key.

If the session update is successful, [session data](#user-session) will be returned to the client
with refreshed `refresh_token`/`access_token` tokens.


### Logout

Two options for logout
1. Delete current session
2. Delete all sessions

During deleting need to delete session from identity-provider

# Visibility group

Restricting access to data within one resource, users may have the same role granting access to the API, but different visibility groups returning different data.

# Create

1. Add a new column to the Visibility Group Table.
2. Populate the column with settings as values.
3. Update the schema.



# Users

## User types

The service supports the following types of users:

1. Client - is someone who login to the system via login form on the landing page.
    Client data is stored in DB (see [model](ClientModel.md));
1. User - participiant which can be created via google workspace.
    User data is stored in DB (see [model](UserModel.md));


# Blocking

Blocking the user allows you to block the user's ability to [authentication](Authentication.md)
and revoke the user's session immediately. It is worth distinguishing between blocking a user and
[blocking authorization code entry](Authentication.md#blocking-entering-authorization-code).

## Block user

The following methods are used to block users:

1. `/api/client/block`;
2. `/api/user/block`.

These actions require [special rights](Authorization.md#requests-requiring-authorization)

## Unblock user

To unlock users, the following methods are used:

1. `/api/client/unblock`;
2. `/api/user/unblock`.

These actions require [special rights](Authorization.md#requests-requiring-authorization)


