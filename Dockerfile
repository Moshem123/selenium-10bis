FROM selenium/node-firefox

USER root

RUN apt-get update \
    && apt-get install -y python3-distutils \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3 get-pip.py --user \
    && python3 -m pip install --user selenium \
    && /opt/bin/start-xvfb.sh &