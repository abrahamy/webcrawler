#!/usr/bin/env bash
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018

set -x

clean_build() {
    '''Cleanup old build artefacts'''
    local unneeded=(api_logs media_store data)
    for build_dir in $unneeded
	do
		if [[ -d "$build_dir" ]]; then
			rm -rf "$build_dir"
		fi
	done

    local dc_conf="docker-compose.yml"
    if [[ -f "$dc_conf" ]]; then
        rm -f "$dc_conf"
    fi
}

build_containers() {
    local new_password="$(pwgen 24 1)"
    local placeholder="MySuperSecretPassword"

    sed s/$placeholder/$new_password/g <docker-compose.sample.yml >docker-compose.yml
    
    docker-compose build
}

clean_build
build_containers

