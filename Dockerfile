FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y \
            python-dev \
            python-pip \
	    nodejs \
	    npm \
	    xvfb \
	    git \
	    libfontconfig1 && \
    apt-get clean -q && \
    rm -rf  /tmp/* /var/tmp/* /var/lib/apt/lists/* && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    npm install -g phantomjs-prebuilt bower && \
    pip install --upgrade pip

RUN pip install \
            behave==1.2.5 \
            pyhamcrest==1.8.1 \
            splinter \
	    Flask \
	    kazoo \
	    requests && \
    mkdir /houses

WORKDIR /houses

ADD app/bower.json /houses/app/
ADD app/.bowerrc /houses/app/

RUN cd app && \
    bower install --allow-root

ADD . /houses

ENTRYPOINT [ "python", "main.py" ]
CMD [ "test" ]
