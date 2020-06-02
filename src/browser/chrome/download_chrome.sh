#!/usr/bin/bash

DEFAULT_VERSION=81
SPECIFIED_VERSION=$1

LINUX_ZIP=chromedriver_linux64.zip
MAC_ZIP=chromedriver_mac64.zip

version() {
if [ -n "$SPECIFIED_VERSION" ]; then
    echo "You specified: ${SPECIFIED_VERSION}"
    VERSION="$SPECIFIED_VERSION"
  else
    echo "Using Default: ${DEFAULT_VERSION}"
    VERSION="$DEFAULT_VERSION"
  fi
}

get_uname() {
  echo $(uname -s)
}

get_path_last_dir() {
  IFS=':' read -r -a ARRAY <<< "$PATH"
  echo "${ARRAY[$ARRAY_LENGTH]}"
}

find_storage_url() {
  CURR=$(curl https://chromedriver.chromium.org/downloads | grep "Current Releases")
  #CURR=$(cat chrome.html | grep -o "https://chromedriver.storage.googleapis.com/index.html?path=[0-9.]*");
  for url in $(echo "$CURR" | grep -o "https://chromedriver.storage.googleapis.com/index.html?path=[0-9.]*");
  do
    V=$(echo $url | cut -d"=" -f 2);
    MAIN_V=$(echo $V | cut -d"." -f 1);
    if [ "$VERSION" == "$MAIN_V" ]; then
        echo "$V";
        STORAGE_URL="https://chromedriver.storage.googleapis.com/${V}/"
        break
    fi
  done
}

run() {
  U=$(get_uname)
  if [ "$U" == "Linux" ]; then
    ZIP="$LINUX_ZIP";

  elif [ "$U" == "Darwin" ]; then
    ZIP="$MAC_ZIP";

  else
    echo "System not supported"
    exit 2
  fi

  # Define specified Chrome version or use default.
  version

  echo "Downloading Chrome Driver...."
  find_storage_url

  if [ -z ${STORAGE_URL+x} ]; then
    echo "Could not find storage url for specified version" 
    exit 2
  fi

  TARGET="${STORAGE_URL}${ZIP}"
  echo "$TARGET"
  curl --output "$ZIP" "$TARGET"

  # extract
  unzip "$ZIP"

  # copy to final dir in PATH
  COPY_TO=$(get_path_last_dir)
  echo "Copying chromedriver to" "$COPY_TO"
  cp chromedriver "$COPY_TO"
}

run
