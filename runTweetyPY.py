from bottle import route, request, debug, run, template, redirect
import urllib2
import twURL
import json
import sqlite3
import pickle
import time
from operator import itemgetter



session = {'archive_ID': 1, 'login_credentials': []}


# function to create the side container and all of its associated card/list items.

def create_side_container_component():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    global session
    side_container = ""  # creates empty side_container variable to append various elements to.

    # makes a call to 'get_trending_nothern_ireland' function and assigns returned values to the 'local_trending' variable.
    local_trending = get_trending_northern_ireland()

    # opens the card/card-content tags and contains the current application user and their home timeline link.
    side_container += "<div class='card'>" \
                        "<div class='card-content'>" \
                            "<p><strong>Current User</strong></p>" \
                            "<ul>" \
                                "<li class = 'menuOptions'>" \
                                    "<a href = '/'>" + str(session['login_credentials'][3]) + "'s Timeline </a>" \
                                "</li>" \
                            "</ul><hr>"

    # appends html items to side_container to allow the user to create a new archive to the application.
    side_container += "<p><strong>New Archive</strong></p>" \
                    "<div class='content'>" \
                        "<form method='post' action='/createArchive'>" \
                            "<div class='control'>" \
                                "<input class='input' type='text' name='newArchive' size='15' placeholder='New Archive Name'>" \
                            "</div><br>" \
                            "<div class='control'><button type='submit' class='button is-primary'>Create Archive</button></div>" \
                        "</form>" \
                    "</div><hr>"

    # appends html itmes to side_container to show the user's personal archives created in the application and stored in the database.
    side_container += "<p><strong>My Created Archives</strong></p>"

    # retrieves all archive names and associated user ID's and if none are returned, an info message will be printed to the screen.
    cursor.execute("SELECT DISTINCT archives.id, archives.archive_name FROM archives WHERE "
                   "archives.userID = ? ORDER BY archives.archive_name ASC",
                   (session['login_credentials'][0],))
    created_archives = cursor.fetchall()

    if not created_archives:
        side_container += "<li>No archives found for this user!</li>"
    for archive in created_archives:
        # select query fetches all associated results and is used to show the number of tweets saved to the archive.
        cursor.execute("SELECT tweet FROM tweets WHERE archiveID = ?", (archive[0],))
        result = cursor.fetchall()

        # shows hyperlink to archive and the number of tweets within the archive (found in the results variable)
        side_container += "<a href='/displayArchive/" + str(archive[0]) +"'>"+ archive[1] + " (" + str(len(result)) + ")</a>"
    side_container += "<hr>"


    # appends html items to side_container for the archives shared to the currently active user.
    side_container += "<ul><p><strong>Shared Archives</strong></p>"

    # get all shared archives - names and id
    cursor.execute(
        "SELECT id, archive_name FROM archives "
        "WHERE id = (SELECT archiveID FROM archiveUsers WHERE sharedUserID = ?)"
        "ORDER BY archive_name ASC", (str(session['login_credentials'][0])))
    shared_archives = cursor.fetchall()

    # if no results are returned from above query, prints info message to container.
    if not shared_archives:
        # print "RESULT WAS NONE"
        side_container += "<li>No shared archives for this user!</li>"

    for shared_archive in shared_archives:
        # get the length of the archive to display
        cursor.execute("SELECT tweet FROM tweets WHERE archiveID = ?", (shared_archive[0],))
        result = cursor.fetchall()

        side_container += "<li class = 'menuOptions'><a class='menuItem' href='/displayArchive/" + str(shared_archive[0]) + "'>" + \
                     shared_archive[1] + " (" + str(
                len(result)) + ")</a></li><br>"
    side_container += "</ul><hr>"

    # adds all northern ireland trends to the container.
    side_container += "<div class='panel'><p class='panel-heading'>Trends in Northern Ireland</p>"
    side_container += local_trending + "</div></div>"

    # close database connections.
    cursor.close()
    connect.close()

    return side_container


# ------------ Archive related functionality --------------

def get_archive_creator(user, archive_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM archives WHERE userID = ? and id = ?", (user, archive_id,))
    creator = cursor.fetchone()
    cursor.close()
    connect.close()

    if creator:
        # current user is the archive creator
        return creator
    else:
        return False


def get_archive_name(count):
    # check if archive is owned by the current user

    current_user_created_archive = get_archive_creator(session['login_credentials'][0], session['archive_ID'],)

    # retrieve the current archives name
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT archive_name FROM archives WHERE id = ?", (session['archive_ID'],))
    archive_name = cursor.fetchone()

    header = "<p class='card-header-title'>Archive: " + str(archive_name[0]) + " ({}) ".format(count)

    # if user owns the archive then allow them to share it and delete it
    if current_user_created_archive:
        # get all users to share archive with
        # users = make_share_archive_dropdown()
        cursor.execute(
            "SELECT id, name, display_name FROM users WHERE NOT EXISTS "
            "(SELECT * FROM archiveUsers WHERE archiveUsers.sharedUserID = users.id "
            "AND archiveUsers.archiveID = ?) "
            "AND id != ? ORDER by users.name ASC",
            (session['archive_ID'], session['login_credentials'][0],))
        user_results = cursor.fetchall()

        if not user_results:
            share_to_users = "<form name='shareArchive' method='POST' action='/shareArchive'" \
                   "<div class='control'><div class='select'><select name='sharedUserID' disabled>" \
                   "<option>No available users to share archive with!</option></select></p></form>"
        else:
            share_to_users = "<form name ='shareArchive' method='POST' action='/shareArchive'>" \
                   "<div class='control'><div class='select'><select name='sharedUserID' onchange='form.submit()'>" \
                   "<option>Share archive</option>"

            for user in user_results:
                share_to_users += "<option value='" + str(user[0]) + "'>" + user[2] + "</option>"
            share_to_users += "</select></form></div></div>"

        # enable owner to delete their archive
        header += "<br><a href='/deleteArchive' class='button is-danger'> Delete Archive</a></p>"
        header += share_to_users
    else:
        # display name of user who shared the archive
        archive_creator = get_archive_login_credentials()
        header += "<p class = 'card-header-title'>Shared by: " + str(archive_creator[2]) + "</p>"
        header += "<p class = 'card-header-title'><a href='/unfollowArchive' class='button is-danger'> Unfollow Archive</a></p>"

    cursor.close()
    connect.close()
    return header


def get_archive_login_credentials():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # get archive owners id and name
    cursor.execute("SELECT id, name, display_name FROM users "
                   "WHERE id=(SELECT userID FROM archives WHERE id = ?)",
                   (session['archive_ID']))
    archive_creator = cursor.fetchone()

    return archive_creator


def create_share_archive_dropdown(tweet_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT id, archive_name, userID from archives "
                   "WHERE NOT EXISTS(SELECT * FROM tweets WHERE tweets.tweetID = ? AND archives.id = archiveID) "
                   "AND userID  = ?", (tweet_id, session['login_credentials'][0],))
    archives = cursor.fetchall()

    html=""
    if not archives:
        html += "<div class='select'><select name='archive_ID' disabled><option>No archives found</option></select>"
    else:
        html += "<div class='select'><select name='archive_ID' onchange='form.submit()'>"
        html += "<option>Save tweet to archive</option>"
        for archive in archives:
                html += "<option value='" + str(archive[0]) + "'>" + archive[1] + "</option>"
        html += "</select>"
    cursor.close()
    connect.close()

    return html


def create_tweet(item, mode, archive_list):
    global session

    html, tweet_html, links = '', item['full_text'], ''
    user_mentions, hashtags, images, urls = [], [], [], []

    if 'urls' in item['entities']:
        for user in item['entities']['urls']:
            # print user['indicies'][0]
            # print user['indicies'][1]
            # print user['url']
            urls.append([ user['indices'][0], user['indices'][1], 'urls', user['url']])
        sorted_urls = sorted(urls, key=itemgetter(0))

        for url in sorted_urls:
                tweet_html = tweet_html.replace(url[3]," <a target='_blank' href='" + url[3] + "'>" + url[3] + "</a>")
        # print urls
        # print sorted_urls

    if mode == 'myTimeline':
        links = "<form name='archive' method='post' action='/archive'>"
        links += "<input type='hidden' name='tweetID' value='" + str(item['id']) + "'>"
        links += archive_list
        links += "</form>"
    elif mode == 'archive':
        is_archive_creator = get_archive_creator(session['login_credentials'][0], session['archive_ID'], )

        # enable user to move the tweets in the archive and also delete them if they are the owner
        if is_archive_creator:
            links = "<a href='/moveUp/" + str(item['id']) + "'><img class = 'archiveArrows' title = 'Move Up' alt = 'Move Up' src='https://www.iconexperience.com/_img/o_collection_png/green_dark_grey/512x512/plain/navigate_up.png' style='height:50px; width:50px; border-radius:0% !important'/></a><br>" + \
                    "<a href='/moveDown/" + str(item['id']) + "'><img class = 'archiveArrows' title = 'Move Down' alt = 'Move Down' src='https://www.iconexperience.com/_img/o_collection_png/green_dark_grey/512x512/plain/navigate_down.png' style='height:50px; width:50px; border-radius:0% !important'/></a><br>" + \
                    "<a href='/deleteTweet/" + str(item['id']) + "'><img id = 'deleteIcon' title = 'Remove Tweet' alt ='Remove Tweet' src='https://image.flaticon.com/icons/svg/63/63260.svg' style='height:50px; width:50px; border-radius:0% !important'</a>"
    else:
        return


    # get the username and make into a clickable hyperlink.
    if 'user_mentions' in item['entities']:
        for user in item['entities']['user_mentions']:
            user_mentions.append([user['indices'][0], user['indices'][1], 'user', user['screen_name']])

        sorted_user_mentions = sorted(user_mentions, key=itemgetter(0))
        for user in sorted_user_mentions:
            tweet_html = tweet_html.replace("@" + user[3], "<a href='/userMentions/" + user[3] + "'>@" + user[3] + "</a>")

    # get hashtags and make into a clickable hyperlink.
    if 'hashtags' in item['entities']:
        for hashtag in item['entities']['hashtags']:
            hashtags.append(hashtag['text'])
        sorted_hashtags = sorted(hashtags, key=itemgetter(0))
        for hashtag in sorted_hashtags:
            tweet_html = tweet_html.replace("#" + hashtag, "<a href='/hashtag/" + hashtag + "'>#" + hashtag + " </a>")

    # images
    # print item['entities']
    if 'media' in item['entities']:
        for image in item['entities']['media']:
            images.append(image['media_url'])
            # print image

            if(image['url'] in item['full_text']):
                tweet_html = tweet_html.replace(image['url'], " <a target='_blank' href='" + image['url'] + "'>" + image['url'] + "</a>")
            # print images
        sorted_images = sorted(images, key=itemgetter(0))
        # print sorted_images

        for image in sorted_images:
            # print image
            tweet_html += "<br><div class='card-image'><figure style='max-width:256px; max-height:256px'>"
            tweet_html += "<img id = 'tweetedImage' src='" + image + "'></figure></div>"
            # print tweet_html

    # found and adapted from: https://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
    tweet_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

    html += "<div class='box'><article class='media'>"
    html += "<div class='media-left'><figure class='image is-48x48'><img src='" + item['user']['profile_image_url'] + "'></figure>"
    if mode == 'archive':
        html += "<div>"+links+"</div></div>"
    else:
        html += "</div>"
    html += "<div class='media-content'><div class='content'><p id='userField' class='title is-4' style='margin-bottom:0px !important'>" + item['user']['name'] + "</p><p class='subtitle is-6'><a id ='userHandle' href='/userMentions/" + item['user'][
        'screen_name'] + "'> @" + item['user']['screen_name'] + "</a></p></div>"

    html += "<p>" + tweet_html + "<br><hr/>"
    html += "<div><img style='width:20px' src='https://image.flaticon.com/icons/png/512/25/25328.png'>" \
            + str(item['retweet_count']) + \
            " <img style='width:20px' src='https://image.flaticon.com/icons/png/512/0/412.png'>" \
            + str(item['favorite_count']) + " "+" <div class='media-content'>"+str(tweet_date) +"</div></div><br>"
    # html += "<div id='date'> " + str(tweet_date) + "</div>"
    if not mode=='archive':
        html += "<div> " + links + " </div></div>"
    html += "</p></div></div></article><hr>"

    return html


# ------------ Twitter API Calls --------------

def call_api(twitter_url, parameters):
    url = twURL.augment(twitter_url, parameters)
    connection = urllib2.urlopen(url)
    return connection.read()


def show_user_timeline():
    twitter_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    parameters = {'count': 15, 'tweet_mode':'extended'}
    data = call_api(twitter_url, parameters)
    js = json.loads(data)

    html = ''

    for item in js:
        archives = create_share_archive_dropdown(item[ 'id' ])
        html += create_tweet(item, 'myTimeline', archives)
    return html


def get_tweet(tweet_id):
    twitter_url = 'https://api.twitter.com/1.1/statuses/show.json'
    parameters = {'id': tweet_id, 'tweet_mode': 'extended'}
    data = call_api(twitter_url, parameters)
    return json.loads(data)


def search_for_tweets(search_term):
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json'
    url = twURL.augment(twitter_url, {'q': search_term, 'count': 15, 'tweet_mode': 'extended'})
    connection = urllib2.urlopen(url)
    data = connection.read()
    js = json.loads(data)
    # print js
    html = ''

    for item in js['statuses']:
        archives = create_share_archive_dropdown(item['id'])
        html += create_tweet(item, 'myTimeline', archives)
        print html
    return html


# returns trends from the twitter api within the WoeID of 44544(Northern Ireland)
# TODO: Add ability to chagne to global trends/back to local trends and vice-versa
def get_trending_northern_ireland():
    trend_names = []
    html = ''
    twitter_url = "https://api.twitter.com/1.1/trends/place.json?"
    parameters = {'id': 44544, 'count': 10} #WoeID passed into the twitter api, found on: http://www.woeidlookup.com/
    data = call_api(twitter_url, parameters)
    json_data = json.loads(data)


    for values in json_data:
        trend_obj = values['trends']
        for trend in trend_obj:
            if 'name' in trend:
                trend_names.append([trend['name'], trend['query'] ])

        sorted_trends = sorted(trend_names, key=itemgetter(0))

        for name in sorted_trends:
            html += "<a class ='panel-block' href='/trend/" + name[1] + "'>" + name[0] + "</a>"

    return html


def show_stored_tweets(archive_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT tweet FROM tweets "
                   "WHERE archiveID = ? "
                   "ORDER BY position ASC", (archive_id,))
    result = cursor.fetchall()
    count = len(result)
    cursor.close()
    connect.close()
    html = ''

    for tweet in result:
        html += create_tweet(pickle.loads(tweet[0]), 'archive', '')
    return html, count


# ------------ Routes --------------

# index route
@route('/')
def index():
    global session
    # checks if details have been passed into the login_credentials dictionary - if they haven't redirect to /login route.
    if not session['login_credentials']:
        redirect('/login')
    else:
        user = session['login_credentials'][3] + '\'s' # adds 's to the username to show within the heading.
        html = show_user_timeline()
        return template('showTweets.tpl', heading="<p class='card-header-title'>"+ user + " Timeline</p>", menu=create_side_container_component(), html=html)

@route('/userMentions/<name>')
def user_mentions(name):
    if not session['login_credentials']:
        redirect('/login')
    name = "@" + name
    html = search_for_tweets(name)

    return template('showTweets.tpl', heading="<p class='card-header-title'>"+name+"</p>", menu=create_side_container_component(), html=html)

@route('/hashtag/<hashtag>')
def search_for_hashtag(hashtag):
    if not session['login_credentials']:
        redirect('/login')
    hashtag = "#" + hashtag
    html = search_for_tweets(hashtag)

    return template('showTweets.tpl', heading="<p class='card-header-title'>"+hashtag+"</p>", menu=create_side_container_component(), html=html)


@route('/login')
def login():
    return template('loginRegister.tpl', message='Tweety-Py Login', link='/register',
                    linkMessage='Register to Tweety-Py', post='/verifyLogin')


@route('/verifyLogin', method='post')
def login_submit():

    global session
    name = request.forms.get('name').lower()
    password = request.forms.get('password')

    print name
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users "
                   "WHERE name = ? and password = ?", (name.lower(), password))
    found = cursor.fetchone()
    cursor.close()
    connect.close()

    if found:
        # user exists and password matches
        session['login_credentials'] = found
        redirect('/')
    else:
        # user does not exist or password does not match
        return template('loginVerification.tpl', message='Incorrect user credentials - please try again!',
                        link='/login', linkMessage='Retry Login')


@route('/register')
def sign_up():
    return template('loginRegister.tpl', message='Tweety-Py Registration', link='/login',
                    linkMessage='Existing member? Login here!', post='/verifyRegistration')


@route('/verifyRegistration', method='post')
def verify_registration():

    display_name = request.forms.get('name')
    name = request.forms.get('name').lower()
    password = request.forms.get('password')

    if name == '' or password == '':
        return template('loginVerification.tpl', message='Please enter both a username and password when registering!',
                        link='/register', linkMessage='Retry Registration')
    else:
        connect = sqlite3.connect('twitterDB.db')
        cursor = connect.cursor()

        cursor.execute('SELECT name FROM users '
                       'WHERE name = ?', (name.lower(),))
        db_row = cursor.fetchone()

        if db_row is not None:
            return template('loginVerification.tpl', message='Username already exists - Please try a different one!',
                            link='/register', linkMessage='Retry Registration')
        else:
            # add new user name and password to db
            cursor.execute("INSERT INTO users (name, password, display_name) VALUES (?, ?, ?)", (name.lower(), password, display_name))
            connect.commit()
            cursor.close()
            connect.close()

            return template('loginVerification.tpl', message='User Registered Successfully!',
                            link='/login', linkMessage='Log in')


@route('/archive', method='post')
def archive_tweet():
    global session
    if not session['login_credentials']:
        redirect('/login')

    archive_id = request.POST.get('archive_ID', '').strip()

    # print archive_id

    # return archive_id;
    tweet_id = request.POST.get('tweetID', '').strip()
    pickled_tweet = pickle.dumps(get_tweet(tweet_id))
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute('SELECT position FROM tweets '
                   'WHERE archiveID = ? '
                   'ORDER BY position DESC LIMIT 1', (archive_id))
    db_row = cursor.fetchone()

    if db_row is not None:
        next_position = int(db_row[0]) + 1
    else:
        next_position = 1
    cursor.execute("INSERT INTO tweets (tweetID, tweet, archiveID, position) VALUES (?,?,?,?)",
                   (tweet_id, sqlite3.Binary(pickled_tweet), archive_id, next_position))
    connect.commit()
    cursor.close()
    connect.close()
    session['archive_ID'] = archive_id
    html, count = show_stored_tweets(archive_id)

    return template('showTweets.tpl', heading=get_archive_name(count), menu=create_side_container_component(), html=html)


@route('/deleteTweet/<id>')
def delete_tweet(id):
    if not session['login_credentials']:
        redirect('/login')
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM tweets WHERE tweetID = ? AND archiveID = ?", (id, session['archive_ID']))
    connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archive_ID'])

    return template('showTweets.tpl', heading=get_archive_name(count), menu=create_side_container_component(), html=html)


@route('/moveUp/<id>')
def move_up(id):
    global session
    if not session['login_credentials']:
        redirect('/login')

    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT position FROM tweets "
                   "WHERE tweetID = ? AND archiveID = ?", (id, session['archive_ID']))
    position = cursor.fetchone()[0]
    cursor.execute(
        "SELECT tweetID, position FROM tweets "
        "WHERE position < ? AND archiveID = ? "
        "ORDER BY position DESC LIMIT 1",
        (position, session['archive_ID']))
    db_row = cursor.fetchone()

    if db_row is not None:
        other_id, other_position = db_row[0], db_row[1]
        cursor.execute("UPDATE tweets SET position = ? WHERE tweetID = ? AND archiveID = ? ",
                       (other_position, id, session['archive_ID']))
        cursor.execute("UPDATE tweets SET position = ? WHERE tweetID = ? AND archiveID = ?",
                       (position, other_id, session['archive_ID']))
        connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archive_ID'])
    return template('showTweets.tpl', heading=get_archive_name(count), menu=create_side_container_component(), html=html)


@route('/moveDown/<id>')
def move_down(id):
    global session
    if not session['login_credentials']:
        redirect('/login')

    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT position FROM tweets WHERE tweetID = ? AND archiveID = ?", (id, session['archive_ID']))
    position = cursor.fetchone()[0]
    cursor.execute(
        "SELECT tweetID, position FROM tweets WHERE position > ? AND archiveID = ? ORDER BY position ASC LIMIT 1",
        (position, session['archive_ID']))
    db_row = cursor.fetchone()

    if db_row is not None:
        other_id, other_position = db_row[0], db_row[1]
        cursor.execute("UPDATE tweets SET position = ? WHERE tweetID = ? AND archiveID = ? ",
                       (other_position, id, session['archive_ID']))
        cursor.execute("UPDATE tweets SET position = ? WHERE tweetID = ? AND archiveID = ?",
                       (position, other_id, session['archive_ID']))
        connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archive_ID'])
    return template('showTweets.tpl', heading=get_archive_name(count), menu=create_side_container_component(), html=html)


@route('/displayArchive/<archive_id>')
def display_archive(archive_id):
    global session
    if not session['login_credentials']:
        redirect('/login')

    session['archive_ID'] = archive_id
    html, count = show_stored_tweets(archive_id)

    return template('showTweets.tpl', heading=get_archive_name(count), menu=create_side_container_component(), html=html)


@route('/createArchive', method='post')
def create_archive():
    if not session['login_credentials']:
        redirect('/login')
    new_archive = request.POST.get('newArchive', '').strip()
    user_id = session['login_credentials'][0]
    user = session['login_credentials'][3] + '\'s'
    html = show_user_timeline()
    if new_archive != '' or new_archive == None:
        connect = sqlite3.connect('twitterDB.db')
        cursor = connect.cursor()

        cursor.execute("SELECT archive_name FROM archives WHERE archive_name = ? AND userID = ?", (new_archive, user_id))
        archiveExists = cursor.fetchone()

        if archiveExists is not None:
            return template('showTweets.tpl', heading="<p class='card-header-title'>"+user + " Timeline</p>", menu=create_side_container_component(), html=html)
        # add new archive name and owner to db
        cursor.execute("INSERT INTO archives (archive_name, userID) VALUES (?,?)", (new_archive, user_id,))
        connect.commit()

        cursor.close()
        connect.close()
    html = show_user_timeline()

    return template('showTweets.tpl', heading="<p class='card-header-title'>"+user + " Timeline</p>", menu=create_side_container_component(), html=html)


@route('/deleteArchive')
def delete_archive():
    global session
    if not session['login_credentials']:
        redirect('/login')
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE from archives WHERE id = ?", (session['archive_ID']))
    cursor.execute("DELETE from tweets WHERE archiveID = ?", (session['archive_ID']))

    connect.commit()
    cursor.close()
    connect.close()

    user = session['login_credentials'][3] + '\'s'
    html = show_user_timeline()
    return template('showTweets.tpl', heading="<p class='card-header-title'>"+user + " Timeline</p>", menu=create_side_container_component(), html=html)


@route('/unfollowArchive')
def delete_archive():
    global session
    if not session['login_credentials']:
        redirect('/login')

    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # delete current user from the archiveUsers if they decide to unfollow
    cursor.execute("DELETE FROM archiveUsers WHERE sharedUserID = ? AND archiveID = ?",
                   (session['login_credentials'][0], session['archive_ID'], ))
    connect.commit()
    cursor.close()
    connect.close()

    user = session['login_credentials'][3] + '\'s'
    html = show_user_timeline()

    return template('showTweets.tpl', heading="<p class='card-header-title'>"+ user + " Timeline</p>", menu=create_side_container_component(), html=html)


# routing and function to provide searching facilities within the application searchbar
@route('/searchTwitter', method='post')
def search_twitter():
    global session
    if not session['login_credentials']:
        redirect('/login')
    search_criteria = request.POST.get('searchTwitter', '').strip()
    html = search_for_tweets(search_criteria)

    print html

    return template('showTweets.tpl', heading="<p class='card-header-title'>Search Criteria: " + search_criteria +"</p>", menu=create_side_container_component(), html=html)


@route('/trend/<trend>')
def search_for_trend(trend):
    global session
    if not session['login_credentials']:
        redirect('/login')
    html = search_for_tweets(trend)

    return template('showTweets.tpl', heading="<p class='card-header-title'>Trend Search Criteria: "+trend +"</p>", menu=create_side_container_component(), html=html)


@route('/shareArchive', method='post')
def share_archive():
    global session
    if not session['login_credentials']:
        redirect('/login')
    shared_user_id = request.POST.get('sharedUserID', '').strip()
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # add user to archive users list to enable them to view the shared archive
    cursor.execute("INSERT INTO archiveUsers (archiveID, sharedUserID) VALUES (?,?)",
                   (session['archive_ID'], shared_user_id))
    connect.commit()
    cursor.close()
    connect.close()

    redirect('/displayArchive/' + session['archive_ID'])


@route('/logout')
def logout():
    session.clear()
    redirect('/login')

debug(True)
run(reloader=True)
