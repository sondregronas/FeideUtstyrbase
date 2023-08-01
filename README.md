# UtstyrServer with Feide innlogging
The point of this application is to do the following:

- [x] Student registration using FEIDE login
- [ ] Inventory management for rental equipment (with label printer API https://github.com/VaagenIM/EtikettServer)
- [ ] Booking form for teachers / kiosk
- [ ] Return form
- [ ] Searchable logs

Status: OK starting point, missing a lot of API endpoints. Should be refactored to be more cohesive

## setup
copy `.env.example` to `.env`, add values from Dataporten

## Implemented

- [x] Feide login / protected routes using `@login_required(admin_only=True)` decorator in `app.py` / `api.py`
- [x] Classroom selector / admin
- [x] Inventory view

- [x] Endpoint `GET /items`
- [x] Endpoint `GET /items/<id>`
- [x] Endpoint `GET /groups` (All classrooms / teachers)
- [x] Endpoint `POST /update/groups` (Form in `klasser.html`)
- [x] Endpoint `GET /users` (All users, including expired)
- [x] Endpoint `POST /update/student` (form in `index_student.html`)

- [x] A way to add new items to the inventory

## TODO Backend

- [x] Inventory edit / delete
- [x] Inventory print label

- [ ] Book
- [ ] Return

- [ ] Logs
- [ ] Coherent SQL methodology

- [ ] Kiosk mode (username/password login method, locked behind FQND / proxy)

- [ ] Dockerfile
- [ ] Split up the functions from `api.py` to their respective modules, too much responsibility per function right now (though it's not a problem yet)

## TODO Frontend

- [ ] Everything