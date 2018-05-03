require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'
require 'ox'

get "/styles.css" do
  send_file("styles/styles.css")
end

get "/image" do
  if File.exist?(temp_file)
    send_file(temp_file)
  else
    halt 404
  end
end

get '/:type?' do
  clusters = 5
  size = 100
  url = params['url']
  pretty = false
  if !validURI?(url)
    halt 400
  end
  type = params['type'] || "json"
  if type.eql?("pretty")
    type = "json"
    pretty = true
  end
  if type.eql?("xmljson")
    type = "xml"
    pretty = true
  end
  open(temp_file, "wb") do |file|
    file << open(url).read
  end
  output = ""
  cmd = "perl -X #{folder}/bin/colorsummarizer -image #{temp_file} -width #{size} -#{type} -stats -histogram -clusters #{clusters}"
  p cmd
  Open3.popen3(cmd) {|i,o,e,t|
    line = o.read.chomp.gsub("#{temp_file}", "").strip
    output = output + line
  }
  hexes = []
  if pretty && type.eql?("json")
    json = JSON.parse(output)
    json["data"].each do |key, hex|
      hexes.push(hex)
    end
  end
  # File.delete(temp_file)
  if !pretty && type.eql?("json")
    headers['Content-Type'] = "application/json"
    json JSON.parse(output)
  elsif type.eql?("text")
    headers['Content-Type'] = "text/plain"
    output
  elsif !pretty && type.eql?("xml")
    headers['Content-Type'] = "text/xml"
    output
  elsif type.eql?("xml")
    headers['Content-Type'] = "application/json"
    json Ox.load(output, mode: :hash)
  elsif pretty
    erb :pretty, :locals => {:url => url, :output => output, :image => temp_filename, :hexes => hexes}
  else
    output
  end
end

def folder
  "/usr/src/app"
end

def temp_file
  "#{folder}/#{temp_filename}"
end

def temp_filename
  "temp.jpg"
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end

