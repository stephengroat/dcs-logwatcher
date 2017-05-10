FROM ubuntu
RUN apt-get update && apt-get install -y python-pip git-core
RUN git clone https://github.com/stephengroat/dcs-logwatcher
RUN cd dcs-logwatcher && pip install -r requirements.txt && pip install .
CMD /usr/local/bin/dcs-logwatcher
