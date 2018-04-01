#!/usr/bin/env bash
set -x

clean_build() {
    '''Cleanup old build artefacts'''
    local unneeded=(api_logs scrapy_logs mariadb_data)
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
    
    docker-compose --project-name '' build
}

clean_build
build_containers

