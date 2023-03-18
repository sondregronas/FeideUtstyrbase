# EduGearConnect
A Feide application for equipment management.

Right now it's a mess.

You need to copy `globals.example.js` to `globals.js` and fill in the blanks. Will move to `.env` soon, and add a Dockerfile.

## Dataporten scopes: 
- [ ] `email` - the app sends emails when items are late for delivery to both the student & the classroom teacher
- [ ] `groups-org` - gets the user affiliation (student / employee)
- [ ] `userinfo-name` - names tend to be friendlier than unique identifiers, but that's just an opinion
- [ ] `userinfo-photo` (optional) - currently not in use, but it is stored should one want to use it
