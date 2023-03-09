let express = require("express");
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

app.get("/", (req, res) => {
  res.render("index", { title: "Hey", message: "Hello there!" });
});

app.get("/auth", async (req, res) => {
  let clientInfo = await feide.getClientInfo(
    await feide.getAccessToken(req.query.code)
  );

  let redirect = router_utils.getRedirectPath(clientInfo);
  if (redirect.logged_in) {
    res.cookie("sub", clientInfo.openid["sub"]);
    db.addFeideUser(clientInfo);
  }
  res.redirect(redirect.redirect_url);
});

app.get("/login", (req, res) => {
  res.redirect(feide.OAuthURL);
});

app.get("/retry", (req, res) => {
  res.send("retry <a href='/login'>login</a>");
});

// /register uses the cookie to get the user info
app.get("/register", (req, res) => {
  if (!req.cookies.sub) {
    res.redirect("/login");
    return;
  }

  res.render("register", { feide: db.readFeideUser(req.cookies.sub) });
});

app.post("/register", (req, res) => {
  try {
    console.log(req.body)
    db.addRegisteredUser(
        req.cookies.sub,
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
  res.send(db.readFeideUser(req.cookies.sub));
});

// Start the server
db.initializeAll();
app.listen(3000, () => {
  console.log("Server started on port 3000");
});
