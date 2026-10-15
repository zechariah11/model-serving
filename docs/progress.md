# Progress

Claude updates this after each review. You don't need to edit it.

**Current step:** Phase 1, Step 2 — fixing review items
**Last reviewed commit:** `4d8940a`

## Open items

- [ ] `summarize()`: crashes when every successful request has fewer than 2 tokens,
      because the "nothing to take a percentile of" check looks at the error count,
      not at each list. Test: `test_time_per_token_is_nan_when_no_request_has_two_tokens`
- [ ] `summarize()`: a successful request with no text (`ttft_s=None`) breaks the
      sort. Test: `test_success_without_text_has_no_first_token`
- [ ] Journal, Step 2 (optional): add the positional-vs-aggregate point and the
      1-in-100 vs 2-in-100 case

## Strengths noticed

- Handles the last-index edge case in `percentile()` (p = 100) without going out of range
- Gives an example in the journal and gets the arithmetic right
- Turned off editor autocomplete to practice writing code unaided

## History

| Date | Step | Commit | Notes |
|---|---|---|---|
| 2026-10-15 | 2 | `4d8940a` | `percentile()` correct. `summarize()` passes the original tests; two edge cases added as new tests. Discussed why p99 misses one slow request in 100. |
