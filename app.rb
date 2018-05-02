require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'

get '/:format?' do
  temp_file = "temp.jpg"
  url = params['url']
  open(temp_file, "wb") do |file|
    file << open(url).read
  end
  output = ""
  Open3.popen3("perl -X /usr/src/app/bin/colorsummarizer -image /usr/src/app/#{temp_file} -json
") {|i,o,e,t|
    output = output + o.read.chomp
  }
  File.delete(temp_file)
  json JSON.parse(output)
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end
