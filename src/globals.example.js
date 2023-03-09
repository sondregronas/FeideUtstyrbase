const client_id = "https://dashboard.dataporten.no/";
const client_secret = "https://dashboard.dataporten.no/";
const basic = Buffer.from(`${client_id}:${client_secret}`).toString("base64");
const redirect_uri = "http://localhost:3000/auth";

module.exports = {
  client_id,
  basic,
  redirect_uri,
};
