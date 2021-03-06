# Journal Officieux - Parsing & backend

Le code ci présent a pour but de collecter les données du Journal Officiel
français, de les analyser et de les ajouter à une base de données.

## Docker
```
docker build . -t jorf_rss
```

## Execution/mise a jour de la bdd
```
mkdir -p work/{downloads,logs,xmlstructures}
docker run --rm -ti -v $(realpath work):/mnt jorf python main.py /opt/jorf/config/docker.yml
```

## Execution de l'API web
```
cat config/docker.yml | sed 's/EDIT-THIS-BASEURL/www.hostname.com/' > config/my-docker.yml
docker run -v $(realpath work/db.sqlite):/mnt/db.sqlite:ro -v $(realpath config/my-docker.yml):/opt/jorf/config/docker.yml:ro -p80:80 jorf
```

## Installation

Certaines dépendances Python sont requises pour exécuter les scripts de ce repo,
il suffit d'exécuter la commande suivante pour les installer :
```
pip3 install -r requirements.txt
```

## Exécution du code

* Une instance ElasticSearch (>= 6.0.2) doit être démarrée sur la machine sur laquelle
vous exécutez le code actuel.
* Ensuite, il suffit d'exécuter le commande suivante depuis la racine du repo :
```
python3 main.py config/default.yml
```

Cela aura pour effet de télécharger les données depuis le serveur FTP de la DILA
(Direction de l'Information Légale et Administrative) et de peupler votre
instance Elastic avec ces données.

## Utilitaires

Plusieurs scripts sont disponibles pour explorer les données présentes sur le serveur de la DILA.

### Exploration de la structure XML des fichiers d'une tarball

Le fichier `./utils/exploreXMLStructure.py` génère une arborescence des balises XML des fichiers dans une tarball.
Cela est utile afin de parser les fichiers XML par la suite. Il prend en argument le chemin vers la tarball à explorer,
le nom du ficher d'output (qui est stocké dans un folder dont le chemin est indiqué dans le fichier de config),
le fichier de config lui-même ainsi que la regex qui permet de sélectionner les fichiers lors de l'exploration.
Un nombre limité de regexes est disponible; elles correspondent simplement à des besoin personnels et il est possible
d'en ajouter de nouvelles.

Exemple d'utilisation :
```
python3 utils/exploreXMLStructure.py config/default.yml -i /root/data/LEGI/Freemium_legi_global_20170302-080753.tar.gz -o legi_freemium -r legi_arti -v
```

Un second script est utilisé pour simplifier les résultats obtenus (notamment supprimer les balises HTML qui rendent l'étude du fichier plus fastidieuse).
Exemple d'utilisation :
```
python3 utils/cleanXMLStructure.py -i /root/data/xmlStructures/legi_freemium -o /root/data/xmlStructures/legi_freemium_cleaned
```
