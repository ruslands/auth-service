# # Native # #
import os
import re
import json

# # Installed # #
from pydantic import ValidationError

# # Package # #
from app import crud
from app.authoriser.util import rbac_validate, get_access_token
from app.authoriser.aws.schema import RequestVersion1 as AWSRequestV1, RequestVersion2 as AWSRequestV2
from app.authoriser.yc.schema import RequestVersion as YCRequest
from core.database.session import get_session
from core.logger import logger
from core.sentry import sentry_init
from core.security import verify_jwt_token

sentry_init()


AUTHORIZER_TYPE = os.environ.get("AUTHORIZER_TYPE", "YC")


def get_aws_payload(event: dict) -> AWSRequestV1 | AWSRequestV2:
    try:
        return AWSRequestV1.parse_obj(event)
    except ValidationError:
        return AWSRequestV2.parse_obj(event)


def get_yc_payload(event: dict) -> YCRequest:
    try:
        return YCRequest.parse_obj(event)
    except ValidationError:
        pass


async def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    """validate the incoming payload"""

    match AUTHORIZER_TYPE:
        case "AWS":
            payload = get_aws_payload(event)
        case "YC":
            payload = get_yc_payload(event)
        case _:
            raise Exception("Invalid AUTHORIZER_TYPE")

    if not payload:
        logger.error(f"Invalid payload: {event}")
        raise Exception("Invalid payload")

    logger.info(f"Payload: {payload}")

    """validate the incoming access token"""
    """and produce the principal user identifier associated with the token"""
    """this could be accomplished in a number of ways:"""
    """1. Call out to OAuth provider"""
    """2. Decode a JWT token inline"""
    """3. Lookup in a self-managed DB"""

    async for db_session in get_session():
        try:
            authorization_header = payload.headers.get("authorization") or payload.headers.get("Authorization")

            if not authorization_header:
                raise Exception("No Authorization header found")

            access_token = get_access_token(authorization_header)
            access_token_payload = await verify_jwt_token(
                token=access_token,
                token_type="access",
                db_session=db_session,
                crud=crud
            )

            principalId = access_token_payload.get("user_id")
            context = {
                "user_id": access_token_payload.get("user_id"),
                "email": access_token_payload.get("email"),
                "region": access_token_payload.get("region"),
                "teams": access_token_payload.get("teams"),
                "roles": json.dumps(access_token_payload.get("roles")),
                "visibility_group": access_token_payload.get("visibility_group"),
                "access_token": access_token,
            }
            is_authorized = True
        except Exception as e:
            logger.error(f"Token Validation Error: {str(e)}")
            is_authorized = False
            principalId = "none"

        """validate the user permissions"""
        if is_authorized:
            try:
                await rbac_validate(payload, communication="internal", db_session=db_session)
                logger.info("RBAC Validation Passed")
                is_authorized = True
            except Exception as e:
                logger.error(f"RBAC Validation Error: {str(e)}")
                is_authorized = False

        """policy must be generated which will allow or deny access to the client"""
        """keep in mind, the policy is cached for 5 minutes by default (TTL is configurable in the authorizer)"""

    if AUTHORIZER_TYPE == "AWS" and payload.version == "1.0":
        policy = AuthPolicy(principalId, payload.awsAccountId)
        policy.restApiId = payload.awsRestApiId
        policy.region = payload.awsRegion
        policy.stage = payload.awsStage

        if is_authorized:
            policy.allowAllMethods()
        else:
            policy.denyAllMethods()

        # Finally, build the policy
        response = policy.build()

        # if is_authorized:
        response["context"] = context
    else:
        response = {"isAuthorized": is_authorized}
        if is_authorized:
            response.update({"context": context})

    logger.info(f"Response: {response}")

    return response


class HttpVerb:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    ALL = "*"


class AuthPolicy(object):
    accountId = ""
    """The AWS account id the policy will be generated for. This is used to create the method ARNs."""
    principalId = ""
    """The principal used for the policy, this should be a unique identifier for the end user."""
    version = "2012-10-17"
    """The policy version used for the evaluation. This should always be '2012-10-17'"""
    pathRegex = "^[/.a-zA-Z0-9-\*]+$"  # noqa
    """The regular expression used to validate resource paths for the policy"""

    """these are the internal lists of allowed and denied methods. These are lists
    of objects and each object has 2 properties: A resource ARN and a nullable
    conditions statement.
    the build method processes these lists and generates the approriate
    statements for the final policy"""
    allowMethods = []
    denyMethods = []

    restApiId = "<<restApiId>>"
    """ Replace the placeholder value with a default API Gateway API id to be used in the policy.
    Beware of using '*' since it will not simply mean any API Gateway API id, because stars will greedily expand over '/' or other separators.
    See https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html for more details. """

    region = "<<region>>"
    """ Replace the placeholder value with a default region to be used in the policy.
    Beware of using '*' since it will not simply mean any region, because stars will greedily expand over '/' or other separators.
    See https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html for more details. """

    stage = "<<stage>>"
    """ Replace the placeholder value with a default stage to be used in the policy.
    Beware of using '*' since it will not simply mean any stage, because stars will greedily expand over '/' or other separators.
    See https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html for more details. """

    def __init__(self, principalId, accountId):
        self.accountId = accountId
        self.principalId = principalId
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):
        """Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null."""
        if verb != "*" and not hasattr(HttpVerb, verb):
            raise NameError(
                f"Invalid HTTP verb {verb}. Allowed verbs in HttpVerb class"
            )
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError(
                f"Invalid resource path: {resource}. Path should match {self.pathRegex}"
            )

        if resource[:1] == "/":
            resource = resource[1:]

        resourceArn = f"arn:aws:execute-api:{self.region}:{self.accountId}:{self.restApiId}/{self.stage}/{verb}/{resource}"  # noqa

        if effect.lower() == "allow":
            self.allowMethods.append(
                {"resourceArn": resourceArn, "conditions": conditions}
            )
        elif effect.lower() == "deny":
            self.denyMethods.append(
                {"resourceArn": resourceArn, "conditions": conditions}
            )

    def _getEmptyStatement(self, effect):
        """Returns an empty statement object prepopulated with the correct action and the
        desired effect."""
        statement = {
            "Action": "execute-api:Invoke",
            "Effect": effect[:1].upper() + effect[1:].lower(),
            "Resource": [],
        }

        return statement

    def _getStatementForEffect(self, effect, methods):
        """This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy."""
        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod["conditions"] is None or len(curMethod["conditions"]) == 0:
                    statement["Resource"].append(curMethod["resourceArn"])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement["Resource"].append(curMethod["resourceArn"])
                    conditionalStatement["Condition"] = curMethod["conditions"]
                    statements.append(conditionalStatement)

            statements.append(statement)

        return statements

    def allowAllMethods(self):
        """Adds a '*' allow to the policy to authorize access to all methods of an API"""
        self._addMethod("Allow", HttpVerb.ALL, "*", [])

    def denyAllMethods(self):
        """Adds a '*' allow to the policy to deny access to all methods of an API"""
        self._addMethod("Deny", HttpVerb.ALL, "*", [])

    def allowMethod(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy"""
        self._addMethod("Allow", verb, resource, [])

    def denyMethod(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy"""
        self._addMethod("Deny", verb, resource, [])

    def allowMethodWithConditions(self, verb, resource, conditions):
        """Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition"""
        self._addMethod("Allow", verb, resource, conditions)

    def denyMethodWithConditions(self, verb, resource, conditions):
        """Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition"""
        self._addMethod("Deny", verb, resource, conditions)

    def build(self):
        """Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy."""
        if (self.allowMethods is None or len(self.allowMethods) == 0) and (
            self.denyMethods is None or len(self.denyMethods) == 0
        ):  # noqa
            raise NameError("No statements defined for the policy")

        policy = {
            "principalId": self.principalId,
            "policyDocument": {"Version": self.version, "Statement": []},
        }

        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect("Allow", self.allowMethods)
        )
        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect("Deny", self.denyMethods)
        )

        return policy
