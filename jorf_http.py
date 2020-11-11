import yaml, json
import datetime
import argparse
import rfeed
import locale
from dateutil import relativedelta
from bottle import route, run, template, response
from pony import orm

locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

db = orm.Database()
base_url = "" #will be overidden when conf is loaded

class Summary(db.Entity):
    id = orm.PrimaryKey(str)
    data = orm.Required(str)
    date = orm.Required(datetime.date)

class Article(db.Entity):
    id = orm.PrimaryKey(str)
    data = orm.Required(str)
    date = orm.Required(datetime.date)

@route('/')
def hello():
    return "Hello world"

@route('/jorf/<date:re:[0-9]{4}-[0-9]{2}-[0-9]{2}>')
def viewJorfDate(date):
    return template('summary', base_url=base_url, jo=getJorfDate(date))

def getJorfDate(date):
    with orm.db_session:
        jo = Summary.select(lambda s : s.date == datetime.date.fromisoformat(date))[:][0]
    return json.loads(jo.data)


@route('/jorf/<joid:re:JORFCONT[0-9]{12}>')
def viewJorfId(joid):
    return template('summary', base_url=base_url, jo=getJorfDate(date))


def getJorfId(id_jo):
    with orm.db_session:
        jo = Summary[id_jo]
    return json.loads(jo)

@route('/texte/<idtexte:re:JORFTEXT[0-9]{12}>')
def viewTexte(idtexte):
    return template('article', base_url=base_url, txt=getTexte(idtexte))

def getTexte(idTexte):
    with orm.db_session:
        txt = Article[idTexte]
    return json.loads(txt.data)

@route('/rss/rss.xml')
def rssJo():
    NOMBRE_JO = 100
    last_year = datetime.date.today()
    try :
        last_year = last_year.replace(year = last_year.year - 1)
    except ValueError:
        last_year = last_year + (datetime.date(last_year.year - 1, 3, 1) - datetime.date(last_year.year, 3, 1))

    feed_items = []
    with orm.db_session:
        jos = orm.select(s for s in Summary).order_by(lambda: orm.desc(s.date))[:NOMBRE_JO]
        for jo in jos:
            feed_items.append(
                rfeed.Item(
                    title = "Jo du " + jo.date.strftime('%A %e %B %Y'),
                    link = base_url+"/jorf/"+str(jo.date),
                    description = template('summary', base_url=base_url, jo=json.loads(jo.data)),
                    guid = rfeed.Guid(base_url+"/jorf/"+str(jo.date)),
                    pubDate = datetime.datetime(jo.date.year, jo.date.month, jo.date.day, 1, 0, 0)
                )
            )

    feed = rfeed.Feed(
        title = "Journal officiel",
        link = base_url+"/",
        description = "Journal officiel de la république française",
        language = "fr-FR",
        image = rfeed.Image("https://www.legifrance.gouv.fr/contenu/logo-rf", "Journal officiel", base_url+"/"),
        items = feed_items)
    response.content_type =  'application/rss+xml'
    return(feed.rss())

def parcoursJo(base_date, jo_elt, feed_items, rank):
    if not jo_elt["links"]:
        #pas de liens, donc c'est un titre
        print("-"*rank + jo_elt['name'])
        feed_items.append(
            rfeed.Item(
                title = "-"*rank + jo_elt['name'],
                pubDate = datetime.datetime(base_date.year, base_date.month, base_date.day, 1, 0, 0) - datetime.timedelta(minutes=len(feed_items))
            )
        )
    else:
        for link in jo_elt['links']:
            txt = getTexte(link['idtxt'])
            print(link['titre'])
            feed_items.append(
                rfeed.Item(
                    title = link['titre'],
                    link = base_url + "/texte/"+link['idtxt'],
                    pubDate = datetime.datetime(base_date.year, base_date.month, base_date.day, 1, 0, 0) - datetime.timedelta(minutes=len(feed_items)),
                    description = template('article', base_url=base_url, txt=txt)
                )
            )
    for child in jo_elt['children']:
        parcoursJo(base_date, child, feed_items, rank+1)


@route('/rss/rss_today2.xml')
def rssLastJo():
    with orm.db_session:
        jo = orm.select(s for s in Summary).order_by(lambda: orm.desc(s.date))[:1][0]
    jo_date = jo.date
    jo = json.loads(jo.data)
    feed_items = []
    parcoursJo(jo_date, jo['STRUCTURE_TXT']['children'][0], feed_items, 0)

    feed = rfeed.Feed(
        title = jo['TITRE'],
        description = "Dernier JO publié",
        link = base_url+"/jorf/"+jo['ID'],
        pubDate = datetime.datetime(jo_date.year, jo_date.month, jo_date.day, 1, 0, 0),
        items = feed_items
        )
    response.content_type =  'application/rss+xml'
    return(feed.rss())



if __name__ == '__main__':    
    # Read CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('configPath', metavar='configPath',
            help='Path to YML config file')
    parser.add_argument('-v', '--verbose', action='store_true',
            help='Should print information and debug messages')
    args = parser.parse_args()

    verbose = args.verbose

    with open(args.configPath, 'r') as ymlFile:
        params = yaml.load(ymlFile)
        # CONSTANTS
        verbose = args.verbose
        databasePath = params['databasePath']
        base_url = params['baseURL']

    db.bind('sqlite', databasePath)
    db.generate_mapping()
    
    run(host='0.0.0.0', port=2000, debug=True)
