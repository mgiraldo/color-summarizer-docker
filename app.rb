require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'
require 'ox'
require 'securerandom'

Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8

get "/styles.css" do
  send_file("assets/styles.css")
end

get '/:type?' do
  clusters = params['clusters'] || 5
  size = params['size'] || 50
  url = params['url']
  pretty = false
  is_json = false
  if !validURI?(url)
    halt 400
  end
  uuid = uuid()
  final_file_name = final_file(uuid)
  temp_file_name = temp_file(uuid)
  type = params['type'] || "json"
  if type.eql?("pretty")
    type = "xml"
    pretty = true
  end
  if type.eql?("json")
    # because real json option only returns the cluster hexes
    type = "xml"
    is_json = true
  end
  open(temp_file_name, "wb") do |file|
    file << open(url).read
  end
  convertcmd = "convert #{temp_file_name} -profile ./profiles/ColorMatchRGB.icc -resize #{size}x PNG24:#{final_file_name}"
  Open3.popen3(convertcmd) {|i,o,e,t|
  }
  output = ""
  cmd = "perl -X #{folder}/bin/colorsummarizer -conf summarizer.conf -clip transparent -image #{final_file_name} -width #{size} -#{type} -stats -histogram -clusters #{clusters}"
  p cmd
  Open3.popen3(cmd) {|i,o,e,t|
    line = o.read.chomp.gsub("#{final_file_name}", "").strip
    output = output + line
  }
  File.delete(final_file_name)
  File.delete(temp_file_name)
  if !pretty && is_json
    headers['Content-Type'] = "application/javascript"
    json Ox.load(output, mode: :hash)
  elsif type.eql?("text")
    headers['Content-Type'] = "text/plain"
    output
  elsif !pretty && type.eql?("xml")
    headers['Content-Type'] = "text/xml"
    output
  elsif pretty
    hexes = []
    json = Ox.load(output, mode: :hash)
    json[:imgdata][1][:clusters][:cluster].each do |cluster|
      hex = cluster[2][:hex][0][:hex]
      hexes.push(hex)
    end
    erb :pretty, :locals => {:url => url, :output => JSON.pretty_generate(json), :hexes => hexes}
  else
    output
  end
end

def folder
  "/usr/src/app"
end

def temp_file(uuid)
  "#{folder}/#{uuid}.jpg"
end

def uuid
  SecureRandom.uuid
end

def final_file(uuid)
  "#{folder}/#{uuid}.png"
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end
