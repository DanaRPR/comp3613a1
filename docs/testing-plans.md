# Student Awards — Test Plans

These plans use the table formats from Tutorials 4 and 5. The unit and
integration sections map the implemented pytest functions to the assertions
they actually make; they do not report test outcomes. The API section describes
planned Postman checks. The application workflow routes return rendered HTML
or redirects; they do not return JSON.

Test data must use an isolated test database and must never use deployed or
production data. The pytest suite is split with `@pytest.mark.unit` for
isolated service and route behavior with fake dependencies and
`@pytest.mark.integration` for service/repository calls against the SQLite
test database. The current suite has 11 unit tests and 17 integration tests
(28 tests total).

The application seeds Bronze, Silver, and Gold with thresholds of 20, 35,
and 50 approved hours, respectively (`app/cli.py`). Some tests construct
their own Award records with different thresholds (including 10, 20, or 25
hours) to exercise progress and eligibility logic. Those are test-specific
fixture values, not changes to the seeded application award thresholds.

## 1. Unit Test Plan

The unit tests use fake dependencies, including fake repositories, session
objects, templates, and services; they do not use the SQLite fixture or
connect to a configured application database. The table records the
assertions made by the current test functions, not additional expected checks.

| Test function | Behavior exercised | Assertions actually made |
|---|---|---|
| `test_submit_hours_adds_pending_submission()` | `VolunteerHoursService.submit_hours()` with a fake repository | Returned submission has `pending` status, the supplied student ID, hours, and activity; the fake repository's submission is the returned object. The test does not assert the date. |
| `test_approve_updates_submission_and_totals()` | `VolunteerHoursService.approve()` with fake submission, student, and progress objects | Status becomes `approved`, administrator ID is set, student total increases from 10 to 18, progress total increases from 15 to 23, and the fake session records an added object. It does not assert a commit, persisted state, or approval of a missing progress row. |
| `test_approve_raises_value_error_for_missing_submission()` | Approval of an absent submission | Raises `ValueError` with message matching `Submission not found`. |
| `test_reject_marks_submission_rejected()` | `VolunteerHoursService.reject()` with a fake submission | Status becomes `rejected`, administrator ID is set, and the fake session records an added object. It does not assert unchanged student/progress totals. |
| `test_get_available_awards_marks_eligible_and_not_redeemed()` | Award availability with one award, sufficient supplied hours, and no redeemed IDs | The result is available and `already_redeemed` is false. |
| `test_get_available_awards_marks_redeemed_and_ineligible()` | Award availability with supplied hours below the threshold and that award ID in redeemed IDs | The result is unavailable and `already_redeemed` is true. Because both conditions are present together, this test does not isolate either condition. |
| `test_redeem_raises_for_missing_award()` | Redemption when the fake repository has no awards | Raises `ValueError` with message matching `Award not found`. |
| `test_redeem_raises_for_duplicate_redemption()` | Redemption when the award ID is already in the fake repository's redeemed IDs | Raises `ValueError` with message matching `already redeemed`. |
| `test_get_leaderboard_assigns_rank_and_current_student()` | Leaderboard formatting with two ordered fake student rows | First row has rank 1, expected name and hours, and `is_current` true; second row has `is_current` false. It does not test repository ordering or admin filtering. |
| `test_get_progress_returns_next_award_and_threshold()` | Progress summary with fake progress, awards, and one redeemed award | Returns the same progress object, selects the second test award as `next_award`, and reports its test-specific threshold of 25 hours (not the seeded Silver threshold). |
| `test_submit_action_renders_value_error_message()` | `submit_hours.submit_action()` with a fake service that raises `ValueError` | Checks the response status is 400, the rendered template is `submit_hours.html`, and the error context contains `invalid submission`. |

`VolunteerHoursService.approve()`, `VolunteerHoursService.reject()`,
`LeaderboardService.get_progress()`, and `AwardService.redeem()` also have
unit tests using fake repository/session dependencies. Those tests check only
the assertions listed above; database persistence is covered separately by
integration tests where applicable.

## 2. Integration Test Plan

Integration tests use the shared `session` fixture, which creates tables in a
temporary SQLite database under `tmp_path`. They exercise services and
repositories with SQLModel records; they do not connect to the Render database.
Descriptions below are limited to what each function explicitly asserts.

| Test function | Behavior exercised | Assertions actually made |
|---|---|---|
| `test_submit_hours_creates_pending_submission()` | Submit hours through the service and repository | Reads the created record from the test session and checks it exists, has `pending` status, the expected student ID, and 5 hours. It does not assert the saved date or activity. |
| `test_approve_submission_updates_student_and_progress()` | Approve a pending submission with an existing Progress row | Checks returned status is `approved`; stored student total is 8; stored progress total is 8 and `awardsEarned` is 0. It does not assert the submission's administrator ID. |
| `test_approve_submission_creates_progress_when_missing()` | Approve a pending submission without an existing Progress row | Checks returned status is `approved`; a Progress row exists with total hours 8 and zero awards earned. |
| `test_approve_submission_rejects_duplicate_review()` | Approve the same submission twice | The second call raises `ValueError` matching `already been reviewed`. It does not assert that totals remain unchanged after the second call. |
| `test_approve_missing_submission_raises_value_error()` | Approve a nonexistent submission | Raises `ValueError` matching `Submission not found`. |
| `test_reject_submission_sets_rejected_status()` | Reject a pending submission | Checks returned status is `rejected` and administrator ID is 7. It does not check student or progress totals. |
| `test_reject_missing_submission_raises_value_error()` | Reject a nonexistent submission | Raises `ValueError` matching `Submission not found`. |
| `test_pending_submissions_include_student_names()` | Retrieve pending submissions through the repository | Checks two rows are returned, their student names are the two expected usernames, and their activities are the two expected pending activities. A reviewed row is seeded but the test does not directly assert its ID or status is absent, nor check returned dates/hours. |
| `test_get_available_awards_eligible_and_unredeemed()` | Award availability for one award with supplied hours above its threshold and no redemption | Checks `available` is true and `already_redeemed` is false. |
| `test_get_available_awards_marks_ineligible_and_redeemed()` | Award availability for an award below its threshold that has also been redeemed | Checks `available` is false and `already_redeemed` is true. The two conditions are combined rather than isolated. |
| `test_redeem_award_creates_redemption_and_updates_progress()` | Redeem an eligible award with an existing Progress row | Checks the returned redemption is `completed` and has the student's ID, and stored `Progress.awardsEarned` is 1. It does not query the database to independently verify the redemption row. |
| `test_redeem_award_does_not_create_missing_progress()` | Redeem an eligible award without a Progress row | Checks returned redemption status is `completed` and no Progress row exists afterward. It does not independently query for a saved Redemption row. |
| `test_redeem_award_rejects_insufficient_hours()` | Redeem below the award threshold | Raises `ValueError` with message matching `You need`. It does not assert database state afterward. |
| `test_redeem_award_rejects_duplicate()` | Redeem an award, then attempt the same redemption again | The second call raises `ValueError` matching `already redeemed`. It does not assert the number of redemption rows afterward. |
| `test_leaderboard_excludes_admins_and_orders_students_by_hours()` | Retrieve leaderboard with an admin at 99 hours and students at 20 and 15 hours | Checks returned names are `student1`, then `student2`, first row rank is 1, and first row is marked current. The names/order establish that the seeded admin is not in the result; it does not assert every row's displayed hour value or tie handling. |
| `test_get_progress_returns_next_unredeemed_award()` | Progress summary when the only seeded award is redeemed | Checks progress total is 30 and both `next_award` and `next_threshold` are `None`. |
| `test_get_progress_returns_first_unredeemed_award()` | Progress summary with two test awards, the lower-threshold award redeemed | Checks the next award is named Silver and the next test-specific threshold is 25 hours (not the seeded Silver threshold of 35 hours). It does not assert the returned progress object or total. |

## 3. API Test Plan

API tests use Postman against the local app. Form submissions use
`application/x-www-form-urlencoded`. Authenticated routes use the `access_token`
cookie set by a successful login. Disable automatic redirect following when
checking a redirect's status and `Location` header.

| Description | Method | URL | Request Headers, Body | Response Body, Status |
|---|---|---|---|---|
| Display login form | `GET` | `/login` | No body required | Rendered login HTML; `200`. |
| Log in with valid credentials | `POST` | `/login` | Form fields: `username`, `password` | Redirect to the role-specific home page; `303`; successful response sets the `access_token` cookie. |
| Log in with invalid credentials | `POST` | `/login` | Form fields: invalid `username` and/or `password` | Redirect to `/login`; `303`. |
| Display registration form | `GET` | `/register` | No body required | Rendered registration HTML; `200`. |
| Register a user | `POST` | `/register` | Form fields: `username`, `email`, `password` | Redirect to `/login`; `303`. The route's declared `201` does not override the returned redirect response status. |
| Display submit-hours form | `GET` | `/app/submit` | Authenticated user cookie | Rendered submit-hours HTML; `200`. |
| Submit valid volunteer hours | `POST` | `/app/submit` | Authenticated user cookie; form fields: `date`, positive integer `hours`, `activity` | Rendered submit-hours HTML with a success context; `200`. The persisted record has `pending` status. |
| Submit hours with invalid fields | `POST` | `/app/submit` | Authenticated user cookie; invalid/missing `date`, invalid/missing `hours`, or `hours <= 0` | FastAPI request validation response; `422`; route body does not run. |
| Handle a service `ValueError` during submission | `POST` | `/app/submit` | Authenticated user cookie; valid form data; service raises `ValueError` | Rendered `submit_hours.html` with the exception text in the error context; `400`. The unit regression test asserts these response details. |
| Display admin review page | `GET` | `/admin` | Authenticated administrator cookie | Rendered admin HTML with pending records; `200`. |
| Approve volunteer-hours submission | `POST` | `/admin/approve/{submission_id}` | Authenticated administrator cookie; integer path parameter `submission_id`; no form body | Redirect to `/admin`; `303`. Verify persisted status and totals separately; the route also redirects when the service raises `ValueError`. |
| Reject volunteer-hours submission | `POST` | `/admin/reject/{submission_id}` | Authenticated administrator cookie; integer path parameter `submission_id`; no form body | Redirect to `/admin`; `303`. Verify persisted status and unchanged totals separately; the route also redirects when the service raises `ValueError`. |
| Display progress | `GET` | `/app/progress` | Authenticated user cookie | Rendered progress HTML; `200`. |
| Display leaderboard | `GET` | `/app/leaderboard` | Authenticated user cookie | Rendered leaderboard HTML; `200`. |
| Display awards | `GET` | `/app/awards` | Authenticated user cookie | Rendered awards HTML; `200`. |
| Redeem award | `POST` | `/app/awards/redeem/{award_id}` | Authenticated user cookie; integer path parameter `award_id`; no form body | Redirect to `/app/awards`; `303`. Verify redemption state separately; the route also redirects when the service raises `ValueError`. |
| Access an `AuthDep` route without a valid cookie | `GET` | For example, `/app/progress` | No cookie or invalid `access_token` cookie | App renders `401.html`; current exception handler returns this template without setting a status code, so the HTTP status is `200`. |
| Access an admin route as a non-admin | `GET` | `/admin` | Valid student `access_token` cookie | App renders `401.html`; current exception handler returns this template without setting a status code, so the HTTP status is `200`. |

## Notes for implementation and reporting

- API tests must distinguish the route response from persisted outcomes. In
  particular, the admin review and redemption routes redirect after both
  successful actions and caught `ValueError` failures.
- `GET /admin` and the review POST routes require `AdminDep`; student workflow
  pages require `AuthDep`. `AuthDep` checks that a user is authenticated but
  does not restrict those pages to the student role, so do not expect admins to
  be blocked from student workflow routes.
- The `/app/submit` router converts a caught `ValueError` with `str(exc)` and
  returns `submit_hours.html` with status `400`. The unit regression test
  `test_submit_action_renders_value_error_message()` uses a fake service that
  raises `ValueError("invalid submission")` and checks the status, template,
  and rendered error context.
- Tests must not connect to or alter the configured production database.

## Source files reviewed

- `app/routers/submit_hours.py`
- `app/routers/admin_home.py`
- `app/routers/progress.py`
- `app/routers/awards.py`
- `app/routers/login.py`
- `app/routers/register.py`
- `app/dependencies/auth.py`
- `app/main.py`
- `app/services/volunteer_hours.py`
- `app/services/award.py`
- `app/services/leaderboard.py`
- `app/repositories/volunteer_hours.py`
- `app/repositories/award.py`
- `app/repositories/leaderboard.py`
- `app/models/volunteer_hours.py`
- `app/models/progress.py`
- `app/models/award.py`
- `app/models/user.py`
