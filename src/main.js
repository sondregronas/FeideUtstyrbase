let feide = require("./feide");
let router_utils = require("./router_utils");
let db = require("./database");
let secrets = require("./globals");
let express_utils = require("./express_utils");

let { getExpressApp } = express_utils;

let app = getExpressApp();

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

app.get("/logout", async (req, res) => {
  req.session.destroy();
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

app.get("/lend", async (req, res) => {
  res.render("lend", {
    inventory: await db.getInventoryItems(),
    ...router_utils.getUserStatus(req),
    users: db.readAllActiveUsers(),
  });
});

// Start the server
db.initializeAll();
app.listen(3000, () => {
  console.log("Server started on port 3000");
});
