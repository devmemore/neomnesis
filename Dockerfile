FROM alpine:3.6 

RUN apk update && apk upgrade && apk add bash
RUN apk add wget
RUN apk add ca-certificates
RUN apk add g++ 
RUN apk add gcc 
RUN apk add make 
RUN apk add tar 
 
RUN mkdir -p /usr/local/neomnsesis 

COPY neomnesis /usr/local/neomnesis/neomnsesis,
COPY scripts /usr/local/neomnesis/scripts

RUN /bin/bash /usr/local/neomnesis/scripts/launch_app_for_docker.sh



