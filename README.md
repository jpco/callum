# callum

For "CALEndar Merge": I hacked together callum to merge several of my Google calendars in order to share them more conveniently with someone else, and because I didn't want to spend a whopping $2/mo to a website to do it.

For now callum simply authenticates as user, creates a calendar 'callum-merged' if it does not exist (if it does exist, empties all 'callum-merged' events which have not already passed), and copies all future events from calendars with summaries (names) listed in `calmn_list` to the 'callum-merged' calendar.

If you are running callum for the first time, run it on a machine which can run a browser; when callum tries to authenticate, it will open the browser and authentication can happen from there.  From then on, user credentials are stored in `~/.credentials/callum_usercred.json`, which can be migrated machine to machine as necessary.

Additionally, callum needs the file `callum_cred.json` in the same directory as `callum.py`; this file can be generated following the Python quickstart at `https://developers.google.com/google-apps/calendar/quickstart/python`.

Lastly, you must have the `google-api-python-client` package in pip. Help in that regard can also be found in the above link.

Like I said, this is a really, really dumb script. I simply have it run in a cron job every midnight. If I ever care enough, I might set up push notifications for this, but I probably won't... oh well.
