FROM ubuntu:24.04

# Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc libgbm1 libu2f-udev libvulkan1 libc-dev libffi-dev libpq-dev python3 python3-dev python3-pip fonts-liberation libappindicator3-1 libasound2t64 libatk-bridge2.0-0 libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 curl unzip wget xvfb

# Install Geckodriver and Firefox
RUN GECKODRIVER_VERSION=v0.34.0 && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# Install Chromedriver
RUN CHROMEDRIVER_VERSION=126.0.6478.182 && \
    wget https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /usr/bin && \
    mv /usr/bin/chromedriver-linux64/chromedriver /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver-linux64.zip
    
# Set Display Port
ENV DISPLAY=:99

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

WORKDIR /root/

COPY . .
