FROM python:3.6-alpine

ENV TM_HOME /talentmap
RUN mkdir ${TM_HOME}
WORKDIR ${TM_HOME}
ADD . ${TM_HOME}

# uWSGI will listen on this port
EXPOSE 8000

RUN chmod +x ${TM_HOME}/entrypoint.sh
RUN chmod +x ${TM_HOME}/build.sh

RUN apk add --update bash
ENTRYPOINT ["${TM_HOME}/entrypoint.sh"]
