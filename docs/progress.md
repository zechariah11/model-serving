# Progress

Claude updates this after each review. You don't need to edit it.

**Current step:** Phase 1, Step 3 — look at the stream
**Last reviewed commit:** `9dc17cf`

## Open items

- [x] `summarize()`: crashes when every successful request has fewer than 2 tokens
- [x] `summarize()`: a successful request with no text (`ttft_s=None`) breaks the sort
- [x] Style (small): compare with `None` using `is not None`, not `!= None`
- [ ] Journal, Step 2 (optional): add the positional-vs-aggregate point and the
      1-in-100 vs 2-in-100 case

## Strengths noticed

- Handles the last-index edge case in `percentile()` (p = 100) without going out of range
- Gives an example in the journal and gets the arithmetic right
- Turned off editor autocomplete to practice writing code unaided
- Fixed both review bugs at the root cause (each list checked on its own) instead
  of patching each symptom separately

## History

| Date | Step | Commit | Notes |
|---|---|---|---|
| 2026-10-15 | 2 | `4d8940a` | `percentile()` correct. `summarize()` passes the original tests; two edge cases added as new tests. Discussed why p99 misses one slow request in 100. |
| 2026-10-15 | 2 | `d34b5c1` | Both edge cases fixed; all 18 stats tests pass. Step 2 done. |
| 2026-10-15 | 2 | `9dc17cf` | Switched to `is not None`; discussed `==` (asks the object) vs `is` (identity), and the string "None" trap for Step 4. |
