#!/bin/bash

# Function to parse YAML file
# https://stackoverflow.com/a/21189044
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml "config.yaml")

function cleanup {
  lsof -i tcp:${apis_port} | awk 'NR!=1 {print $2}' | xargs kill
  lsof -i tcp:${web_port} | awk 'NR!=1 {print $2}' | xargs kill
}



echo $apis_port $web_port
(cd apis && bash api.sh -p $apis_port --dev) & (cd web && bash web.sh -p $web_port --dev)

trap cleanup EXIT