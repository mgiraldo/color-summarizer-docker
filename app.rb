require 'sinatra'
require "sinatra/json"
require 'open3'

get '/:format?' do
  # url = params['url']
  output = ""
  Open3.popen3("perl -X /usr/src/app/bin/colorsummarizer img/ferns-100.jpg -width 50 -json
") {|i,o,e,t|
    output = output + o.read.chomp
  }
  json JSON.parse(output)
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end
