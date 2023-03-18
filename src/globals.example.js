// TODO: Move to .env / docker secrets
const crypto = require("crypto");
const secrets = require("./globals");

const hash = (text) => {
  /**
   * Hashes the users openid data
   * @param text - The text to hash
   * @returns {string} - The hashed openid data
   */
  let salt = "R@nd0mStr1ng"; // This adds a layer of security to the hashing algorithm

  let salted = text + salt + text.split("").reverse().join("");
  let hash = crypto.createHash("sha256");

  hash.update(salted);
  return hash.digest("hex");
};

const client_id = "https://dashboard.dataporten.no/";
const client_secret = "https://dashboard.dataporten.no/";
const redirect_uri = "http://localhost:3000/auth";
const session_secret = hash("R@nd0mStr1ng"); // This is a random string, be sure to have it be obscure and unique! (The longer and more obscure the better)
const devmode = false;

const kiosk_enabled = false;
const kiosk_username = "kiosk";
const kiosk_password = hash("kiosk");

const mail_user = "";
let mail_password = "";

const transporter_options = {
  host: "send.example.com",
  port: 465,
  secure: true,
  auth: {
    user: mail_user,
    pass: mail_password,
  },
};

module.exports = {
  client_id,
  basic: Buffer.from(`${client_id}:${client_secret}`).toString("base64"),
  redirect_uri,
  session_secret,
  devmode,
  transporter_options,
  mail_user,
  hash,
  kiosk_username,
  kiosk_password,
  kiosk_enabled,
};
