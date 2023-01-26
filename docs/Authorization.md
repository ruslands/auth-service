[Up](../README.md)

# Authorization of requests
Part of the API is open to everyone, and part of the API requires authorization

Some requests require authorization. Request authorization is done using the library [am-auth].
In the `access-token` header of the HTTP request, the client passes access the user token received
after passing [authentication](Authentication.md).
Session data is retrieved from MongoDB (or from Redis).
From this data, it becomes clear on behalf of which user the request is being made.
It also becomes possible to check the availability of [permissions] (#requests-requiring-authorization) for
user to execute the request.

# requests-requiring-authorization

1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}` - `opportunities:read`;
1. PATCH `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}` - `opportunities:update`;
1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/related-opportunities` - no special permissions required;
1. POST `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/details` - no special permissions required;
1. POST `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/deal_projection` - no special permissions required;
1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/deal_projection` - no special permissions required;
1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/get_omg` - no special permissions required;
1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/comparables` - no special permissions required;
1. POST `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/comparables/<string:comparable>/<string:compare_type>/<string:comp_id>` - no special permissions required;
1. DELETE `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/opportunities/{{OPPORTUNITY_ID}}/comparables/<string:comparable>/<string:compare_type>/<string:comp_id>` - no special permissions required;
1. GET `api/opportunity/{{REGION}}/{{LEAD_TYPE}}/pd_seller_ids/merge` - no special permissions required;

1. `/api/user/block` - `user:write`, [user block](Blocking.md#block-user);
1. `/api/user/get` - `user:read`;
1. `/api/user/get-roles` - `user:read`;
1. `/api/user/list` - `user:read`;
1. `/api/user/create` - `user:write`;
1. `/api/user/unblock` - `user:write`, [user unblock](Blocking.md#unblock-user);
1. `/api/user/update` - `user:write`;
1. `/api/user/update-permissions` - `user:admin`;
