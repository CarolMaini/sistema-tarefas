# Recurrence rules

The scheduling module implements weekly, biweekly and monthly recurrence generation. A rule belongs to a task and stores its frequency, start/end dates, selected ISO weekdays (Monday = 1 through Sunday = 7), optional default assignee, and (for biweekly rules) an anchor date.

## Frequency behavior

- **Weekly:** generates an occurrence on each selected weekday in every week within the requested generation range.
- **Biweekly:** uses `anchor_date` (or `starts_on` when no anchor is set) as the start of a 14-day cycle. Selected weekdays are generated relative to each cycle's anchor.
- **Monthly:** generates an occurrence on every selected weekday that appears in each calendar month. It does not mean “the same day number” or “the nth weekday” of the month.

For every frequency, generated dates are inclusive of the requested range and must not precede `starts_on` or exceed `ends_on` when an end date is configured. An empty weekday selection produces no dates in the service; the creation form requires at least one weekday.

## Generation and assignments

Creating a recurrence rule generates occurrences from `starts_on` through `ends_on`. When no end date is supplied, the creation view initially generates a rolling horizon of 365 days from the start date. This is a finite initial generation window, not an automatic indefinite scheduler.

Generation is idempotent for a task/date pair: the database uniqueness constraint prevents duplicate occurrences. Re-running generation does not create duplicate assignments or reset an existing assignment's status. If a default assignee is configured and remains eligible (workspace owner or active member), that person is assigned to each occurrence belonging to the rule. An ineligible or inactive default assignee is skipped. Without a default assignee, occurrences are created unassigned.

## Important implementation boundaries

- The service generates dates only when called; this document does not imply that a background job automatically extends the 365-day horizon.
- The monthly rule is based on selected weekdays, not a fixed calendar date.
- Existing occurrences and assignment history are preserved during repeated generation.
- Date generation is covered by automated tests for weekly, biweekly and monthly cases, including anchor-date behavior and idempotency.
