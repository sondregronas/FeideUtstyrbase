# Feide Utstyrbase
For Vågen VGS, might be possible to use for other schools with some modifications - for now this fits our needs, but will most likely not fit yours.

## Setup
README coming soon.

- Register app at Dataporten
- Set callback url to `https://<your-domain>/login/feide/callback`
- Setup https://github.com/VaagenIM/EtikettServer (Currently not optional)
- Only supports SMTP for now.
- Run the `docker-compose.yml` file after setting up the environment variables.

Must be accessed through a reverse proxy, as the server does not support https. Use something like NginxProxyManager. Port `5000` is exposed.

If you need a kiosk mode, set up a separate reverse proxy with a valid access control (see NgixnProxyManager) and set the `KIOSK_MODE` environment variable to the FQDN of the proxy.

## API Endpoints:
Some endpoints can be accessed without login using the specified `?token=<token>` parameter.

- `GET /items` - Get all items in the database as JSON.
- `POST /email/report (params: interval=<days>` - Send out an email report to all specified emails (in admin panel), see `cron_examples.txt` for an example use case.
- `POST /users/prune_inactive` - Remove all inactive users from the database (regular users expire in July, admins never expire).

## TODO:
- [ ] Prettier frontend (`booking.html` needs more work)
- [ ] Move to a proper database?
- [ ] Tests
- [ ] Documentation
- [ ] Docker