import datetime
import json
import os
from pony import orm

db = orm.Database()

class Summary(db.Entity):
    id = orm.PrimaryKey(str)
    data = orm.Required(str)
    date = orm.Required(datetime.date)

class Article(db.Entity):
    id = orm.PrimaryKey(str)
    data = orm.Required(str)
    date = orm.Required(datetime.date)


class DatabaseManager:
    '''Populates local ElasticSearch database with JORF
    summaries and articles.'''

    def __init__(self, overwriteIndices=False, sqliteFile="db.sqlite", verbose=False):
        '''Initiates database manager with a connexion to the
        local running ElasticSearch instance.'''

        db.bind(provider="sqlite", filename=sqliteFile, create_db=True)
        self.verbose = verbose
        if overwriteIndices:
            self.deleteIndices()

    def deleteIndices(self):
        '''Deletes used indices in ES.'''

        if self.verbose:
            print('Deleting indices...')

        raise NotImplementedError("Delete the sqlite file instead")
        #self.es.indices.delete(index='summary', ignore=[400, 404])
        #self.es.indices.delete(index='article', ignore=[400, 404])

    def initESIndexes(self):
        '''Creates indices in ES, as well as their respective mappings.'''

        if self.verbose:
            print('Creating indices...')
        db.generate_mapping(create_tables=True)

    def initESIndexes_backup(self):
        '''Creates indices in ES, as well as their respective mappings.'''

        if self.verbose:
            print('Creating indices...')

        # Initate summary ES index
        self.es.indices.create(index='summary', ignore=400)
        self.es.indices.put_mapping(index='summary',
            doc_type='nodes',
            body={
                "properties": {
                    "DATE_PUBLI": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "ID": {
                        "type": "keyword"
                    },
                    "STRUCTURE_TXT": {
                        "type": "object",
                        "enabled": False
                    }
                }
            }
        )

        # Initiate article ES index
        self.es.indices.create(index='article', ignore=400)
        self.es.indices.close(index='article')
        self.es.indices.put_settings(index='article',
            body={
                "analysis": {
                    "analyzer": {
                        "htmlStripAnalyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["standard", "lowercase"],
                            "char_filter": [
                                "html_strip"
                            ]
                        }
                    }
                }
            }
        )
        self.es.indices.put_mapping(index='article', doc_type='nodes',
            body={
                "properties": {
                    "DATE_PUBLI": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "ID": {
                        "type": "keyword"
                    },
                    "STRUCT": {
                        "type": "object",
                        "properties": {
                            "articles": {
                                "type": "nested",
                                "properties": {
                                    "BLOC_TEXTUEL": {
                                        "type": "text",
                                        "analyzer": "htmlStripAnalyzer"
                                    }
                                }
                            },
                            "signataires": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        )
        self.es.indices.open(index='article')

    def addSummary(self, nodeData, documentId=None):
        try:
            with orm.db_session:
                datepubli = datetime.date.fromisoformat(json.loads(nodeData)['DATE_PUBLI'])
                Summary(id=documentId, data=nodeData, date=datepubli)
        except Exception as e:
            with open('./logs.txt', 'a+') as logFile:
                logFile.write('{} - {}'.format(str(datetime.datetime.now()), e))

    def addArticle(self, nodeData, documentId=None):
        try:
            with orm.db_session:
                datepubli = datetime.date.fromisoformat(json.loads(nodeData)['DATE_PUBLI'])
                Article(id=documentId, data=nodeData, date=datepubli)
        except Exception as e:
            with open('./logs.txt', 'a+') as logFile:
                logFile.write('{} - {}'.format(str(datetime.datetime.now()), e))
