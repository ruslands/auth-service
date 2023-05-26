[Up](../README.md)

# User registration

## Client registration

Not implemnented

## User registration

User registration occurs when calling the `/api/auth/user/create` method, calling the method
requires [rights](Authorization.md#requests-requiring-authorization) to write
to the appropriate section.

When registering, be sure to specify the role of the user - this determines his default set of rights,
the list of available roles is specified in the documentation in postman
