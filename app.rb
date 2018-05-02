require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'

get "/image" do
  send_file(temp_file)
end

get '/:type?' do
  clusters = 4
  size = 100
  url = params['url']
  if !validURI?(url)
    halt 400
  end
  type = params['type'] || "json"
  open(temp_file, "wb") do |file|
    file << open(url).read
  end
  output = ""
  cmd = "perl -X #{folder}/bin/colorsummarizer -image #{temp_file} -width #{size} -#{type} -stats -histogram -clusters #{clusters} -clip transparent,white,black"
  p cmd
  Open3.popen3(cmd) {|i,o,e,t|
    line = o.read.chomp.gsub("#{temp_file}", "").strip
    output = output + line
  }
  # File.delete(temp_file)
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

def folder
  "/usr/src/app"
end

def temp_file
  "#{folder}/temp.jpg"
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end
