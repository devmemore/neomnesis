FROM alpine:3.6 

RUN apk update && apk upgrade && apk add bash
RUN apk add wget
RUN apk add ca-certificates
RUN apk add g++ 
RUN apk add gcc 
RUN apk add make 
RUN apk add tar 

WORKDIR /webservices
 
RUN mkdir -p /webservices/neomnsesis 

COPY neomnesis /webservices/neomnesis/neomnsesis,
COPY scripts /webservices/neomnesis/scripts

RUN /bin/bash /webservices/neomnesis/scripts/launch_app_for_docker.sh



