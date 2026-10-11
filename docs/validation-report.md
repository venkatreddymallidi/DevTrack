# Validation record

Date: 2026-10-11

- Django version: **5.2.18**.
- `python scripts/verify_oop.py`: **7 tests passed**.
- `python manage.py test --verbosity 2`: **16 tests passed**.
- `python manage.py check`: **no issues**.
- Postman collection run using Newman against a live Django development server at `http://127.0.0.1:8765`: **9 requests and 13 assertions passed; zero failures**.
- Tested reporter create/list/lookup; issue create/list/lookup/status filtering; empty-title validation (400); missing issue (404).
- Source JSON data files reset to empty arrays after testing so first-run Postman requests work.

[`newman-results.json`](newman-results.json) contains a compact report extracted from the actual Newman execution, including request bodies, actual HTTP response status/body and assertion results.

## Remaining submission requirement

Authentic screenshots from the Postman UI have not been captured. Newman is Postman's command-line collection runner, but its report does not replace the assignment's UI screenshot requirement. See [`README.md`](README.md) for the two screenshots to add.
