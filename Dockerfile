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

# API token
ENV API_TOKEN=''

# Misc
ENV DEBUG='False'
ENV AUTO_UPDATE='True'
ENV WEB_CONCURRENCY='1'

RUN pip install -U pip && pip install setuptools wheel

RUN git clone https://github.com/sondregronas/FeideUtstyrbase &&  \
    pip install -r /FeideUtstyrbase/requirements.txt &&  \
    mkdir /app &&  \
    cp -r /FeideUtstyrbase/BookingSystem/* /app

RUN echo  \
    "cd /FeideUtstyrbase && \
    git pull && \
    pip install -r requirements.txt && \
    cp -r /FeideUtstyrbase/BookingSystem/* /app" > /usr/local/bin/auto-update.sh

# Entrypoint (Update / run)
RUN echo  \
    "if [ \"\$AUTO_UPDATE\" = \"True\" ]; then \
      echo \"Auto update enabled\" && \
      sh /usr/local/bin/auto-update.sh; \
    else \
      echo \"Auto update disabled (AUTO_UPDATE not True)\"; \
    fi && \
    gunicorn -b 0.0.0.0:5000 app:app" > /usr/local/bin/entrypoint.sh

EXPOSE 5000
WORKDIR /app
VOLUME /app/data
CMD ["sh", "/usr/local/bin/entrypoint.sh"]
