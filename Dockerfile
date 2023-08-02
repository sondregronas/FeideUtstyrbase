FROM python:3.10

# Setup Timezone
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ='Europe/Oslo'
RUN apt-get update && apt-get install -y tzdata
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# FEIDE OAuth2
ENV FEIDE_REDIRECT_URI='https://<fqdn>/login/feide/callback'
ENV FEIDE_CLIENT_ID=''
ENV FEIDE_CLIENT_SECRET=''

# Label server (https://github.com/VaagenIM/EtikettServer)
ENV LABEL_SERVER='https://<fqdn-label>'

# SMTP
ENV SMTP_SERVER=''
ENV SMTP_PORT='587'
ENV SMTP_USERNAME=''
ENV SMTP_PASSWORD=''
ENV SMTP_FROM='UtstyrBase'

# Kiosk (Admin access without login) (FQDN)
ENV KIOSK_FQDN=''

# Debug mode
ENV DEBUG='False'

WORKDIR /app
COPY requirements.txt requirements.txt
COPY BookingSystem .
RUN pip install -r requirements.txt

VOLUME /app/data
EXPOSE 5000
CMD ["python", "app.py"]

