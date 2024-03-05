# syntax=docker/dockerfile:1

ARG GO_VERSION="1.21"
ARG RUNNER_IMAGE="alpine:3.19"

# --------------------------------------------------------
# Builder
# --------------------------------------------------------

FROM golang:${GO_VERSION}-alpine as builder

WORKDIR dymension
COPY . .
RUN go mod download

RUN apk add --no-cache \
    ca-certificates \
    build-base gcc \
    linux-headers \
    git python3 libc-dev jq curl wget \
    tree eudev-dev bash \
    && rm -rf /var/cache/apk/*


# Build dymd binary
RUN make build 

# --------------------------------------------------------
# Runner
# --------------------------------------------------------

FROM ${RUNNER_IMAGE}

COPY --from=builder ./build/dymd /usr/local/bin/

WORKDIR /dymension/localnet

# Add opionanted node configuration
# This files are copied at runtime so it is possible to override them

# RUN echo $VALIDATOR_MNEMONIC >> /etc/dymension/mnemonic
# RUN echo $VALIDATOR_ADDRESS > /etc/dymension/address

EXPOSE 26656
EXPOSE 26657
EXPOSE 1317
EXPOSE 9090

COPY ./tests/localdymension/init.sh .
COPY ./tests/localdymension/start.sh .
RUN chmod +x start.sh
RUN chmod +x init.sh
ENTRYPOINT ["/dymension/localnet/start.sh"] 