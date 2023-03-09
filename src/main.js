let express = require("express");
let expressSession = require("express-session");
let cookieParser = require("cookie-parser");
let app = express();

app.use(cookieParser());
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
  expressSession({
    secret: secrets.session_secret,
    resave: false,
    saveUninitialized: true,
    cookie: { secure: secrets.redirect_uri.startsWith("https") },
  })
);

// PRIVATE ROUTES
const private_routes = ["/edugear", "/register"];
app.use(private_routes, (req, res, next) => {
  if (!router_utils.userLoggedIn(req)) {
    res.clearCookie("token");
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
  let clientInfo = await feide.getClientInfo(
    await feide.getAccessToken(req.query.code)
  );

  let redirect = router_utils.getRedirectPath(clientInfo);
  if (redirect.logged_in) {
    res.cookie("token", clientInfo.hashed_identifier);
    req.session.logged_in = true;
    db.addFeideUser(clientInfo);
  }
  res.redirect(redirect.redirect_url);
});

app.get("/login", (req, res) => {
  res.redirect(feide.OAuthURL);
});

app.get("/logout", (req, res) => {
  res.clearCookie("token");
  req.session.destroy();
  res.redirect("/");
});

// PROTECTED ROUTES
/////////////////////
app.get("/register", (req, res) => {
  res.render("register", { feide: db.readFeideUser(req.cookies.token) });
});

app.post("/register", (req, res) => {
  if (!router_utils.userLoggedIn(req)) {
    res.redirect("/logout");
    return;
  }
  try {
    console.log(req.body);
    db.addRegisteredUser(
      req.cookies.token,
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
  res.send(db.readFeideUser(req.cookies.token));
});

// Start the server
db.initializeAll();
app.listen(3000, () => {
  console.log("Server started on port 3000");
});
