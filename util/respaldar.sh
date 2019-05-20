#!/bin/bash

nombre_respaldo="respaldo_dermatologia_`date +"%Y%m%d_%H%M%S"`.tar.gz"

# ingresa en el directorio
cd dermatologia/principal

# comprime los archivos
tar -zcvf /tmp/${nombre_respaldo} media/ db.sqlite3

#envia los archivos
scp /tmp/${nombre_respaldo} hilda@192.168.0.100:/home/hilda

#elimina el comprimido actual
rm /tmp/${nombre_respaldo}
