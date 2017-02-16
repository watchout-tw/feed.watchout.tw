 #!/usr/bin/python
 # -*- coding: utf-8 -*-

import json
from bson import json_util
from instance import config
import MySQLdb
import datetime
import time
from pytz import timezone
import pytz
from feedgen.feed import FeedGenerator


twTime = timezone('Asia/Taipei')

# Settings
SITEURL = config.URL_SITEURL
FOCUSES_URL = config.URL_FOCUSES
VIDEO_URL = config.URL_VIDEO
PHOTOLINK = config.URL_PHOTOLINK
CATEGORY = config.CATEGORY

FEED_TITLE = config.FEED_TITLE
FEED_SUBTITLE = config.FEED_SUBTITLE
FEED_AUTHOR = config.FEED_AUTHOR
FEED_LOGO = config.FEED_LOGO


def make_rss():
    db = MySQLdb.connect(host=config.DB_HOST,    # your host, usually localhost
                        user=config.DB_USERNAME,         # your username
                        passwd=config.DB_PASSWORD,  # your password
                        db=config.DB_DATABASE,  # name of the data base
                        charset='utf8')
    cur = db.cursor()
    cur.execute(config.DBEXECUTE)
    db_data = cur.fetchall()
    db.close()

    fg = FeedGenerator()
    fg.id(SITEURL)
    fg.title(FEED_TITLE)
    fg.author({'name': FEED_AUTHOR['name'], 'email': FEED_AUTHOR['email']})
    fg.link(href=SITEURL, rel='alternate')
    fg.logo(FEED_LOGO)
    fg.subtitle(FEED_SUBTITLE)
    fg.link(href=SITEURL, rel='self')
    fg.language('zh-tw')

    for item in db_data:
        itemdata = pack_data(item, 'rss')
        fe = fg.add_entry()
        fe.id(itemdata['link'])
        fe.link(href=itemdata['link'], rel='alternate')
        fe.author(name=unicode(itemdata['author']), replace=True)
        fe.title(itemdata['title'])
        fe.description(itemdata['abstract'] + remore_link(itemdata['link']))
        # fe.content(content=remore_link(itemdata['link']),type='CDATA')
        fe.enclosure(url=itemdata['photo_thumb'], length=u'200', type=u'image/jpeg')
        fe.published(twTime.localize(itemdata['publish_date']))
        fe.category(category=CATEGORY, replace=True)
    fg.rss_file('rss.xml')


def make_json():
    db = MySQLdb.connect(host=config.DB_HOST,    # your host, usually localhost
                        user=config.DB_USERNAME,         # your username
                        passwd=config.DB_PASSWORD,  # your password
                        db=config.DB_DATABASE,  # name of the data base
                        charset='utf8')
    cur = db.cursor()
    cur.execute(config.DBEXECUTE)
    datalist = cur.fetchall()
    db.close()

    data_dis = []
    for data in datalist:
      data_dis.append(pack_data(data, 'json'))

    with open('rss.json', 'w') as fp:
        json.dump(data_dis, fp)


def remore_link(link):
    return("<a href='" + link + "'>" + u"（閱讀全文⋯）" + "<a>")


def pack_data(data, option):

    data_item = ""
    d_link = ""
    d_category = ""
    d_publish_date = ""

    if option == 'json':
      d_publish_date = int(time.mktime(data[4].timetuple()))
    else:
      d_publish_date = data[4] + datetime.timedelta(hours=8)

    if data[7] == 'text':
      d_link = FOCUSES_URL + str(data[0])
      d_category = config.CATEGORY_LABLE_F + data[5]
    elif data[7] == 'video':
      d_category = config.CATEGORY_LABLE_V + data[8]
      d_link = VIDEO_URL + str(data[0])

    if data[3] is None:
      photo = ''
    else:
      photo = unicode(PHOTOLINK + str(data[0]) + '/normal_' + data[3])

    data_item = {'id': int(data[0]),
      'title': data[1],
      'abstract': data[2],
      'photo_thumb': photo,
      'publish_date': d_publish_date,
      'category': d_category,
      'author': data[6],
      'link': d_link}

    return data_item


def write_log():

    t = datetime.datetime.now() + datetime.timedelta(hours=8)
    log = {'last_update_itme': str(t)}

    with open('log.json', 'w') as fp:
        json.dump(log, fp)


if __name__ == "__main__":
    print '[System] Start! \n'
    make_rss()
    print '[System] RSS Done!'
    make_json()
    print '[System] JSON Done!'
    write_log()
    print '[System] LOG Done!'
