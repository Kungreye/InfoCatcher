# InfoCatcher

InfoCatcher is an app for post display. It is built with Flask.


## Features
1. Register / Login & Logout
2. Homepage Post
3. Tags
4. Search
5. Upvote
6. Collect
7. Comment
8. User (following / setting)
9. Share (hot / latest)
10. Homepage Feed


## Scaffolds
- Flask
- SQLAlchemy
- Bootstrap
- JQuery
- MySQL
- Redis
- Elasticsearch

---
## Install

    git clone https://github.com/Kungreye/InfoCatcher.git

---
## Requirements
<b>1.</b> Packages below have been customized, and should be installed first:

- <b>for Register / Login / Logout</b>

        pip install git+https://github.com/Kungreye/flask-security.git@develop

- <b>for Social-auth</b> 

        pip install git+https://github.com/Kungreye/social-core.git@master

        pip install git+https://github.com/Kungreye/social-app-flask.git@master

        pip install git+https://github.com/Kungreye/social-app-flask-sqlalchemy.git@master

        pip install git+https://github.com/Kungreye/social-storage-sqlalchemy.git@master


<b>2.</b> Install other packages via <i>requirements</i>.

        pip install -r requirements
    
----
## Configure

Change <i>config.py</i> according to your needs, like:
- database uri
- redis
- mail server
- celery config
- etc.

Note: to enable social-auth, remember to add <i>SOCIAL_AUTH_GITHUB_KEY</i> and <i>SOCIAL_AUTH_GITHUB_SECRET</i>.

    
---
## Front-end preparation

- Install <b>npm</b>. (You should have noticed a file named <b>package.json</b>, which was initially created by <i>npm init</i>)
- Run <b><i>npm install</i></b>, to install the dependencies specified in package.json, then you would see a dir <i>node_modules</i>.
- Run <b><i>npm run build</i></b>

---
### Start app

- Init db
   
        export FLASK_APP=manage.py
    
        flask initdb


- Flush redis

        redis-cli flushall
      

- Start app

<i>Note</i>: Elasticsearch, Redis and RabbitMQ should be started in advance.

        export FLASK_APP=app.py
        
        flask run
               
                
- Open browser at <i>localhost:5000</i>, register, login and set profile.

> Until now, you should see nothing in the homepage.

..................................................................................................................................

- Start celery

        celery -A handler worker -l info


- Fill some content for display

        python3 crawling.py 
        

- After the crawling is completed, start app again, and login to check the new content.


---
## Demo

- Posts by tag <i>python</i>
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/posts_by_tag.png">
---
- Post
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/post.png">
---
- Upvote, collect, comment
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/upvote_collect_comment.png">
---
- Share to Weixin
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/share_weixin.png">
---
- Share to Weibo
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/share_weibo.png">
---
- Setting
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/setting.png">
---
- Follow
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/following.png">
<h>
<img src="https://github.com/Kungreye/InfoCatcher/blob/master/demo/follow.png">
---