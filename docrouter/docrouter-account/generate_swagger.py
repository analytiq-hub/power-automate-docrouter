#!/usr/bin/env python3
"""Emit apiDefinition.swagger.json (OpenAPI 2.0) for DocRouter Account connector."""
import json

ORG_MEMBER = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "user_id": {"type": "string"},
        "role": {"type": "string", "description": "admin or user"},
    },
}

DEFS = {
    "OrganizationMember": ORG_MEMBER,
    "Organization": {
        "type": "object",
        # Do not declare created_at/updated_at: API returns ISO-like strings without a timezone
        # suffix; Power Automate Test still expects "string date-time" vs "string undefined".
        # additionalProperties allows those fields without strict typed validation.
        "additionalProperties": True,
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "members": {"type": "array", "items": {"$ref": "#/definitions/OrganizationMember"}},
            "type": {"type": "string"},
            "default_prompt_enabled": {"type": "boolean"},
            "ocr_config": {"type": "object"},
            "ocr_catalog": {"type": "object"},
        },
    },
    "OrganizationCreate": {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string", "description": "individual, team, or enterprise"},
            "default_prompt_enabled": {"type": "boolean"},
            "ocr_config": {"type": "object"},
        },
    },
    "OrganizationUpdate": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "members": {"type": "array", "items": {"$ref": "#/definitions/OrganizationMember"}},
            "default_prompt_enabled": {"type": "boolean"},
            "ocr_config": {"type": "object"},
        },
    },
    "ListOrganizationsResponse": {
        "type": "object",
        "properties": {
            "organizations": {"type": "array", "items": {"$ref": "#/definitions/Organization"}},
            "total_count": {"type": "integer", "format": "int32"},
            "skip": {"type": "integer", "format": "int32"},
        },
    },
    "UserResponse": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "email": {"type": "string"},
            "name": {"type": "string"},
            "role": {"type": "string"},
            "email_verified": {"type": "boolean"},
            "created_at": {"type": "string"},
            "has_password": {"type": "boolean"},
            # API/DB may surface this as string in some cases; Power Automate Test expects string vs boolean match.
            "has_seen_tour": {"type": "string", "description": "Tour flag; may be boolean in API but serialized as string."},
        },
    },
    "UserCreate": {
        "type": "object",
        "required": ["email", "name", "password"],
        "properties": {
            "email": {"type": "string"},
            "name": {"type": "string"},
            "password": {"type": "string", "format": "password"},
        },
    },
    "UserUpdate": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "password": {"type": "string", "format": "password"},
            "role": {"type": "string"},
            "email_verified": {"type": "boolean"},
            "has_seen_tour": {"type": "boolean"},
        },
    },
    "ListUsersResponse": {
        "type": "object",
        "properties": {
            "users": {"type": "array", "items": {"$ref": "#/definitions/UserResponse"}},
            "total_count": {"type": "integer", "format": "int32"},
            "skip": {"type": "integer", "format": "int32"},
        },
    },
    "AccessToken": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "user_id": {"type": "string"},
            "organization_id": {"type": "string", "x-nullable": True},
            "name": {"type": "string"},
            "token": {"type": "string"},
            "created_at": {"type": "string"},
            "lifetime": {"type": "integer", "format": "int32"},
        },
    },
    "CreateAccessTokenRequest": {
        "type": "object",
        "required": ["name", "lifetime"],
        "properties": {
            "name": {"type": "string"},
            "lifetime": {"type": "integer", "format": "int32", "description": "Token lifetime in seconds"},
        },
    },
    "ListAccessTokensResponse": {
        "type": "object",
        "properties": {
            "access_tokens": {"type": "array", "items": {"$ref": "#/definitions/AccessToken"}},
        },
    },
    "AWSConfig": {
        "type": "object",
        "required": ["access_key_id", "secret_access_key", "s3_bucket_name"],
        "properties": {
            "access_key_id": {"type": "string"},
            "secret_access_key": {"type": "string", "format": "password"},
            "s3_bucket_name": {"type": "string"},
        },
    },
    "MessageResponse": {
        "type": "object",
        "properties": {"message": {"type": "string"}},
    },
    "StatusResponse": {
        "type": "object",
        "properties": {"status": {"type": "string"}},
    },
    "LLMChatModel": {
        "type": "object",
        "properties": {
            "litellm_model": {"type": "string"},
            "litellm_provider": {"type": "string"},
            "max_input_tokens": {"type": "integer"},
            "max_output_tokens": {"type": "integer"},
            "input_cost_per_token": {"type": "number", "format": "float"},
            "output_cost_per_token": {"type": "number", "format": "float"},
        },
    },
    "LLMEmbeddingModel": {
        "type": "object",
        "properties": {
            "litellm_model": {"type": "string"},
            "litellm_provider": {"type": "string"},
            "max_input_tokens": {"type": "integer"},
            "dimensions": {"type": "integer"},
            "input_cost_per_token": {"type": "number", "format": "float"},
            "input_cost_per_token_batches": {"type": "number", "format": "float"},
        },
    },
    "ListLLMModelsResponse": {
        "type": "object",
        "properties": {
            "chat_models": {"type": "array", "items": {"$ref": "#/definitions/LLMChatModel"}},
            "embedding_models": {"type": "array", "items": {"$ref": "#/definitions/LLMEmbeddingModel"}},
        },
    },
    "LLMProvider": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "display_name": {"type": "string"},
            "litellm_provider": {"type": "string"},
            "litellm_models_available": {"type": "array", "items": {"type": "string"}},
            "litellm_models_enabled": {"type": "array", "items": {"type": "string"}},
            "litellm_models_chat_agent": {"type": "array", "items": {"type": "string"}},
            "enabled": {"type": "boolean"},
            "token": {"type": "string"},
            "token_created_at": {"type": "string", "x-nullable": True},
        },
    },
    "ListLLMProvidersResponse": {
        "type": "object",
        "properties": {
            "providers": {"type": "array", "items": {"$ref": "#/definitions/LLMProvider"}},
        },
    },
    "SetLLMProviderConfigRequest": {
        "type": "object",
        "properties": {
            "litellm_models_enabled": {"type": "array", "items": {"type": "string"}},
            "litellm_models_chat_agent": {"type": "array", "items": {"type": "string"}},
            "enabled": {"type": "boolean"},
            "token": {"type": "string", "format": "password"},
        },
    },
    "TokenOrganizationResponse": {
        "type": "object",
        "properties": {
            "organization_id": {"type": "string", "x-nullable": True},
            "organization_name": {"type": "string", "x-nullable": True},
            "organization_type": {"type": "string", "x-nullable": True},
        },
    },
}


def json_body(ref_name: str):
    return {
        "name": "body",
        "in": "body",
        "required": True,
        "schema": {"$ref": f"#/definitions/{ref_name}"},
    }


def ok_json_schema(ref_name: str):
    return {
        "description": "Success",
        "schema": {"$ref": f"#/definitions/{ref_name}"},
    }


def path_param(name: str, desc: str):
    return {
        "name": name,
        "in": "path",
        "required": True,
        "type": "string",
        "x-ms-summary": name.replace("_", " ").title(),
        "description": desc,
        "x-ms-url-encoding": "single",
    }


def query_param(
    name: str,
    typ: str,
    desc: str,
    fmt=None,
    default=None,
    required=False,
    enum=None,
):
    p = {
        "name": name,
        "in": "query",
        "required": required,
        "type": typ,
        "x-ms-summary": name.replace("_", " ").title(),
        "description": desc,
    }
    if fmt:
        p["format"] = fmt
    if default is not None:
        p["default"] = default
    if enum:
        p["enum"] = enum
    return p


PATHS = {
    "/v0/account/organizations": {
        "get": {
            "operationId": "ListOrganizations",
            "summary": "List organizations",
            "description": "List organizations visible to the token, filter by user or single org id, or search by name/member. Requires appropriate permissions.",
            "x-ms-summary": "List organizations",
            "parameters": [
                query_param("user_id", "string", "Filter by user ID (admin or self)."),
                query_param("organization_id", "string", "Return a single organization by ID."),
                query_param("name_search", "string", "Case-insensitive name search."),
                query_param("member_search", "string", "Case-insensitive member name or email search."),
                query_param("skip", "integer", "Pagination offset.", "int32", 0),
                query_param("limit", "integer", "Page size (1–100).", "int32", 10),
            ],
            "responses": {"200": ok_json_schema("ListOrganizationsResponse")},
        },
        "post": {
            "operationId": "CreateOrganization",
            "summary": "Create organization",
            "description": "Create a new organization; the current user becomes an admin member.",
            "x-ms-summary": "Create organization",
            "parameters": [json_body("OrganizationCreate")],
            "responses": {"200": ok_json_schema("Organization")},
        },
    },
    "/v0/account/organizations/{organization_id}": {
        "put": {
            "operationId": "UpdateOrganization",
            "summary": "Update organization",
            "description": "Update organization name, members, type, OCR config, etc. Requires org admin or system admin.",
            "x-ms-summary": "Update organization",
            "parameters": [
                path_param("organization_id", "Organization ID."),
                json_body("OrganizationUpdate"),
            ],
            "responses": {"200": ok_json_schema("Organization")},
        },
        "delete": {
            "operationId": "DeleteOrganization",
            "summary": "Delete organization",
            "description": "Delete an organization. Requires org admin or system admin.",
            "x-ms-summary": "Delete organization",
            "parameters": [path_param("organization_id", "Organization ID.")],
            "responses": {"200": ok_json_schema("StatusResponse")},
        },
    },
    "/v0/account/users": {
        "get": {
            "operationId": "ListUsers",
            "summary": "List users",
            "description": "List users or filter by organization or single user id. Permissions apply per DocRouter rules.",
            "x-ms-summary": "List users",
            "parameters": [
                query_param("organization_id", "string", "Filter users belonging to this organization."),
                query_param("user_id", "string", "Return a single user by ID."),
                query_param("search_name", "string", "Search name or email (case-insensitive)."),
                query_param("skip", "integer", "Pagination offset.", "int32", 0),
                query_param("limit", "integer", "Page size.", "int32", 10),
            ],
            "responses": {"200": ok_json_schema("ListUsersResponse")},
        },
        "post": {
            "operationId": "CreateUser",
            "summary": "Create user",
            "description": "Create a user and default individual organization (system admin only).",
            "x-ms-summary": "Create user",
            "parameters": [json_body("UserCreate")],
            "responses": {"200": ok_json_schema("UserResponse")},
        },
    },
    "/v0/account/users/{user_id}": {
        "put": {
            "operationId": "UpdateUser",
            "summary": "Update user",
            "description": "Update user profile (self or admin).",
            "x-ms-summary": "Update user",
            "parameters": [
                path_param("user_id", "User ID."),
                json_body("UserUpdate"),
            ],
            "responses": {"200": ok_json_schema("UserResponse")},
        },
        "delete": {
            "operationId": "DeleteUser",
            "summary": "Delete user",
            "description": "Delete a user (self or admin).",
            "x-ms-summary": "Delete user",
            "parameters": [path_param("user_id", "User ID.")],
            "responses": {"200": ok_json_schema("MessageResponse")},
        },
    },
    "/v0/account/access_tokens": {
        "get": {
            "operationId": "ListAccountAccessTokens",
            "summary": "List account API tokens",
            "description": "List account-level API tokens for the current user (previews only).",
            "x-ms-summary": "List account API tokens",
            "parameters": [],
            "responses": {"200": ok_json_schema("ListAccessTokensResponse")},
        },
        "post": {
            "operationId": "CreateAccountAccessToken",
            "summary": "Create account API token",
            "description": "Create a new account-level API token (acc_...). Store the returned token securely; it is not shown again in full.",
            "x-ms-summary": "Create account API token",
            "parameters": [json_body("CreateAccessTokenRequest")],
            "responses": {"200": ok_json_schema("AccessToken")},
        },
    },
    "/v0/account/access_tokens/{token_id}": {
        "delete": {
            "operationId": "DeleteAccountAccessToken",
            "summary": "Delete account API token",
            "description": "Revoke an account-level API token by id.",
            "x-ms-summary": "Delete account API token",
            "parameters": [path_param("token_id", "Access token document id.")],
            "responses": {"200": ok_json_schema("MessageResponse")},
        },
    },
    "/v0/account/aws_config": {
        "get": {
            "operationId": "GetAwsConfig",
            "summary": "Get AWS configuration",
            "description": "Get stored AWS credentials and S3 bucket for the account (system admin only).",
            "x-ms-summary": "Get AWS configuration",
            "parameters": [],
            "responses": {"200": ok_json_schema("AWSConfig")},
        },
        "post": {
            "operationId": "SetAwsConfig",
            "summary": "Set AWS configuration",
            "description": "Create or update AWS access key and S3 bucket for the account (system admin only).",
            "x-ms-summary": "Set AWS configuration",
            "parameters": [json_body("AWSConfig")],
            "responses": {"200": ok_json_schema("MessageResponse")},
        },
        "delete": {
            "operationId": "DeleteAwsConfig",
            "summary": "Delete AWS configuration",
            "description": "Remove stored AWS configuration (system admin only).",
            "x-ms-summary": "Delete AWS configuration",
            "parameters": [],
            "responses": {"200": ok_json_schema("MessageResponse")},
        },
    },
    "/v0/account/llm/models": {
        "get": {
            "operationId": "ListAccountLlmModels",
            "summary": "List LLM models",
            "description": "List available chat and embedding models across providers.",
            "x-ms-summary": "List LLM models",
            "parameters": [
                query_param("provider_name", "string", "Filter by provider internal name."),
                {
                    "name": "provider_enabled",
                    "in": "query",
                    "required": False,
                    "type": "boolean",
                    "x-ms-summary": "Provider enabled",
                    "description": "If set, filter models to enabled (true) or disabled (false) providers.",
                },
                {
                    "name": "llm_enabled",
                    "in": "query",
                    "required": False,
                    "type": "boolean",
                    "default": True,
                    "x-ms-summary": "LLM enabled",
                    "description": "If true (default), return only enabled models; if false, return all available models.",
                },
            ],
            "responses": {"200": ok_json_schema("ListLLMModelsResponse")},
        },
    },
    "/v0/account/llm/providers": {
        "get": {
            "operationId": "ListAccountLlmProviders",
            "summary": "List LLM providers",
            "description": "List LLM provider definitions and masked tokens (system admin only).",
            "x-ms-summary": "List LLM providers",
            "parameters": [],
            "responses": {"200": ok_json_schema("ListLLMProvidersResponse")},
        },
    },
    "/v0/account/llm/provider/{provider_name}": {
        "put": {
            "operationId": "SetAccountLlmProviderConfig",
            "summary": "Set LLM provider configuration",
            "description": "Update enabled models, chat-agent models, enabled flag, or API token for a provider (system admin only).",
            "x-ms-summary": "Set LLM provider configuration",
            "parameters": [
                path_param("provider_name", "Provider key (matches provider name in DocRouter)."),
                json_body("SetLLMProviderConfigRequest"),
            ],
            "responses": {"200": ok_json_schema("MessageResponse")},
        },
    },
    "/v0/account/token/organization": {
        "get": {
            "operationId": "ResolveTokenOrganization",
            "summary": "Resolve token to organization",
            "description": "Given an API token string, return organization id/name/type or nulls for account-level tokens.",
            "x-ms-summary": "Resolve token to organization",
            "parameters": [
                {
                    "name": "token",
                    "in": "query",
                    "required": True,
                    "type": "string",
                    "x-ms-summary": "API token",
                    "description": "The org or account API token to inspect.",
                }
            ],
            "responses": {"200": ok_json_schema("TokenOrganizationResponse")},
        },
    },
}


def main():
    spec = {
        "swagger": "2.0",
        "info": {
            "title": "DocRouter Account",
            "description": (
                "DocRouter account-scoped APIs under /v0/account/: manage users, organizations, "
                "account-level API tokens, AWS integration, and LLM provider configuration. "
                "Authenticate with an account-level API token (prefix acc_, no organization binding) "
                "via X-Api-Key — create one in the DocRouter app under Settings → Developer. "
                "Organization-scoped tokens (org_...) cannot call these paths."
            ),
            "version": "1.0",
            "contact": {
                "name": "DocRouter Support",
                "url": "https://docrouter.ai",
                "email": "support@docrouter.ai",
            },
        },
        "host": "app.docrouter.ai",
        "basePath": "/fastapi",
        "schemes": ["https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "api_key": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}
        },
        "security": [{"api_key": []}],
        "x-ms-connector-metadata": [
            {"propertyName": "Website", "propertyValue": "https://docrouter.ai"},
            {"propertyName": "Privacy policy", "propertyValue": "https://docrouter.ai/privacy"},
            {"propertyName": "Categories", "propertyValue": "AI"},
        ],
        "definitions": DEFS,
        "paths": PATHS,
    }
    out = "/home/andrei/build/analytiq/power-automate-docrouter/docrouter/docrouter-account/apiDefinition.swagger.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
