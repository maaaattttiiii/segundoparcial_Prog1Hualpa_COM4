# Parcial 2 - Persistencia Avanzada (NBA)

##  Descripción
Este proyecto implementa un **sistema de persistencia avanzada** en Python que utiliza una **estructura jerárquica de tres niveles** basada en el sistema de archivos.  
La jerarquía representa la organización de la **NBA**:  
- Nivel 1 → nba(carpeta principal)  
- Nivel 2 → conferencia(Este u Oeste)  
- Nivel 3 → equipo(por ejemplo, `los_angeles_lakers`)  

Cada equipo contiene un archivo CSV (`players.csv`) con los **jugadores registrados**, sus estadísticas y algo mas de información.  

El sistema permite **crear, leer, actualizar y eliminar jugadores**, además de calcular **estadísticas** de toda la NBA.

##  Estructura Jerárquica

ejemplo con algunos equipos...
data/
└── nba/
├── este/
│ ├── boston_celtics/
│ │ └── players.csv
│ └── miami_heat/
│ └── players.csv
└── oeste/
├── los_angeles_lakers/
│ └── players.csv
└── golden_state_warriors/
└── players.csv

