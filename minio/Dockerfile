FROM alpine/openssl:latest AS certs

WORKDIR /certs/

RUN openssl ecparam -name secp384r1 -out /tmp/params.pem
RUN openssl req -x509 -newkey ec:/tmp/params.pem -nodes -keyout private.key -out public.crt -days 3653 -subj "/C=RU/ST=Moscow/CN=MINIO"


FROM minio/minio:latest

COPY --from=certs /certs/ /certs/


CMD [ "minio", "-S", "/certs/", "server", "/data/" ]
