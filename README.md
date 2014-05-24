No-Repost-Tumblr
================

A python script that gets all of the photos posted from one of your bloggers that is deemed original. To use this software, you must configure your tumblr with oauth so that the software can get access to the nessesary data. This software does not make any posts on your behalf, like anything, or change anything. It simply scans a target blog for any photo posts that could be posted by that same blogger (meaning that they are the original poster, not a reblogger.)

Release number: 0.1 beta
---------------
That means this software is still under construction, and not yet proven to be correct/stable. Working with python 2.7.5

Instructions:
--------
- Install both the PyTumblr API (https://github.com/tumblr/pytumblr) and Oauth (https://github.com/simplegeo/python-oauth2)
- Configure your tumblr for access with oauth (which I did here -> https://api.tumblr.com/console//calls/user/info)
- run with ```python noRepostTumblr.py```

TODO
----
- Solve the issues with missing API data from posts.
- Clean up some formatting, and maybe a bit of the logic for speed.
- Create an install script to walk through the dependency list.
- Update for python 3.
- Add a GUI (reach goal, might be unnessesary.) 
