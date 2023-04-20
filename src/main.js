let feide = require("./feide");
let router_utils = require("./router_utils");
let db = require("./database");
let secrets = require("./globals");
let express_utils = require("./express_utils");

let { getExpressApp } = express_utils;
let { sendMail } = require("./mail");

let app = getExpressApp();
let pug = require("pug");

app.get("/", (req, res) => {
  res.render("index", { ...router_utils.getUserStatus(req) });
});

app.get("/auth", async (req, res) => {
  // Get the access token from the code provided by feide in the redirect_uri
  console.log(req.query);
  let accessToken = await feide.getAccessToken(req.query.code);
  try {
    // Get the clients info, including the users extended info & groups
    let clientInfo = await feide.getClientInfo(accessToken);
    let affiliation = clientInfo.ext_info.eduPersonPrimaryAffiliation;

    // Add the user to the database
    db.addFeideUser(clientInfo);

    // Save the access token in the session
    req.session.token = accessToken;
    req.session.logged_in = true;

    // Redirect the user to the correct page, based on their affiliation
    res.redirect(router_utils.getRedirectPath(affiliation));
  } catch (e) {
    // If the query fails, destroy the session and redirect the user to the login page
    req.session.destroy();
    res.redirect("/login");
  }
});

app.get("/login", (req, res) => {
  res.redirect(feide.OAuthURL);
});

if (secrets.kiosk_enabled) {
  app.get("/kiosk", (req, res) => {
    let valid_r = secrets.kiosk_use_fqdn && req.hostname !== secrets.kiosk_fqdn;
    if (req.session.logged_in || valid_r) {
      res.redirect("/");
      return;
    }
    res.render("kiosk_login");
  });

  app.post("/kiosk_login", async (req, res) => {
    let valid_r = secrets.kiosk_use_fqdn && req.hostname !== secrets.kiosk_fqdn;
    if (req.session.logged_in || valid_r) {
      res.redirect("/");
      return;
    }

    let { username, password } = req.body;
    username = username.toLowerCase();
    password = secrets.hash(password);

    if (
      password !== secrets.kiosk_password ||
      username !== secrets.kiosk_username
    ) {
      res.render("kiosk_login", { error: "Feil brukernavn eller passord" });
      return;
    }

    req.session.kiosk_logged_in = true;
    req.session.logged_in = true;
    db.addAudit(`Kiosk logged in.`);
    res.redirect("/edugear");
  });
}

app.get("/logout", async (req, res) => {
  let kiosk = !!req.session.kiosk_logged_in;
  req.session.destroy();

  if (kiosk) {
    res.redirect("/");
    return;
  }
  res.redirect(`https://auth.dataporten.no/openid/endsession`);
});

// PROTECTED ROUTES
/////////////////////
app.get("/register", async (req, res) => {
  let feideUser = undefined;
  try {
    feideUser = await db.readFeideUser(res.locals.openid.sub);
  } catch (e) {
    console.log("Error reading feide user: " + e);
    res.redirect("/");
    return;
  }
  res.render("register", {
    feide: feideUser,
    ...router_utils.getUserStatus(req),
  });
});

app.post("/register", async (req, res) => {
  try {
    db.addRegisteredUser(
      res.locals.openid.sub,
      req.body.classroom,
      req.body.classroom_teacher,
      req.body.personal_email
    );
    res.send("success");
  } catch (e) {
    res.send(e);
  }
});

app.get("/edugear", (req, res) => {
  res.render("edugear", {
    ...router_utils.getUserStatus(req),
  });
});

app.get("/inventory", async (req, res) => {
  res.render("inventory", {
    ...router_utils.getUserStatus(req),
  });
});

app.get("/inventory/fetch", async (req, res) => {
  res.send(await db.getInventoryItems());
});

app.post("/inventory/add", (req, res) => {
  try {
    db.addInventoryItem(req.body);
    res.send({ success: true, message: `La til ${req.body.name}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke legge til ${req.body.name}`,
    });
  }
});

app.post("/inventory/remove", (req, res) => {
  try {
    db.removeInventoryItem(req.body.name);
    res.send({ success: true, message: `Fjernet ${req.body.name}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke fjerne ${req.body.name}`,
    });
  }
});

app.post("/inventory/update", (req, res) => {
  try {
    db.updateInventoryItemBasic(req.body.old_name, req.body.new_item);
    res.send({ success: true, message: `Oppdaterte ${req.body.old_name}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke oppdatere ${req.body.name}`,
    });
  }
});

app.get("/users", async (req, res) => {
  res.render("users", {
    ...router_utils.getUserStatus(req),
  });
});

app.get("/users/fetch", async (req, res) => {
  res.send(await db.readAllActiveUsers());
});

app.post("/users/update", async (req, res) => {
  try {
    db.updateUser(req.body);
    res.send({ success: true, message: `Oppdaterte ${req.body.name}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke oppdatere ${req.body.name}`,
    });
  }
});

app.post("/users/deactivate", async (req, res) => {
  try {
    db.deactivateUser(req.body.sub);
    res.send({ success: true, message: `Deaktiverte ${req.body.sub}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke deaktivere ${req.body.sub}`,
    });
  }
});

app.get("/lend", async (req, res) => {
  res.render("lend", {
    inventory: await db.getInventoryItems(),
    ...router_utils.getUserStatus(req),
    users: db.readAllActiveUsers(),
  });
});

app.post("/api/lend", async (req, res) => {
  try {
    db.addLend(req.body);
    return res.send({ success: true, message: `Utlånt ${req.body.name}` });
  } catch (e) {
    console.log(e);
    res.send({
      success: false,
      message: `Kunne ikke låne bort ${req.body.name}`,
    });
  }
});

app.get("/api/loans/overdue", async (req, res) => {
  res.send(await db.getOverdueLoans());
});

app.get("/api/loans/active", async (req, res) => {
  res.send(await db.getActiveLoans());
});

app.get("/logs", async (req, res) => {
  res.render("logs", {
    ...router_utils.getUserStatus(req),
  });
});

app.get("/logs/fetch", async (req, res) => {
  res.send(await db.readAudits(req.query.count, req.query.offset));
});

// Temporary as get, should be post
app.get("/mail/send", async (req, res) => {
  let template = `views/mail/${req.query.template}.pug`;
  let to = req.query.to;
  let subject = `[UTSTYRSBASE] ${req.query.subject}`;
  let text = pug.renderFile(template);

  if (!to || !subject || !text) {
    res.send("error");
    return;
  }

  await sendMail(to, subject, text).catch((e) => {
    console.log(e);
    res.send("error");
  });
  db.addAudit(`Sendte mail til ${to} (${subject})`);
});

// Start the server
db.initializeAll();
app.listen(3000, () => {
  console.log("Server started on port 3000");
});
