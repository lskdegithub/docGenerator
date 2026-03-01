FROM texlive/texlive:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    coreutils \
    findutils \
    gawk \
    grep \
    sed \
    tzdata \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-core \
    fonts-texgyre \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages pyyaml

RUN fc-cache -f

WORKDIR /workspace

CMD ["bash"]
