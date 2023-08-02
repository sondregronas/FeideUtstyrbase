# UtstyrServer with Feide innlogging
- [x] Student registration using FEIDE login
- [x] Inventory management for rental equipment (with label printer API https://github.com/VaagenIM/EtikettServer)
- [x] Kiosk mode with non-feide login (password)
- [x] Email reports to teachers
- [x] Frontend that makes sense
- [x] Move off CDNs
- [ ] Move to a proper database?
- [ ] Tests
- [x] Return form
- [x] Searchable logs
- [ ] Docker

Status: its "working", needs a lot of work to make things more coherent and less spaghetti code. Frontend is not pretty, but it works.

## setup
copy `.env.example` to `.env`, add values from Dataporten

Must be accessed through a reverse proxy, as the server does not support https. Use something like NginxProxyManager.