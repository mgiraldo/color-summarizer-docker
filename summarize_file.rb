#!/usr/bin/env ruby

require 'open3'
require 'ox'
require 'securerandom'
require 'optparse'

Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8

options = {}

optparse = OptionParser.new do |opts|
  opts.banner = "USAGE: summarize_file.rb -i /path/to/some_image.jpg -d /path/to/output.json"

  opts.on("-i", "--image IMAGE", "Image to summarize") do |i|
    options[:image] = i
  end

  opts.on("-d", "--destination DESTINATION", "Destination JSON file") do |d|
    options[:destination] = d
  end

  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
end

begin
  optparse.parse!
  mandatory = [:image, :destination]
  missing = mandatory.select{ |param| options[param].nil? }
  unless missing.empty?
    raise OptionParser::MissingArgument.new(missing.join(', '))
  end
rescue OptionParser::InvalidOption, OptionParser::MissingArgument
  puts $!.to_s
  puts optparse
  exit
end

filename = options[:image]
size=50
clusters=5
uuid = SecureRandom.uuid
final_file_name = "./#{uuid}.png"
folder = "./colorsummarizer-0.77"

if !File.file?(filename)
  puts "File #{filename} does not exist."
  exit
end  

convertcmd = "convert #{filename} -profile ./profiles/ColorMatchRGB.icc -resize #{size}x PNG24:#{final_file_name}"
Open3.popen3(convertcmd) {|i,o,e,t|
}

output = ""
cmd = "perl -X #{folder}/bin/colorsummarizer -conf summarizer.conf -clip transparent -image #{final_file_name} -width #{size} -xml -stats -histogram -clusters #{clusters}"
Open3.popen3(cmd) {|i,o,e,t|
  line = o.read.chomp.gsub("#{final_file_name}", "").strip
  output = output + line
}

File.delete(final_file_name)

open(options[:destination], "wb") do |file|
  file <<  Ox.load(output, mode: :hash)
end
