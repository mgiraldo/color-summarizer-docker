require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'

get '/:type?' do
  temp_file = "temp.jpg"
  url = params['url']
  type = params['type'] || "json"
  open(temp_file, "wb") do |file|
    file << open(url).read
  end
  output = ""
  cmd = "perl -X /usr/src/app/bin/colorsummarizer -image /usr/src/app/#{temp_file} -#{type} -all"
  p cmd
  Open3.popen3(cmd) {|i,o,e,t|
    line = o.read.chomp.sub("/usr/src/app/#{temp_file}", "").strip
    output = output + line
  }
  File.delete(temp_file)
  if type.eql?("json")
    headers['Content-Type'] = "application/json"
    json JSON.parse(output)
  elsif type.eql?("text")
    headers['Content-Type'] = "text/plain"
    output
  elsif type.eql?("xml")
    headers['Content-Type'] = "text/xml"
    output
  else
    output
  end
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end
