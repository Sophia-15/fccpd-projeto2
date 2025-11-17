FROM alpine:3.19

RUN apk add --no-cache curl bash python3

COPY client.sh /client.sh

RUN chmod +x /client.sh

CMD ["/client.sh"]
