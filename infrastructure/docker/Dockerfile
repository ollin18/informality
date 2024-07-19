FROM ubuntu:22.04
LABEL maintainer="Ollin Demian Langle Chimal <olanglechimal@thinkmd.org>"

ENV refreshed_at 2023-08-29
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt -y install build-essential tzdata locales
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt update -qq
RUN apt -y install software-properties-common dirmngr
RUN apt -y install wget gdal-bin curl sed gawk unzip tar default-jdk grep python3 python3-pip libiconv-hook-dev pandoc pandoc-citeproc gdebi-core parallel

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda
# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN mkdir /data
COPY requirements.txt /data/requirements.txt
RUN conda create --name tmdexpectations
ENV PATH /opt/conda/envs/tmdexpectations/bin:$PATH
RUN /bin/bash -c "source activate tmdexpectations"
RUN pip install -r /data/requirements.txt

CMD ["true"]
