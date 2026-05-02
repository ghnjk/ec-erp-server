## 1. Backend Status Helper

- [x] 1.1 Add a status helper in `ec_erp_api/common/seller_util.py` that returns `erp_type`, `email`, `warehouse_id`, `is_login`, `auto_login`, and `message`.
- [x] 1.2 Implement BigSeller status checking with automatic login by reusing existing BigSeller client construction and `login()` behavior.
- [x] 1.3 Implement UpSeller status checking without automatic login by constructing `UpSellerClient`, loading `up_seller.cookies`, and calling `is_login()` only.
- [x] 1.4 Ensure helper responses never include password, token, cookie, or other credential values.

## 2. System API

- [x] 2.1 Add `POST /erp_api/system/get_backend_erp_status` to `ec_erp_api/apis/system.py` with `@api_post_request()`.
- [x] 2.2 Require an authenticated ERP session by reusing the same not-login behavior as `_get_login_user_info()`.
- [x] 2.3 Return the seller status helper result via `response_util.pack_json_response()` or equivalent standard response wrapper.

## 3. Documentation and Specs

- [x] 3.1 Add `openspec/specs/apis/design/system/get_backend_erp_status.md` with route, request, response fields, examples, business logic, and Change-Log.
- [x] 3.2 Add `docs/erp_api/system/get_backend_erp_status.md` with business-facing API documentation.
- [x] 3.3 Update `openspec/specs/system_module_spec.md`, `openspec/specs/apis/spec.md`, and `openspec/specs/config.yaml` API indexes/counts.
- [x] 3.4 Update `docs/erp_api/README.md` system API list and total count.

## 4. Verification

- [x] 4.1 Run a BigSeller-path smoke test with `use_up_seller=false` and confirm the status helper can auto-login or report a structured failure.
- [x] 4.2 Run an UpSeller-path smoke test with `use_up_seller=true` and confirm no `UpSellerClient.login()`/selenium flow is triggered.
- [x] 4.3 Run Python import/syntax checks for `ec_erp_api/apis/system.py` and `ec_erp_api/common/seller_util.py`.
