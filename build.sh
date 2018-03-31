#!/usr/bin/env bash
set -x

export MYSQL_PASSWORD=$(pwgen 24 1)

clean_build() {
    '''Cleanup old build artefacts'''
    local unneeded=(api_logs mariadb_data redis_data scrapyd)
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

clean_build

mkdir scrapyd
cp scrapyd_Dockerfile scrapyd/Dockerfile

cp docker-compose.sample.yml docker-compose.yml

docker-compose --project-name '' build