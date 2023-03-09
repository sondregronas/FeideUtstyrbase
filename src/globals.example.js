// TODO: Move to .env / docker secrets

const client_id = "https://dashboard.dataporten.no/";
const client_secret = "https://dashboard.dataporten.no/";
const redirect_uri = "http://localhost:3000/auth";
const session_secret = "R@nd0mStr1ng"; // This is a random string, be sure to have it be obscure and unique! (The longer and more obscure the better)
const salt = "R@nd0mStr1ng";

const hashOpenID = (openid_data) => {
  /**
   * Hashes the users openid data
   * @param openid_data - The users openid data
   * @returns {string} - The hashed openid data
   */
  let crypto = require("crypto");

  // Make the string obscure using data from the openid api and salt (sub, email, name, etc.)
  let str = openid_data.sub + openid_data.name;
  let hash = crypto.createHash("sha256");
  // Make it even more obscure using salt for good measure!
  let salted = str + salt;

  // Hash it!
  hash.update(salted);
  return hash.digest("hex");
};

module.exports = {
  client_id,
  basic: Buffer.from(`${client_id}:${client_secret}`).toString("base64"),
  redirect_uri,
  hash: hashOpenID,
  session_secret,
};
