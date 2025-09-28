FROM python:3.10

# Setup Timezone
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ='Europe/Oslo'
RUN apt-get update && apt-get install -y tzdata git
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Global settings
ENV MIN_DAYS='1'
ENV MAX_DAYS='90'
ENV MIN_LABELS='0'
ENV MAX_LABELS='10'
ENV SECRET_KEY='SuperSecretKeyHere'

# FEIDE OAuth2
ENV FEIDE_REDIRECT_URI='https://<fqdn>/login/feide/callback'
ENV FEIDE_CLIENT_ID=''
ENV FEIDE_CLIENT_SECRET=''

# Label server (https://github.com/VaagenIM/EtikettServer)
ENV LABEL_SERVER='https://<fqdn-label>'

# Teams webhooks (comma separated)
ENV TEAMS_WEBHOOKS=''
ENV TEAMS_WEBHOOKS_DEVIATIONS=''

# Kiosk (Admin access without login) (FQDN)
ENV KIOSK_FQDN=''
ENV KIOSK_SECRET=''

# API token
ENV API_TOKEN=''

# Misc
ENV DEBUG='False'
ENV AUTO_UPDATE='True'
ENV WEB_CONCURRENCY='1'

COPY requirements.txt .
RUN pip install -U pip && pip install setuptools wheel && pip install -r requirements.txt

RUN echo  \
    "cd /FeideUtstyrbase && \
    git pull && \
    pip install -q -r requirements.txt && \
    cp -r /FeideUtstyrbase/BookingSystem/* /app" > /usr/local/bin/auto-update.sh

RUN git clone https://github.com/sondregronas/FeideUtstyrbase

WORKDIR /app
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY BookingSystem /app

EXPOSE 5000
VOLUME /app/data
CMD ["sh", "/usr/local/bin/entrypoint.sh"]
