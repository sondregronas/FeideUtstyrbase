# Feide Utstyrbase
[![GitHub Pages](https://badgen.net/badge/preview/github%20pages/?icon=chrome)](https://sondregronas.github.io/FeideUtstyrbase/)
[![GitHub Pages](https://badgen.net/badge/docs/github%20pages/?icon=chrome)](https://sondregronas.github.io/FeideUtstyrbase/docs)
[![Test Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/CI.yml?label=tests)](https://github.com/sondregronas/FeideUtstyrbase)
[![Build Status](https://img.shields.io/github/actions/workflow/status/sondregronas/FeideUtstyrbase/release.yml?branch=main)](https://github.com/sondregronas/FeideUtstyrbase/pkgs/container/feideutstyrbase)
[![codecov](https://codecov.io/gh/sondregronas/FeideUtstyrbase/branch/main/graph/badge.svg?token=JNLY5WWC3X)](https://codecov.io/gh/sondregronas/FeideUtstyrbase)
[![License](https://img.shields.io/github/license/sondregronas/FeideUtstyrbase)](https://github.com/sondregronas/FeideUtstyrbase/blob/main/LICENSE)

For Vågen VGS, might be possible to use for other schools with some modifications. (Work in progress, not plug and play)

## Dev setup
Recommended `.env` file for development:
```
DEBUG=True  
MOCK_DATA=True             # Uses mock data instead of real data
KIOSK_FQDN=127.0.0.1:5000  # Automatically logs in as Kiosk user when visiting this domain
```

> If both `DEBUG` and `MOCK_DATA` are set to true you can also log in as an admin by visiting `/demo-login`, which is slightly different from logging in as kiosk.

## Setup

1. Register app at Dataporten (must be approved by a Feide Administrator)
2. Set callback url to `https://<your-domain>/login/feide/callback`
3. Setup https://github.com/VaagenIM/EtikettServer (currently not optional)
4. Add as many Teams webhooks as you want, they need to be comma separated in the `TEAMS_WEBHOOKS` environment variable. (see cron examples in docs for how to automatically send reports to teams)
5. Run the `docker-compose.yml` file after setting up the environment variables.

> The application must be configured through a reverse proxy, such as [NginxProxyManager](https://nginxproxymanager.com/) - you don't want to run this without SSL.

To configure a kiosk, set up a separate reverse proxy with proper access controls (limit to specified IP) and set `KIOSK_FQDN` to the FQDN of the kiosk proxy. (Remember, you can restrict access further by setting up a firewall rule)

## Overrides

Logo and favicon can be changed by replacing the files in `/overrides/static/` with your own within the container, requiring the mapping of the `/overrides` directory. You can also change any of the files inside `BookingSystem` by putting them in `/overrides` should you need to.

## TODO:

- [ ] Find a way to implement included_batteries (and possibly other accessories) in a way that makes sense (ignoring them for now)
- [ ] Code cleanup / refactoring, it's very inconsistent
- [ ] Reduce coupling between modules (database, api, etc. - its a bit inconsistent)
- [ ] Actual logo and favicon (currently a playstation shopping bag emoji)