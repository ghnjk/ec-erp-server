## ADDED Requirements

### Requirement: System API exposes backend ERP status
The API layer SHALL expose a POST endpoint under the system module for querying backend ERP status, following the standard `/erp_api/system/*` route convention and `@api_post_request()` response wrapping.

#### Scenario: Authenticated user queries ERP status
- **WHEN** an authenticated user calls `POST /erp_api/system/get_backend_erp_status`
- **THEN** the API SHALL return `result=0` with the backend ERP status data.

#### Scenario: Unauthenticated user queries ERP status
- **WHEN** a request without a valid Flask session calls `POST /erp_api/system/get_backend_erp_status`
- **THEN** the API SHALL return the same not-login error behavior used by existing system user-info APIs.

#### Scenario: API response shape
- **WHEN** the endpoint succeeds
- **THEN** the response `data` SHALL contain `erp_type`, `email`, `warehouse_id`, `is_login`, `auto_login`, and `message` fields.

#### Scenario: Documentation is synchronized
- **WHEN** the API is implemented
- **THEN** `openspec/specs/apis/design/system/get_backend_erp_status.md`, `docs/erp_api/system/get_backend_erp_status.md`, and API indexes SHALL be updated to document the route, request, response fields, examples, and business logic.
