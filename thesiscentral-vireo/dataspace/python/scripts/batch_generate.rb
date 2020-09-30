#!/usr/bin/env ruby

require 'pathname'
require 'pry-byebug'
require 'logger'
require 'open3'

def logger
  @logger ||= begin
                logger = Logger.new(STDOUT)
                logger.level = Logger::INFO
                logger
              end
end

def generate_sip(department_dir_name, spreadsheet)
  logger.info "Processing #{department_dir_name} with #{spreadsheet}..."

  `mkdir -p "export/#{department_dir_name}"`
  `cp "#{spreadsheet}" "export/#{department_dir_name}/ExcelExport.xlsx"`
  `cp "thesiscentral-exports/dspace_packages/#{department_dir_name}.zip" "export/#{department_dir_name}/DSpaceSimpleArchive.zip"`
  `cp export/RestrictionsWithId.xlsx "export/#{department_dir_name}/RestrictionsWithId.xlsx"`
  `cp export/ImportRestrictions.xlsx "export/#{department_dir_name}/ImportRestrictions.xlsx"`
  `cp export/AdditionalPrograms.xlsx "export/#{department_dir_name}/AdditionalPrograms.xlsx"`

  restrict_cmd = <<-BASH
  pipenv run python restrictionsFindIds.py --thesis "export/#{department_dir_name}/ExcelExport.xlsx" --restrictions "export/#{department_dir_name}/RestrictionsWithId.xlsx"
  BASH
  # logger.info "Applying the restrictions..."
  # `#{restrict_cmd}`

  `cd "export/#{department_dir_name}" && unzip DSpaceSimpleArchive.zip; cd -`

  build_sip_cmd = <<-BASH
  pipenv run python enhanceAips.py --thesis "export/#{department_dir_name}/ExcelExport.xlsx" -r "export/#{department_dir_name}/RestrictionsWithId.xlsx" --cover_page export/SeniorThesisCoverPage.pdf --add_certs "export/#{department_dir_name}/AdditionalPrograms.xlsx" --aips "export/#{department_dir_name}" -l INFO
  BASH
  logger.info "Generating the SIP..."
  puts "Please run this in another terminal: #{build_sip_cmd}"
  binding.pry

  Open3.popen2(build_sip_cmd) do |stdin, stdout, status_thread|
    stdout.each_line do |line|
      puts line
    end

    raise "Failed to build the SIP"  unless status_thread.value.success?
  end
  
  sort_sips_cmd = <<-BASH
  pipenv run python sortByStatus.py  --thesis "export/#{department_dir_name}/ExcelExport.xlsx" --aips "export/#{department_dir_name}"
  BASH

  logger.info "Sorting the SIPs..."
  Open3.popen2(sort_sips_cmd) do |stdin, stdout, status_thread|
    stdout.each_line do |line|
      puts line
    end

    raise "Failed to clean the SIP metadata"  unless status_thread.value.success?
  end
  # `#{sort_sips}`

  tar_cmd = <<-BASH
  cd "export/#{department_dir_name}"
  tar \
    --create \
    --file="#{department_dir_name}.tgz" \
    --gzip \
    --verbose \
    --exclude=DSpaceSimpleArchive/ \
    --exclude=DSpaceSimpleArchive.zip \
    --exclude="#{department_dir_name}.tgz" \
    .
  BASH

  logger.info "Compressing the SIP..."
  Open3.popen2(tar_cmd) do |stdin, stdout, status_thread|
    stdout.each_line do |line|
      puts line
    end

    raise "Failed to compess the SIP"  unless status_thread.value.success?
  end

  # `cd "export/#{department_dir_name}" && rm "#{department_dir_name}.tgz" && #{tar_cmd}; cd -`
  # `cd "export/#{department_dir_name}" && #{tar_cmd}`
end

def find_spreadsheet(normal_department_name)
  path_value = File.join(File.dirname(__FILE__), 'thesiscentral-exports', 'metadata', "#{normal_department_name}.xlsx")
  Pathname.new(path_value)
end

def departments
  [
    "Religion",
    "Music",
    "Creative Writing Program",
    "Woodrow Wilson School",
    "Spanish and Portuguese",
    "Sociology",
    "Slavic Languages and Literatures",
    "Psychology",
    "Ops Research and Financial Engineering",
    "Near Eastern Studies",
    "Molecular Biology",
    "Independent Study",
    "History",
    "German"
  ]

  [
    "Sociology",
    "Slavic Languages and Literatures",
    "Psychology"
  ]
end

departments.each do |department|

  normal_name = department.downcase.gsub(' ', '_').gsub('&', 'and')
  spreadsheet_path = find_spreadsheet(normal_name)
  generate_sip(normal_name, spreadsheet_path)
end
