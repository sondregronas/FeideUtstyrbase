# Example cron jobs

Some examples of cron jobs that can be used to automate some tasks.

```bash
# Send report at 8:15 every monday, excluding in the month of july
# Only works when used on the kiosk FQDN, as it uses the kiosk cookie to authenticate
15 8 * 1-6,8-12 MON curl -X POST "<fqdn>/send_report?interval=1&token=<token>"

# Prune inactive users on the first of July
0 1 1 7 * curl -X POST "<fqdn>/users/prune_inactive?token=<token>"

# Backup db weekly
0 1 * * 1 curl -X POST "<fqdn>/backup/backup-$(date +\%Y-w\%V).sqlite?token=<token>"
```