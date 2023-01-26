[Up](../README.md)

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