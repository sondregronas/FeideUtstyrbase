# Routine tasks

The project has the following routine tasks:

- Every monday to friday at 10:00, a report is sent to the configured Teams webhooks with a list of all items that are
  overdue. (Can be toggled in the admin panel)
- Every sunday at 01:00, inactive users are removed from the database, and the database is backed up to `/backups/` with
  the filename `backup-<date>.sqlite`.