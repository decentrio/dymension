# syntax=docker/dockerfile:1

ARG GO_VERSION="1.21"
ARG RUNNER_IMAGE="alpine:3.19"

# --------------------------------------------------------
# Builder
# --------------------------------------------------------

FROM golang:${GO_VERSION}-alpine as builder

COPY . dymension/

RUN apk add --no-cache \
    ca-certificates \
    build-base \
    linux-headers \
    git \
    && rm -rf /var/cache/apk/*

RUN cd dymension/

# Cosmwasm - Download correct libwasmvm version
RUN ARCH=$(uname -m) && WASMVM_VERSION=$(go list -m github.com/CosmWasm/wasmvm | sed 's/.* //') && \
    wget https://github.com/CosmWasm/wasmvm/releases/download/$WASMVM_VERSION/libwasmvm_muslc.$ARCH.a \
        -O /lib/libwasmvm_muslc.a && \
    # verify checksum
    wget https://github.com/CosmWasm/wasmvm/releases/download/$WASMVM_VERSION/checksums.txt -O /tmp/checksums.txt && \
    sha256sum /lib/libwasmvm_muslc.a | grep $(cat /tmp/checksums.txt | grep libwasmvm_muslc.$ARCH | cut -d ' ' -f 1)

# Build dymd binary
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/root/go/pkg/mod \
    go build \
        -mod=readonly \
        -trimpath \
        -tags "netgo,ledger,muslc,osusergo" \
        -ldflags \
            "-X github.com/cosmos/cosmos-sdk/version.Version=${GIT_REF} \
            -X github.com/cosmos/cosmos-sdk/version.Commit=${GIT_COMMIT} \
            -X github.com/cosmos/cosmos-sdk/version.BuildTags=netgo,ledger,muslc \
            -w -s -linkmode=external -extldflags '-Wl,-z,muldefs -static'" \
        -trimpath \
        -o /go/dymension/build/dymd \
        /go/dymension/cmd/dymd/main.go

# --------------------------------------------------------
# Runner
# --------------------------------------------------------

FROM ${RUNNER_IMAGE}

COPY --from=builder /go/dymension/build/dymd /bin/dymd

ENV HOME /dymension
WORKDIR $HOME

# Add opionanted node configuration
# This files are copied at runtime so it is possible to override them

# RUN echo $VALIDATOR_MNEMONIC >> /etc/dymension/mnemonic
# RUN echo $VALIDATOR_ADDRESS > /etc/dymension/address

EXPOSE 26656
EXPOSE 26657
EXPOSE 1317
EXPOSE 9090

COPY ./tests/dymension/start.sh /dymension/start.sh
RUN chmod +x /dymension/start.sh
ENTRYPOINT ["/dymension/start.sh"] 