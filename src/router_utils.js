function getRedirectPath(affiliation) {
  /**
   * Redirects the user to the correct page after authentication
   * @param affiliation - The users affiliation
   * @returns {string} - The path to redirect the user to
   * @type {(affiliation: string) => string}
   */
  switch (affiliation.toLowerCase()) {
    case "student":
      return "/register";
    case "employee":
      return "/register";
  }
  return "/logout";
}

function getUserStatus(req) {
  return {
    logged_in: !!req.session.token,
  };
}

module.exports = {
  getRedirectPath,
  getUserStatus,
};
