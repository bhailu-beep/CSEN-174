FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /usr/local/bin/run.sh
RUN sed -i 's/\r$//' /usr/local/bin/run.sh \
    && chmod 755 /usr/local/bin/run.sh

ENV HOME=/tmp \
    TMPDIR=/tmp

USER nobody
WORKDIR /tmp
ENTRYPOINT ["/usr/local/bin/run.sh"]
