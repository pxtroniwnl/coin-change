
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** coin-change
- **Date:** 2026-05-24
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

### Requirement: Solve Coin Change via HTML Form
- **Description:** Users submit coin denominations and target amount via the HTML form, select one or more algorithms, and view results including coins used, count, optimality, and execution time.

#### Test TC001 Solve coin change with all algorithms
- **Test Code:** [TC001_Solve_coin_change_with_all_algorithms.py](./TC001_Solve_coin_change_with_all_algorithms.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/38db1f12-bcdd-4b53-859f-3cd065610d32
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** All three algorithms (greedy, DP, backtracking) returned correct results for a standard input. Results page rendered with coins used, count, and timing for each algorithm.

---

#### Test TC002 Solve coins with all algorithms on the HTML results page
- **Test Code:** [TC002_Solve_coins_with_all_algorithms_on_the_HTML_results_page.py](./TC002_Solve_coins_with_all_algorithms_on_the_HTML_results_page.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/3fd4c0c6-fbbe-4c58-8339-fa4822c01e67
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** HTML results page correctly displays per-algorithm result sections with all expected fields. UI rendering is consistent across all three algorithm outputs.

---

#### Test TC003 Solve coin change with greedy only and compare against optimal
- **Test Code:** [TC003_Solve_coin_change_with_greedy_only_and_compare_against_optimal.py](./TC003_Solve_coin_change_with_greedy_only_and_compare_against_optimal.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/260c680d-ba20-417c-8b60-1f1a8701e726
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** When only greedy is selected, the app silently runs DP for comparison and correctly flags whether greedy was optimal. The optimality badge reflects the silent DP check result.

---

#### Test TC004 Solve coins with greedy only and verify optimality is shown
- **Test Code:** [TC004_Solve_coins_with_greedy_only_and_verify_optimality_is_shown.py](./TC004_Solve_coins_with_greedy_only_and_verify_optimality_is_shown.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/50a4cd14-e9c8-4229-98ac-6f444ac4574a
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Optimality indicator is displayed correctly on the results page for the greedy-only scenario, accurately reflecting whether the greedy solution matched the DP optimum.

---

#### Test TC005 Reject solve request without an algorithm selection
- **Test Code:** [TC005_Reject_solve_request_without_an_algorithm_selection.py](./TC005_Reject_solve_request_without_an_algorithm_selection.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/0f87fc41-7f1f-418c-af8a-2643d2390d98
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Submitting the form without selecting any algorithm correctly returns an error message prompting the user to select at least one algorithm. No crash or unhandled exception occurred.

---

#### Test TC006 Reject invalid coin input on the HTML form
- **Test Code:** [TC006_Reject_invalid_coin_input_on_the_HTML_form.py](./TC006_Reject_invalid_coin_input_on_the_HTML_form.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/78316b46-fd30-4c2b-8fd6-4eb4cedec2b6
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Invalid coin denominations (e.g., non-numeric, zero, or negative values) are properly rejected with an informative error message on the results page.

---

#### Test TC007 Reject submission when no algorithm is selected
- **Test Code:** [TC007_Reject_submission_when_no_algorithm_is_selected.py](./TC007_Reject_submission_when_no_algorithm_is_selected.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/3ab10097-20a7-4cb2-87b6-b78c87de822a
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Duplicate coverage with TC005 confirms robustness of the no-algorithm guard across different test paths. Error handling is consistent.

---

#### Test TC008 Reject invalid coin input on solve form
- **Test Code:** [TC008_Reject_invalid_coin_input_on_solve_form.py](./TC008_Reject_invalid_coin_input_on_solve_form.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/131bab78-b800-4f7d-b061-afe46079b653
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** A second validation path for invalid coin inputs confirms server-side validation is applied consistently regardless of how the form is submitted.

---

### Requirement: Solve Coin Change via REST API
- **Description:** The `/api/solve` GET endpoint accepts coins, amount, and optional algorithms query params, and returns a structured JSON response with per-algorithm results.

#### Test TC009 Solve coin change through the REST API with one algorithm
- **Test Code:** [TC009_Solve_coin_change_through_the_REST_API_with_one_algorithm.py](./TC009_Solve_coin_change_through_the_REST_API_with_one_algorithm.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/ea1280e0-20eb-46db-a88d-814a98aa5778
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Single-algorithm REST API call returns correctly structured JSON with `coins_used`, `count`, `optimal`, and `time_ms` fields.

---

#### Test TC010 API returns dynamic programming solution
- **Test Code:** [TC010_API_returns_dynamic_programming_solution.py](./TC010_API_returns_dynamic_programming_solution.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/c8be7f38-57d8-4e4c-b3a7-be6d999e048d
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** DP algorithm via API returns the optimal solution and correct coin breakdown. The `optimal` field is `true` as expected.

---

#### Test TC011 Solve coin change through the REST API with multiple algorithms
- **Test Code:** [TC011_Solve_coin_change_through_the_REST_API_with_multiple_algorithms.py](./TC011_Solve_coin_change_through_the_REST_API_with_multiple_algorithms.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/ebf9b930-c025-4d36-88cd-5b0dbc90103f
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Multi-algorithm REST call returns results for all requested algorithms ordered correctly (greedy → dp → backtracking). Response structure is valid JSON.

---

#### Test TC012 Compare multiple algorithms on the same input
- **Test Code:** [TC012_Compare_multiple_algorithms_on_the_same_input.py](./TC012_Compare_multiple_algorithms_on_the_same_input.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/d1eef73f-5a7d-4ba1-a9b7-914f19d7f7c1
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** When all algorithms are run on the same input, their results are consistent and comparable. Coin counts from DP and backtracking match when both yield the optimal solution.

---

### Requirement: Performance Analysis
- **Description:** The `/analysis` endpoint benchmarks all three algorithms across increasing amounts and generates PNG charts (time, coins used, memory, greedy gap) plus a summary table.

#### Test TC013 Run performance analysis and view benchmark summary
- **Test Code:** [TC013_Run_performance_analysis_and_view_benchmark_summary.py](./TC013_Run_performance_analysis_and_view_benchmark_summary.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/3433c656-bca5-4adc-a7da-6a1431585e6b
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Analysis endpoint successfully ran benchmarks, generated all four PNG graphs, and rendered the summary table. No file system or rendering errors observed.

---

#### Test TC014 Review analysis summary metrics and charts
- **Test Code:** [TC014_Review_analysis_summary_metrics_and_charts.py](./TC014_Review_analysis_summary_metrics_and_charts.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/c9a443d2-0f69-41d1-9018-1ec6b7069501
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Charts and summary metrics (complexity table, greedy gap summary) are correctly rendered on the analysis page. Static file paths resolve correctly for all four graph images.

---

### Requirement: Greedy Optimality Verification
- **Description:** Greedy results must always be verified against the DP optimal solution — the greedy module's own `optimal` flag is never trusted alone.

#### Test TC015 Verify greedy results are checked against the optimal solution
- **Test Code:** [TC015_Verify_greedy_results_are_checked_against_the_optimal_solution.py](./TC015_Verify_greedy_results_are_checked_against_the_optimal_solution.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/87565e29-6ee0-437c-87f6-99564419eeb8/a8ed53b9-57ab-4959-b177-e467fc9f91b8
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** The app correctly runs a silent DP check when greedy is selected without DP, and the optimality badge accurately reflects whether greedy matched the DP optimum. Non-canonical coin systems (where greedy is suboptimal) are correctly identified.

---

## 3️⃣ Coverage & Matching Metrics

- **100%** of tests passed (15/15)

| Requirement                          | Total Tests | ✅ Passed | ❌ Failed |
|--------------------------------------|-------------|-----------|-----------|
| Solve Coin Change via HTML Form      | 8           | 8         | 0         |
| Solve Coin Change via REST API       | 4           | 4         | 0         |
| Performance Analysis                 | 2           | 2         | 0         |
| Greedy Optimality Verification       | 1           | 1         | 0         |
| **Total**                            | **15**      | **15**    | **0**     |

---

## 4️⃣ Key Gaps / Risks

> **100% of tests passed fully** — all 15 test cases across 4 requirement groups passed with no failures.

**Observed risks and untested areas:**

- **Backtracking limit boundary**: Tests did not explicitly verify the behavior when `amount == 60` (the exact limit boundary) vs `amount == 61` (should be rejected). Edge case at the hard cap deserves explicit coverage.
- **Amount = 0 edge case**: No test explicitly verifies that all algorithms handle `amount = 0` correctly (expected: empty coin list, count = 0, optimal = true).
- **Impossible change scenario**: No test covers a case where no combination of coins can make the target amount (e.g., coins = [2], amount = 3). DP and backtracking should handle this gracefully.
- **Large amount stress test**: REST API and HTML form were not tested with very large amounts (e.g., amount = 10000) to verify DP performance and absence of timeouts.
- **Concurrent requests**: Dev-mode server (single-threaded uvicorn with `--reload`) was not stress-tested under concurrent load; the analysis endpoint is compute-heavy and could block under simultaneous requests.
- **Graph file persistence**: Old graph PNGs in `static/graphs/` are overwritten silently on each analysis run — no test verified stale-file cleanup or file naming collisions between different coin inputs run in sequence.
