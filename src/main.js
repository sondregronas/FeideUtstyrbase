let express = require("express");
let session = require("express-session");
let app = express();

app.use(express.static("public"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.set("views", "./views");
app.set("view engine", "pug");

let feide = require("./feide");
let router_utils = require("./router_utils");
let db = require("./database");
let secrets = require("./globals");

app.use(
  session({
    secret: secrets.session_secret,
    resave: false,
    saveUninitialized: false,
  })
);

// Ensure that the user is logged in before accessing the protected routes
const protected_routes = ["/edugear", "/register"];
app.use(protected_routes, async (req, res, next) => {
  try {
    res.locals.openid = await feide.getClientInfo(req.session.token, true);
  } catch (e) {
    console.log("Error: User not logged in.");
    req.session.destroy();
    res.redirect("/login");
    return;
  }
  next();
});

app.get("/", (req, res) => {
  res.render("index", { title: "Hey", message: "Hello there!" });
});

app.get("/auth", async (req, res) => {
  // Get the access token from the code provided by feide in the redirect_uri
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

app.get("/logout", (req, res) => {
  req.session.destroy();
  res.redirect("/");
});

// PROTECTED ROUTES
/////////////////////
app.get("/register", async (req, res) => {
  res.render("register", {
    feide: db.readFeideUser(res.locals.openid.sub),
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
  res.send("edugear");
});

// Start the server
db.initializeAll();
app.listen(3000, () => {
  console.log("Server started on port 3000");
});
