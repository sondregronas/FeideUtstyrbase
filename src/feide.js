let secrets = require("./globals");
let axios = require("axios");

let OAuthURL = `https://auth.dataporten.no/oauth/authorization?client_id=${secrets.client_id}&redirect_uri=${secrets.redirect_uri}&response_type=code&scope=openid`;

async function getFeide(endpoint, token) {
  /**
   * Queries the feide api, returns the response
   * @param endpoint - The endpoint to query
   * @param token - The clients access token
   * @returns {Promise<string>} - The response from the query, undefined if the query fails
   * @type {(endpoint : string, token: string) => Promise<string>}
   */

  let output = undefined;
  let headers = {
    Host: endpoint.split("/")[2],
    Authorization: `Bearer ${token}`,
  };

  await axios
    .get(endpoint, { headers })
    .then((response) => {
      output = response.data;
    })
    .catch((error) => {
      console.log(error);
    });
  return output;
}

async function getAccessToken(code) {
  /**
   * Gets the access token from feide using the code from the redirect_uri
   * @param code - The code from the redirect_uri, used to get the access token
   * @returns {Promise<string>} - The access token, undefined if the query fails
   * @type {(code: string) => Promise<string>}
   */

  let url = `https://auth.dataporten.no/oauth/token`;

  let headers = {
    Host: "auth.dataporten.no",
    Authorization: `Basic ${secrets.basic}`,
    "Content-Type": "application/x-www-form-urlencoded",
  };
  let body = `grant_type=authorization_code&code=${code}&client_id=${secrets.client_id}&redirect_uri=${secrets.redirect_uri}`;

  let token = undefined;

  await axios
    .post(url, body, { headers })
    .then((response) => {
      token = response.data["access_token"] || undefined;
    })
    .catch((error) => {
      console.log(error);
    });

  return token;
}

async function getClientInfo(token) {
  /**
   * Gets the clients info from feide using openid, the users extended info & groups
   * @param token - The clients access token
   * @returns {Promise<object>} - The clients info, undefined if the query fails
   * @type {(token: string) => Promise<object>}
   */

  let openid_ep = "https://auth.dataporten.no/openid/userinfo";
  let ext_ep = "https://api.dataporten.no/userinfo/v1/userinfo";
  let groups_ep = "https://groups-api.dataporten.no/groups/me/groups";

  let openid = await getFeide(openid_ep, token);
  let ext_info = await getFeide(ext_ep, token);
  let groups = await getFeide(groups_ep, token);

  if (openid && ext_info && groups) {
    return {
      openid,
      ext_info,
      groups,
    };
  }

  return undefined;
}

module.exports = {
  OAuthURL,
  getAccessToken,
  getClientInfo,
};
