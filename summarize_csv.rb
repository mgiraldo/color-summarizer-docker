#!/usr/bin/env ruby
require 'csv'
require 'optparse'
require 'rbconfig'

THIS_DIR = File.expand_path(File.dirname(__FILE__))
RUBY = File.join(RbConfig::CONFIG['bindir'], RbConfig::CONFIG['ruby_install_name'])


Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8

options = {}

optparse = OptionParser.new do |opts|
  opts.banner = "USAGE: summarize_csv.rb -f /path/to/file.csv -o /path/to/images -d /path/to/output/folder"

  opts.on("-f", "--file FILE", "CSV file") do |f|
    options[:csv] = f
  end

  opts.on("-o", "--origin_folder ORIGIN_FOLDER", "Folder where images are located") do |o|
    options[:origin] = o
  end

  opts.on("-d", "--destination DESTINATION", "Destination folder") do |d|
    options[:destination] = d
  end

  opts.on("-p", "--processes NUM_PROCESSES", "Num of CPU processes to use (default 16)") do |d|
    options[:cpu] = d
  end

  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
end

begin
  optparse.parse!
  mandatory = [:csv, :origin, :destination]
  missing = mandatory.select{ |param| options[param].nil? }
  unless missing.empty?
    raise OptionParser::MissingArgument.new(missing.join(', '))
  end
rescue OptionParser::InvalidOption, OptionParser::MissingArgument
  puts $!.to_s
  puts optparse
  exit
end

CPU = options[:cpu] || 16
csv_file = options[:csv]
origin = options[:origin]
destination = options[:destination]

if !File.file?(csv_file)
  puts "File #{csv_file} does not exist."
  exit
end  

if !File.directory?(destination)
  puts "Directory #{destination} does not exist."
  exit
end

data = CSV.parse(File.read(csv_file), headers: true)

count = data.length

group_size = (count / CPU).ceil + 1

groups = data.each_slice(group_size).to_a

threads = []

groups.each do |g|
  len = g.length
  threads << Thread.new do
    len.times do |i|
      item = g[i]
      if (!item["file_key"].nil? && !item["access_pid"].nil?)
        file_key = item["file_key"].gsub(/"/, '')
        access_pid = item["access_pid"].gsub(/"/, '')
        image = "#{origin}/#{file_key}"
        json = "#{destination}/#{access_pid}.json"
        system(RUBY, "#{THIS_DIR}/summarize_file.rb", "-i", image, "-d", json)
      end
    end
  end
  threads.map(&:join)
end
