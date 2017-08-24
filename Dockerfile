#FROM ubuntu:14.04
FROM gcr.io/tensorflow/tensorflow:latest-gpu

MAINTAINER Sujoy Roy <sujoy.roy@sap.com>

ENV http_proxy=http://proxy:8080
ENV HTTP_PROXY=http://proxy:8080
ENV https_proxy=https://proxy:8080
ENV HTTPS_PROXY=https://proxy:8080
ENV ftp_proxy=ftp://proxy:8080
ENV FTP_PROXY=ftp://proxy:8080

RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        git \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python-dev \
        python-numpy \
        python-pip \
        software-properties-common \
        swig \
        zip \
        zlib1g-dev \
        libcurl3-dev \
        vim \
        python-tk \
        python-opencv \
        protobuf-compiler \
        python-pil \
        python-lxml \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Set up grpc

RUN pip install enum34 futures mock six && \
    pip install --pre 'protobuf>=3.0.0a3' && \
    pip install -i https://testpypi.python.org/simple --pre grpcio && \
    pip install matplotlib pillow lxml

# Set up cuda requirements
# these directories are created by the shell script run before docker build

#COPY cuda /usr/local/cuda
#COPY lib /usr/lib

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/targets/x86_64-linux/lib"

ENV CUDA_HOME=/usr/local/cuda

ENV TF_NEED_CUDA=1
ENV GCC_HOST_COMPILER_PATH=/usr/bin/gcc
ENV TF_CUDA_VERSION=8.0
ENV CUDA_TOOLKIT_PATH=/usr/local/cuda
ENV TF_CUDNN_VERSION=5.1.10
ENV CUDNN_INSTALL_PATH=/usr/local/cuda
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.7,5.2,6.0
ENV CC_OPT_FLAGS="--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.2 --config=cuda"
ENV PYTHON_BIN_PATH="/usr/bin/python"
ENV USE_DEFAULT_PYTHON_LIB_PATH=1
ENV TF_NEED_JEMALLOC=1
ENV TF_NEED_GCP=0
ENV TF_NEED_HDFS=0
ENV TF_ENABLE_XLA=0
ENV TF_NEED_OPENCL=0

RUN pip install Pillow h5py easydict

# Set up Bazel.

# We need to add a custom PPA to pick up JDK8, since trusty doesn't
# have an openjdk8 backport.  openjdk-r is maintained by a reliable contributor:
# Matthias Klose (https://launchpad.net/~doko).  It will do until
# we either update the base image beyond 14.04 or openjdk-8 is
# finally backported to trusty; see e.g.
#   https://bugs.launchpad.net/trusty-backports/+bug/1368094
RUN add-apt-repository -y ppa:openjdk-r/ppa && \
    apt-get update && \
    apt-get install -y openjdk-8-jdk openjdk-8-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Running bazel inside a `docker build` command causes trouble, cf:
#   https://github.com/bazelbuild/bazel/issues/134
# The easiest solution is to set up a bazelrc file forcing --batch.
RUN echo "startup --batch" >>/root/.bazelrc
# Similarly, we need to workaround sandboxing issues:
#   https://github.com/bazelbuild/bazel/issues/418
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone" \
    >>/root/.bazelrc
ENV BAZELRC /root/.bazelrc
# Install the most recent bazel release.
ENV BAZEL_VERSION 0.5.2
WORKDIR /
RUN mkdir /bazel && \
    cd /bazel && \
    curl -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -fSsL -o /bazel/LICENSE.txt https://github.com/bazelbuild/bazel/blob/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

CMD ["/bin/bash"]

