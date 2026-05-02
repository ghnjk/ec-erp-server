# ERP 登录状态规约

### Requirement: Query backend ERP status
The system SHALL provide a backend ERP status capability that reports the currently configured seller platform, configured ERP email, configured warehouse ID, login status, auto-login behavior, and a human-readable status message.

#### Scenario: BigSeller status with automatic login
- **WHEN** the current application configuration has `use_up_seller=false`
- **THEN** the system SHALL check BigSeller login status using existing cookies and SHALL attempt automatic BigSeller login when cookies are missing or invalid.

#### Scenario: UpSeller status without automatic login
- **WHEN** the current application configuration has `use_up_seller=true`
- **THEN** the system SHALL check UpSeller login status by loading existing cookies and calling the login-check endpoint, and MUST NOT call the UpSeller automatic login flow.

#### Scenario: Status response exposes safe configuration only
- **WHEN** the status capability returns data
- **THEN** the response SHALL include platform type, ERP email, warehouse ID, login status, auto-login flag, and message, and MUST NOT include password, token, or cookie values.

#### Scenario: External ERP check failure
- **WHEN** checking the external ERP login status fails due to network, expired session, or service error
- **THEN** the system SHALL return a structured status result with `is_login=false` and an explanatory message instead of exposing sensitive exception details.

### Requirement: Warehouse ID precision safety
The system SHALL return backend ERP warehouse ID as a string to preserve long UpSeller numeric IDs across JSON clients.

#### Scenario: UpSeller warehouse ID is a long integer
- **WHEN** UpSeller is configured with a long numeric warehouse ID
- **THEN** the status response SHALL serialize the warehouse ID as a string value.
