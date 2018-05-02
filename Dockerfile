FROM ruby:2.3

ENV APP_HOME /usr/src/app
ENV RACK_ENV production
ENV MAIN_APP_FILE app.rb

RUN mkdir -p ${APP_HOME}

COPY colorsummarizer-0.77 ${APP_HOME}

WORKDIR ${APP_HOME}

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
RUN cpanm Graphics::ColorObject
RUN cpanm JSON::XS
RUN cpanm Algorithm::Cluster
RUN cpanm Imager

# install sinatra app stuff
ADD Gemfile ${APP_HOME}
RUN bundle install
ADD Gemfile.lock ${APP_HOME}
ADD app.rb ${APP_HOME}
