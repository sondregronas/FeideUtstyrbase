<img src=".github/social-preview.png" width="800" alt="Logo">

[![GitHub Pages](https://badgen.net/badge/preview/github%20pages/?icon=chrome)](https://sondregronas.github.io/FeideUtstyrbase/)
[![GitHub Pages](https://badgen.net/badge/docs/github%20pages/?icon=chrome)](https://sondregronas.github.io/FeideUtstyrbase/docs)
[![Test Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/CI.yml?label=tests)](https://github.com/sondregronas/FeideUtstyrbase)
[![Build Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/release.yml?branch=main)](https://github.com/sondregronas/FeideUtstyrbase/pkgs/container/feideutstyrbase)
[![codecov](https://codecov.io/gh/sondregronas/FeideUtstyrbase/branch/main/graph/badge.svg?token=JNLY5WWC3X)](https://codecov.io/gh/sondregronas/FeideUtstyrbase)
[![License](https://img.shields.io/github/license/sondregronas/FeideUtstyrbase)](https://github.com/sondregronas/FeideUtstyrbase/blob/main/LICENSE)

For Vågen VGS, might be possible to use for other schools with some modifications. (Work in progress, this is not plug
and play).

## Dev setup

Recommended `.env` file for development:

```
DEBUG=True  
MOCK_DATA=True             # Uses mock data instead of real data
KIOSK_FQDN=127.0.0.1:5000  # Automatically logs in as Kiosk user when visiting this domain
```

> If both `DEBUG` and `MOCK_DATA` are set to true you can also log in as an admin by visiting `/demo-login`, which is
> slightly different from logging in as kiosk.

## Setup

1. Register an app at Dataporten (must be approved by your Feide Administrator) with the scopes `email`, `groups-org`
   and `userinfo-name`
2. Set the callback url to `https://<FQDN>/login/feide/callback`
3. Install the labelprinter/service https://github.com/VaagenIM/EtikettServer (currently a requirement)
4. The application sends notifications using Teams Incoming Webhooks, they need to be comma separated in
   the `TEAMS_WEBHOOKS` environment variable. (see cron examples in docs for how to automatically send reports to teams)
5. Run the `docker-compose.yml` file after setting up the environment variables.

> The application must be configured to run through a reverse proxy, such
> as [NginxProxyManager](https://nginxproxymanager.com/) - don't run in production without SSL.

To configure a kiosk, set up a separate reverse proxy with proper access controls (limit to specified IP) and
set `KIOSK_FQDN` to the FQDN of the kiosk proxy. (Remember to restrict access further by setting up a firewall rule) and
add a `X-Internal-Auth` header in your proxy corresponding to the `KIOSK_SECRET` environment variable.

## Overrides

You can change any of the files inside `BookingSystem` by putting them in `/overrides`, should you need to. Files of
interest are `/overrides/templates/user/globals.html` and those found in `/overrides/static/*`

## TODO:

- [ ] Find a way to implement included_batteries (and possibly other accessories) in a way that makes sense (omitted
  entirely them for now)
- [ ] Code cleanup / refactoring, it's a bit inconsistent
- [ ] New UI / UX (In progress)
- [ ] Reduce coupling between modules (database, api, etc.)
- [ ] Add the possibility to limit access to specific Dataporten groups and limit administrator access to specific email
  addresses or something similar, currently every employee can access the admin panel.
