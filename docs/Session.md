[Up](../README.md)

# Session

## User session

The user session appears after passing authentication. Session data is stored in MongoDB and in Redis. 

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

**IMPORTANT** `access_token`, `refresh_token`, `expires` the user receives only when
[authentication](Authentication.md) or [session update](#session-update),
the data of the `session` field can be obtained by the user at any time.

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