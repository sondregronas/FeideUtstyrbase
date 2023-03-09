const db = require("./database");
function userLoggedIn(req) {
  /**
   * Checks if the user is logged in
   * @param req - The request object
   * @returns {boolean} - If the user is logged in
   */
  let is_logged_in = req.session.logged_in || false;
  let is_valid = db.validateUser(req.cookies.token) || false;
  return is_logged_in && is_valid;
}

function getRedirectPath(data) {
  /**
   * Redirects the user to the correct page after authentication
   * @param data - The data from the query
   * @returns {{code: number, url: string}} - The redirect code and url
   * @type {(data: string) => {code: number, url: string}}
   */
  let unauthorized = {
    logged_in: false,
    redirect_url: "/login",
    message: "Unauthorized",
  };
  let forbidden = {
    logged_in: false,
    redirect_url: "/forbidden",
    message: "Forbidden",
  };
  let employee = {
    logged_in: true,
    redirect_url: "/edugear",
    message: "Employee",
  };
  let student = {
    logged_in: true,
    redirect_url: "/register",
    message: "Student",
  };
  let unknown = {
    logged_in: false,
    redirect_url: "/unknown_error",
    message: "Unknown",
  };

  if (data === undefined) {
    return unauthorized;
  }

  // This might not be needed.
  /*if (clientInfo.groups["eduOrgLegalName"] !== secrets.OrgLegalName) {
    return forbidden;
  }*/

  // Use switch case instead
  switch (data["ext_info"]["eduPersonPrimaryAffiliation"]) {
    case "student":
      return student;
    case "employee":
      return employee;
  }

  return unknown;
}

module.exports = {
  getRedirectPath,
  userLoggedIn,
};
