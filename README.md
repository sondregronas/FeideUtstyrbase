# Feide Utstyrbase
[![Test Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/CI.yml?label=tests)](https://github.com/sondregronas/FeideUtstyrbase)
[![Build Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/release.yml?branch=main)](https://github.com/sondregronas/FeideUtstyrbase/pkgs/container/feideutstyrbase)
[![codecov](https://codecov.io/gh/sondregronas/FeideUtstyrbase/branch/main/graph/badge.svg?token=JNLY5WWC3X)](https://codecov.io/gh/sondregronas/FeideUtstyrbase)
[![License](https://img.shields.io/github/license/sondregronas/FeideUtstyrbase)](https://github.com/sondregronas/FeideUtstyrbase/blob/main/LICENSE)

For Vågen VGS, might be possible to use for other schools with some modifications - for now this fits our needs, but will most likely not fit yours. (Work in progress, this is NOT plug and play)

## Setup
Proper README coming soon.

- Register app at Dataporten
- Set callback url to `https://<your-domain>/login/feide/callback`
- Setup https://github.com/VaagenIM/EtikettServer (Currently not optional)
- Only supports SMTP for now.
- Run the `docker-compose.yml` file after setting up the environment variables.

Must be accessed through a reverse proxy, as the server does not support https. Use something like NginxProxyManager. Port `5000` is exposed.

If you need a kiosk mode, set up a separate reverse proxy with a valid access control (see NgixnProxyManager) and set the `KIOSK_MODE` environment variable to the FQDN of the proxy.

## API Endpoints:
Some endpoints can be accessed without login using the specified `?token=<token>` parameter. This isn't strictly necessary, but a few endpoints are useful for cron jobs and such.

- `GET /items` - Get all items in the database as JSON.
- `GET /items/available` - Get all available items as JSON.
- `GET /items/unavailable` - Get all unavailable items as JSON.
- `GET /items/overdue` - Get all overdue items as JSON.
- `GET /user/<userid>` - Get user info as JSON (userid is from `/items`, `borrowed_to`).
- `POST /email/report (params: interval=<days>` - Send out an email report to all specified emails (in admin panel), see `cron_examples.txt` for an example use case.
- `POST /users/prune_inactive` - Remove all inactive users from the database (regular users expire in July, admins never expire).

## TODO:
- [ ] Prettier frontend (`booking.html` needs more work)
- [ ] Move to a proper database?
- [ ] Tests
- [ ] Documentation
- [ ] Docker
- [ ] Better README
- [ ] Code cleanup / refactoring, it's a bit inconsistent right now.
