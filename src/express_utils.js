const express = require("express");
const session = require("express-session");

const secrets = require("./globals");
const feide = require("./feide");
const db = require("./database");
const router_utils = require("./router_utils");

let protected_routes = ["/edugear", "/register"];
const employee_routes = ["/inventory", "/inventory/*"];
protected_routes = protected_routes.concat(employee_routes);

function getExpressApp() {
  let app = express();

  app.use(express.static("public"));
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  app.set("views", "./views");
  app.set("view engine", "pug");

  app.use(
    session({
      secret: secrets.session_secret,
      resave: false,
      saveUninitialized: false,
    })
  );

  // Ensure that the user is logged in before accessing the protected routes
  if (!secrets.devmode) {
    app.use(protected_routes, async (req, res, next) => {
      if (req.session.kiosk_logged_in) {
        next();
        return;
      }
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

    // Employees only routes
    app.use(employee_routes, async (req, res, next) => {
      if (req.session.kiosk_logged_in) {
        next();
        return;
      }

      let sub = res.locals.openid.sub;
      let affiliation = (await db.readFeideUser(sub).affiliation) || undefined;
      if (affiliation !== "employee" && !req.session.kiosk_logged_in) {
        res.status(403).render("403", { ...router_utils.getUserStatus(req) });
        return;
      }
      next();
    });
  }

  // Easy livereload
  if (secrets.devmode) {
    const watchFolders = [
      "views",
      "views/partials",
      "views/conf",
      "views/modals",
      "public",
      "public/js",
    ];

    app.use(
      require("easy-livereload")({
        watchDirs: watchFolders.map((folder) =>
          require("path").join(__dirname, folder)
        ),
        checkFunc: (file) => {
          return /.(pug|css|js|jpg|png|gif|svg)$/.test(file);
        },
      })
    );
  }

  return app;
}

module.exports = {
  getExpressApp,
};
