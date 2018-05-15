require 'sinatra'
require "sinatra/json"
require 'open3'
require 'open-uri'
require 'ox'

Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8

get "/styles.css" do
  send_file("styles/styles.css")
end

get "/image" do
  if File.exist?(final_file)
    send_file(final_file)
  else
    halt 404
  end
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
  open(temp_file, "wb") do |file|
    file << open(url).read
  end
  convertcmd = "convert #{temp_file} -profile ./profiles/ColorMatchRGB.icc -resize #{size}x PNG24:#{final_file}"
  Open3.popen3(convertcmd) {|i,o,e,t|
  }
  output = ""
  cmd = "perl -X #{folder}/bin/colorsummarizer -image #{final_file} -space lab -width #{size} -#{type} -stats -histogram -clusters #{clusters}"
  p cmd
  Open3.popen3(cmd) {|i,o,e,t|
    line = o.read.chomp.gsub("#{final_file}", "").strip
    output = output + line
  }
  # File.delete(final_file)
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
    erb :pretty, :locals => {:url => url, :output => JSON.pretty_generate(json), :image => temp_filename, :hexes => hexes}
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

def final_file
  "#{folder}/#{final_filename}"
end

def final_filename
  "temp.png"
end

def validURI?(value)
  uri = URI.parse(value)
  uri.is_a?(URI::HTTP) && !uri.host.nil?
rescue URI::InvalidURIError
  false
end

