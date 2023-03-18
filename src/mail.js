const secrets = require("./globals");

let nodemailer = require("nodemailer");
let transporter = nodemailer.createTransport(secrets.transporter_options);

transporter.verify(function (error, success) {
  if (error) {
    console.log(error);
  } else {
    console.log("Mail server is ready to take our messages");
  }
});

const sendMail = async (to, subject, text) => {
  /**
   * Send an email using the nodemailer transporter specified in globals.js
   * @param to - The email address to send the email to
   * @param subject - The subject of the email
   * @param text - The text of the email (body)
   * @type {{subject, from: string, to, text}}
   */
  let mailOptions = {
    from: secrets.mail_user,
    to: to,
    subject: subject,
    text: text,
  };

  await transporter
    .sendMail(mailOptions)
    .then((info) => {
      console.log(`Message sent: ${info.response}`);
      return;
    })
    .catch((e) => {
      throw e;
    });
};

module.exports = { sendMail };
