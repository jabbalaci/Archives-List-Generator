#!/usr/bin/env python

# Author:      Laszlo Szathmary (jabba.laci@gmail.com)
# Last update: 2011-03-27 (yyyy-mm-dd)
# Version:     0.2.1
#
# For more info, see the README file.

import xmlrpclib
import sys
import string
import re
import urllib
import datetime
import unicodedata
import getpass

#BLOG_NAME = 'ubuntuincident'
BLOG_NAME = 'pythonadventures'
BLOG_URL = "https://%s.wordpress.com" % BLOG_NAME
TOOLTIP_INNER = 'on %s' % BLOG_NAME
TAG_URL = BLOG_URL + '/' + 'tag'
WP_TAG_URL = 'https://en.wordpress.com/tag'   # global tags on WP.com
WP_TAGS = True   # Put a link to global tags? Default: yes.
TOOLTIP_GLOBAL = 'on wordpress.com'
USER_NAME = 'ubuntuincident'
sys.stderr.write(BLOG_URL + "\n")
USER_PASSWORD = getpass.getpass("%s password: " % USER_NAME)
LIMIT = 10000000    # should be enough
#LIMIT = 6

#############################################################################

def get_posts():
    server = xmlrpclib.ServerProxy(BLOG_URL + '/' + 'xmlrpc.php')
    return server.metaWeblog.getRecentPosts(BLOG_NAME, USER_NAME, USER_PASSWORD, LIMIT)

def get_date(dateCreated):
    s = str(dateCreated)
    result = re.search(r'^(\d{4})(\d{2})(\d{2}).*$', s)
    return "%s-%s-%s" % ( result.group(1), result.group(2), result.group(3) )

def extract_data(post):
    data = {}

    title = post['title']
    try:
        # if the title is a unicode string, normalize it
        title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
    except TypeError:
        # if it was not a unicode string => OK, do nothing
        pass

    data['title'] = title
    data['link'] = post['link']
    data['categories'] = post['categories']
    data['tags'] = map(string.strip, post['mt_keywords'].split(','))
    if len(data['tags']) == 1 and data['tags'][0] == "":
        data['tags'] = []
    data['date'] = get_date(post['dateCreated'])
    data['status'] = post['post_status']

    return data
# extract_data(post)

def simplify(tag):
    tag = tag.lower()
    tag = tag.replace(' ', '-')
    return urllib.quote(tag)

def get_tags_with_links(tags):
    # tags is a list of tags
    sb = []
    for i, tag in enumerate(tags):
        if (i > 0):
            sb.append(", ")
        inner_link = "<a href=\"%s\" style=\"text-decoration:none;\" title=\"%s\">%s</a>" % \
            ( TAG_URL + '/' + simplify(tag), TOOLTIP_INNER, tag )
        sb.append( inner_link )
        if WP_TAGS:
            global_link = "&nbsp;<a href=\"%s\" style=\"text-decoration:none;\" title=\"%s\""">[x]</a>" % \
                ( WP_TAG_URL + '/' + simplify(tag), TOOLTIP_GLOBAL )
            sb.append( global_link )

    return ''.join(sb)

def convert_to_html(data):
    sb = []
    sb.append("<a href=\"%s\">%s</a>" % (data['link'], data['title']))
    sb.append("&nbsp;&nbsp;<sub>(%s)&nbsp;" % data['date'])
    if len(data['categories']) > 0:
        sb.append(get_tags_with_links(data['categories']))
    if len(data['tags']) > 0:
        sb.append('&nbsp;<b>;</b>&nbsp;')
        sb.append(get_tags_with_links(data['tags']))
    sb.append("</sub>")
    return ''.join(sb)

def get_header():
    now = datetime.datetime.now()
    return "<p><sub>Last update: %s.</sub></p>" % now.strftime("%Y-%m-%d @ %Hh%M")

def get_number_of_posts(public_posts, private_posts):
    return "<p>Number of posts: %d public (%d private).</p>" % (public_posts, private_posts)

#
# If you use this script on your blog, I ask you to leave this footer unchanged.
#
def get_footer():
    return "<p><sub>This page was generated with Jabba Laci's <a href=\"%s\"><i>Archives List Generator</i></a>. \
Feel free to use it on your blog.</sub></p>" % \
"http://ubuntuincident.wordpress.com/2011/02/23/archives-list-generator/"

#############################################################################

posts = get_posts()
public_posts = 0
private_posts = 0

if len(posts) > 0:
    print get_header()
    print "<ol>"
    for post in posts:
        data = extract_data(post)
#        if data['title'] != "Intro":
#            continue
        if data['status'] == 'private':
            private_posts += 1
            # do nothing else
        elif data['status'] == 'publish':
            public_posts += 1
            if public_posts == 6:
                print '<!--more-->'
            sys.stdout.write("<li>")
            sys.stdout.write( convert_to_html(data) )
            sys.stdout.write("</li>")
            print
    print "</ol>"
    print get_number_of_posts(public_posts,  private_posts)
    print get_footer()
