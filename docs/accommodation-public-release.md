# Public apartment catalogue contract

The source of truth is the existing nextgenz-accommodation-portal project. Do not duplicate its inventory. The staged HTML and JS use the original partner-review interface and require two read-only unauthenticated endpoints:

- GET /api/accommodation?part=public — approved collection title, city, variant ID, beds, bathrooms, guests, approved features, apartment public code and approved image count. Use the same sanitized review projection, filtered to approved publication records. Do not return supplier URLs, private rates, access tokens, owner identity, lookup records or internal data.
- GET /api/accommodation?part=public-photo&code=PUBLIC_CODE&index=INTEGER — return only approved image bytes for approved public units. Validate exact code/index against published records; return 404 for unpublished/missing units. Keep owner, lookup, directory, private gallery and partner invitation routes authenticated.

Release gate: verify public listing and photos without any cookies; reject invalid unit codes; confirm protected routes remain 403; test complete count against existing approved catalogue; render map and dates form; generate individual canonical crawlable apartment pages from this same projection (not duplicated inventory). Do not promote the staged page until endpoint verification succeeds.
