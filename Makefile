MKDIR_P = mkdir -p

BUILD_DIR = build

BUILD_INV = ${BUILD_DIR}/inventory
BUILD_GV = ${BUILD_INV}/group_vars
BUILD_HV = ${BUILD_INV}/host_vars

INV_DIRS = ${BUILD_DIR} ${BUILD_INV} ${BUILD_HV} ${BUILD_GV}

BUILD_DIRS = ${BUILD_DIR} ${BUILD_INV} ${BUILD_HV} ${BUILD_GV}

INSTALL_DIR = ${HOME}/opt/ddyin-inventory

.PHONY: directories

all: executable default-config inventory

inventory: ${BUILD_INV}  ${BUILD_HV} ${BUILD_GV} ${BUILD_INV}/groups_by_host.yml ${BUILD_INV}/raw.yml

${BUILD_INV}/groups_by_host.yml:
	echo '---' > $@

${BUILD_INV}/raw.yml:
	echo '---' > $@

${BUILD_DIR}:
	${MKDIR_P} $@

default-config: ${BUILD_DIR} ${BUILD_DIR}/ddyin-config.yml

${BUILD_DIR}/ddyin-config.yml:
	cp source/config-templates/ddyin-config.yml/default $@

executable: ${BUILD_DIR} ${BUILD_DIR}/ddyin

${BUILD_DIR}/ddyin:
	cp source/ddyin.py ${BUILD_DIR}/ddyin
	chmod 755 ${BUILD_DIR}/ddyin
