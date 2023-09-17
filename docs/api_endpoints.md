# API Endpoints (no auth required)

The following endpoints are available for the API, meaning they can be accessed without logging in using the `?token=<token>` parameter. Useful for cron jobs and such.

## Endpoints

> [!NOTE]+ GET: `/items` 
> Get all items in the database as JSON.

> [!NOTE]+ GET: `/items/available` 
> Get all available items as JSON.

> [!NOTE]+ GET: `/items/unavailable` 
> Get all unavailable items as JSON.

> [!NOTE]+ GET: `/items/overdue` 
> Get all overdue items as JSON.

> [!NOTE]+ GET: `/items/user/<userid>` 
> Get all items borrowed by a user as JSON.

> [!NOTE]+ GET: `/user/<userid>` 
> Get user info as JSON (userid is from `/items`, `borrowed_to`).

> [!TIP]+ POST: `/send_report (params: interval=<days>` 
> Send out an report to all configured teams webhooks, see cron_examples.txt for an example use case.

> [!TIP]+ POST: `/backup/<filename>.sqlite` 
> Backup the database to a file in the `/data/backups` directory (see cron_examples for an example use case).

> [!TIP]+ POST: `/users/prune_inactive` 
> Remove all inactive users from the database (regular users expire in July, admins never expire).