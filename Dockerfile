FROM python:3.7

ENV APP_HOME /usr/src/app

RUN mkdir -p ${APP_HOME}

WORKDIR ${APP_HOME}

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY colorsummarizer-0.77 ${APP_HOME}

# install cpanminus because less verbose
RUN curl -L https://cpanmin.us | perl - App::cpanminus

# install color summarizer dependencies
RUN cpanm Config::General
RUN cpanm Math::VecStat
RUN cpanm Math::Round
RUN cpanm Statistics::Descriptive
RUN cpanm Statistics::Distributions
RUN cpanm Statistics::Basic 
RUN cpanm SVG
RUN cpanm Graphics::ColorNames::HTML
RUN cpanm Graphics::ColorNames::Windows
RUN cpanm Graphics::ColorNames::Netscape
RUN cpanm Graphics::ColorObject
RUN cpanm JSON::XS
RUN cpanm Algorithm::Cluster
RUN cpanm Imager

ADD . ${APP_HOME}
