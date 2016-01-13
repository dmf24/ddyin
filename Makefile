MKDIR_P = mkdir -p

BUILD_DIR = build

BUILD_INV = ${BUILD_DIR}/inventory
BUILD_GV = ${BUILD_INV}/group_vars
BUILD_HV = ${BUILD_INV}/host_vars

INV_DIRS = ${BUILD_DIR} ${BUILD_INV} ${BUILD_HV} ${BUILD_GV}

BUILD_DIRS = ${BUILD_DIR} ${BUILD_INV} ${BUILD_HV} ${BUILD_GV}

INSTALL_DIR = ${HOME}/opt/ddyin-inventory

SAMPLE_DIR = build-sample
SAMPLE_INV = ${SAMPLE_DIR}/inventory
SAMPLE_GV = ${SAMPLE_INV}/group_vars
SAMPLE_HV = ${SAMPLE_INV}/host_vars

.PHONY: directories

all: executable default-config inventory

inventory: ${BUILD_INV} ${BUILD_HV} ${BUILD_GV} ${BUILD_INV}/groups_by_host.yml ${BUILD_INV}/raw.yml

sample: ${SAMPLE_DIR}/ddyin ${SAMPLE_INV} ${SAMPLE_HV} ${SAMPLE_GV} ${SAMPLE_INV}/groups_by_host.yml ${SAMPLE_INV}/raw.yml ${SAMPLE_GV}/localgroup ${SAMPLE_HV}/localhost

${BUILD_INV}/groups_by_host.yml:
	echo '---' > $@

${BUILD_INV}/raw.yml:
	echo '---' > $@

${BUILD_INV}:
	${MKDIR_P} $@

${BUILD_HV}:
	${MKDIR_P} $@

${BUILD_GV}:
	${MKDIR_P} $@

default-config: ${BUILD_DIR} ${BUILD_DIR}/ddyin-config.yml

${BUILD_DIR}/ddyin-config.yml: source/config-templates/ddyin-config.yml/default
	cp source/config-templates/ddyin-config.yml/default $@

executable: ${BUILD_DIR} ${BUILD_DIR}/ddyin

${BUILD_DIR}/ddyin: source/ddyin.py
	cp source/ddyin.py ${BUILD_DIR}/ddyin
	chmod 755 ${BUILD_DIR}/ddyin

${SAMPLE_DIR}/ddyin: source/ddyin.py
	cp source/ddyin.py $@
	chmod 755 $@

${SAMPLE_INV}/groups_by_host.yml:
	cp source/config-templates/groups_by_host.yml/sample $@

${SAMPLE_INV}/raw.yml:
	echo '---' > $@

${SAMPLE_GV}/localgroup:
	cp source/config-templates/group_vars/localgroup $@

${SAMPLE_HV}/localhost:
	cp source/config-templates/host_vars/localhost $@
