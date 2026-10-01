## 1. Implementation
- [x] 1.1 Render the AUTODETECT block with the file's recorded date and skip the write when it matches
- [x] 1.2 Keep the file's newline style on write; copy the template byte-for-byte when seeding
- [x] 1.3 Tests: unchanged (no write), changed (new date), absent (write), two runs byte-identical, CRLF preserved
- [x] 1.4 Update docs that describe adapt.py as rewriting the block on every run
