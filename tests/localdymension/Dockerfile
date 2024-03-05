# syntax=docker/dockerfile:1

FROM golang:1.19-alpine3.16 as go-builder

WORKDIR /dymesion

COPY go.mod go.sum* ./

RUN go mod download

COPY . .

ENV PACKAGES curl make git tree libc-dev bash gcc linux-headers eudev-dev python3

RUN apk add --no-cache $PACKAGES

RUN make build

FROM alpine:3.16.1

RUN apk add curl jq bash vim 

COPY --from=go-builder /dymesion/build/dymd /usr/local/bin/

WORKDIR /dymension/localnet

EXPOSE 26656
EXPOSE 26657
EXPOSE 1317
EXPOSE 9090

COPY ./tests/localdymension/init.sh .
COPY ./tests/localdymension/start.sh .
COPY scripts/* ./scripts/
RUN chmod +x start.sh
RUN chmod +x init.sh
RUN chmod +x ./scripts/*.sh

# ENTRYPOINT ["/dymension/localnet/start.sh"] 