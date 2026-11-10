# Student Awards — UAT Testing Checklist

## Purpose

This completed UAT report records the actual outcomes provided for the seven
Student Awards workflow scenarios. The actual-result text and PASS statuses
below are preserved as reported.

## Test environment and preparation

- Run the application locally and use a non-production database.
- Sign in with the seeded accounts: `bob` / `bobpass` (student) and `admin` /
  `adminpass` (administrator).
- Prepare a pending volunteer-hours submission for approval and a separate one
  for rejection. Record the student's starting approved-hours total before
  reviewing either submission.
- For award tests, use test data that gives the student at least 20 hours for
  the eligible award test and fewer than 20 hours for the unavailable-award
  test. The seeded award thresholds are Bronze 20 hours, Silver 35 hours, and
  Gold 50 hours. An award already redeemed by the student can also be used for
  the unavailable/duplicate test.
- Use a student data set with different hour totals for the leaderboard check.

## Checklist

| Test ID | User Role | Test Scenario | Steps to Perform | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|
| UAT-01 | Student | Submit volunteer hours | 1. Sign in as `bob`.<br>2. Open **Submit Hours**.<br>3. Enter a date/time, a positive whole number of hours, and an activity.<br>4. Submit the form.<br>5. Sign in as administrator and open the review page. | The student sees the submission success message. The administrator's pending list shows the new submission with the student's name, activity, date, and hours. | The student successfully submitted 5 volunteer hours for a community clean-up activity and received a success message. | PASS |
| UAT-02 | Administrator, then Student | Approve a pending submission | 1. With a pending submission available, sign in as `admin`.<br>2. Open the review page and approve the selected submission.<br>3. Sign in as the student and open **Progress**. | The submission is no longer pending. The student's approved-hours total increases by the submitted hours. | The administrator approved the 5-hour Community clean-up submission. The submission disappeared from the pending submissions list. | PASS |
| UAT-03 | Administrator, then Student | Reject a pending submission | 1. With a separate pending submission available, sign in as `admin`.<br>2. Open the review page and reject the selected submission.<br>3. Sign in as the student and open **Progress**. | The submission is no longer pending. The student's approved-hours total does not increase because of the rejected submission. | The administrator rejected the pending volunteer-hours submission. It disappeared from the pending submissions list, leaving no pending submissions. | PASS |
| UAT-04 | Student | View progress and next milestone | 1. Sign in as a student with approved hours.<br>2. Open **Progress**.<br>3. Review the approved-hours value, progress indicator, and next milestone when one remains. | The page displays the student's current approved hours. When an unredeemed award remains, its name and required-hours threshold are shown as the next milestone. | The student's total volunteer hours increased to 10 hours after the administrator approved the 5-hour Community clean-up submission. | PASS |
| UAT-05 | Student | View leaderboard | 1. Sign in as a student.<br>2. Open **Leaderboard**.<br>3. Compare the displayed order with the available students' approved-hour totals. | Students appear in descending total-hours order; the administrator account is excluded; the signed-in student is marked as “(You)”. | The leaderboard displayed bob in first place with 10 volunteer hours. Other students with 0 hours appeared below him. | PASS |
| UAT-06 | Student | Redeem an eligible award | 1. Sign in as a student whose approved hours meet an unredeemed award threshold.<br>2. Open **Awards** and confirm the award is available.<br>3. Redeem it.<br>4. Reopen or refresh **Awards**. | The request returns to the awards page. The redeemed award is displayed as **REDEEMED** rather than **REDEEM**. | The student reached 20 approved volunteer hours, making the Bronze Award eligible for redemption. The student clicked Redeem and the application displayed 'Redeemed', confirming the award was successfully redeemed. | PASS |
| UAT-07 | Student | Attempt to redeem an unavailable or previously redeemed award | 1. Sign in as a student below the selected award's threshold, or select an award already redeemed by that student.<br>2. Confirm the award is marked **UNAVAILABLE** or **REDEEMED**.<br>3. If testing a direct redemption attempt, submit it and revisit **Awards**. | No new redemption is shown for an ineligible or already redeemed award. The route returns to the awards page; the current UI may not display a specific error message. | The Bronze, Silver and Gold awards were marked as unavailable because the student had only 10 approved volunteer hours. The redemption buttons were disabled, preventing the student from attempting to redeem an award. | PASS |

**Separate award test scenarios:** UAT-06 and UAT-07 used different test states. For UAT-06, the student had 20 approved volunteer hours, making the Bronze Award eligible for redemption. For UAT-07, a separate test state had 10 approved volunteer hours, so the awards remained unavailable.

## Wireframe references

### Submit Volunteer Hours

![Submit Volunteer Hours wireframe](wireframes/wireframe%20final-1.png)

### Track Progress and View Leaderboard

![Track Progress and View Leaderboard wireframe](wireframes/wireframe%20final-2.png)

### Redeem Awards

![Redeem Awards wireframe](wireframes/wireframe%20final-3.png)

## Evidence

The repository currently contains the following automated-test evidence:

- Unit test run: [unit-tests.png](test-evidence/unit-tests.png)
- Integration test run: [integration-tests.png](test-evidence/integration-tests.png)
- Postman collection run: [postman-tests-1.png](test-evidence/postman-tests-1.png),
  [postman-tests-2.png](test-evidence/postman-tests-2.png),
  [postman-tests-3.png](test-evidence/postman-tests-3.png), and
  [postman-tests-4.png](test-evidence/postman-tests-4.png)

These are pytest and Postman results, not screenshots of the manual UAT
scenarios. No scenario-specific UAT screenshots or other UAT evidence references
are recorded in this report.
