# Feide Utstyrbase
[![Test Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/CI.yml?label=tests)](https://github.com/sondregronas/FeideUtstyrbase)
[![Build Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/release.yml?branch=main)](https://github.com/sondregronas/FeideUtstyrbase/pkgs/container/feideutstyrbase)
[![codecov](https://codecov.io/gh/sondregronas/FeideUtstyrbase/branch/main/graph/badge.svg?token=JNLY5WWC3X)](https://codecov.io/gh/sondregronas/FeideUtstyrbase)
[![License](https://img.shields.io/github/license/sondregronas/FeideUtstyrbase)](https://github.com/sondregronas/FeideUtstyrbase/blob/main/LICENSE)

For Vågen VGS, might be possible to use for other schools with some modifications. (Work in progress, this is NOT plug and play)

## Setup
Proper README coming soon.

- Register app at Dataporten (must be approved by a Feide Administrator)
- Set callback url to `https://<your-domain>/login/feide/callback`
- Setup https://github.com/VaagenIM/EtikettServer (currently not optional)
- Add as many Teams webhooks as you want, they need to be comma separated in the `TEAMS_WEBHOOKS` environment variable. (using cron to send out reports - will be built in sooner or later, see `cron_examples.txt` for an example use case)
- Run the `docker-compose.yml` file after setting up the environment variables.

Must be accessed through a reverse proxy, such as [NginxProxyManager](https://nginxproxymanager.com/).

If you need a kiosk, set up a separate reverse proxy with proper access controls (limit to specified IP) and set `KIOSK_FQDN` to the FQDN of the kiosk proxy.

Logo and favicon can be changed by replacing the files in `/overrides/static/` with your own within the container, requiring the mapping of the `/overrides` directory. You can also change any of the files inside `BookingSystem` by putting them in `/overrides` should you need to.

## API Endpoints:
Some endpoints can be accessed without login using the specified `?token=<token>` parameter. This isn't strictly necessary, but a few endpoints are useful for cron jobs and such.

- `GET /items` - Get all items in the database as JSON.
- `GET /items/available` - Get all available items as JSON.
- `GET /items/unavailable` - Get all unavailable items as JSON.
- `GET /items/overdue` - Get all overdue items as JSON.
- `GET /items/user/<userid>` - Get all items borrowed by a user as JSON.
- `GET /user/<userid>` - Get user info as JSON (userid is from `/items`, `borrowed_to`).
- `POST /send_report (params: interval=<days>` - Send out an report to all configured teams webhooks, see `cron_examples.txt` for an example use case.
- `POST /backup/<filename>.sqlite` - Backup the database to a file in `/backups` (see `cron_examples.txt` for an example use case).
- `POST /users/prune_inactive` - Remove all inactive users from the database (regular users expire in July, admins never expire).

## TODO:
- [ ] Find a way to implement included_batteries (and possibly other accessories) in a way that makes sense (omitting them for now)
- [ ] Move to a proper database?
- [ ] Tests
- [ ] Documentation
- [ ] Better README
- [ ] `booking.html` is a mess.
- [ ] Code cleanup / refactoring, it's a bit inconsistent right now.
- [ ] Actual logo and favicon (currently a playstation shopping bag emoji)

## Dependencies
Python Dependencies are listed in `requirements.txt`

JS/CSS libraries are used:

- [PicoCSS](https://picocss.com/) (for now)
- [jQuery](https://jquery.com/)
- [DataTables](https://datatables.net/)
- [iziToast](https://izitoast.marcelodolza.com/)
- [jquery-confirm](https://craftpip.github.io/jquery-confirm/)
- [Font Awesome](https://fontawesome.com/)
- [Tom Select](https://tom-select.js.org/)
- [html5-qrcode](https://github.com/mebjas/html5-qrcode)
