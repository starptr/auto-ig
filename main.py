import os
import time
import csv
from instapy import InstaPy
from instapy import smart_run
from dotenv import load_dotenv
load_dotenv()


def fancyLog(x):
    print(f">>>> {x}")


HALF_DAY_IN_SECONDS = 60 * 60 * 12
DAY_IN_SECONDS = 2 * HALF_DAY_IN_SECONDS
WEEK_IN_SECONDS = DAY_IN_SECONDS * 7

# login credentials
insta_username = os.getenv("INSTA_USERNAME")  # <- enter username here
insta_password = os.getenv("INSTA_PASSWORD")  # <- enter password here
bep = os.getenv("BROWSER_EXECUTABLE_PATH")

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
# session = InstaPy(username=insta_username, password=insta_password, browser_executable_path=bep, headless_browser=False)
session = InstaPy(username=insta_username, password=insta_password, headless_browser=False)

with smart_run(session):
    session.set_skip_users(skip_private=False, private_percentage=0)

    fancyLog("Checking lastrun")
    with open("./data/lastrun.log", "r") as ftime:
        lastrun_timestamp = ftime.readline()

    # Check if at least a day has passed before getting following/ers
    if (not lastrun_timestamp) or (time.time() - float(lastrun_timestamp) >= HALF_DAY_IN_SECONDS):
        # Get list from online
        fancyLog("Lastrun was more than 12 hrs ago; getting followers and followings")
        followings = set(session.grab_following(username=insta_username, amount="full"))
        followers = set(session.grab_followers(username=insta_username, amount="full"))

        # Keep uni-directionals only
        followings_only = list(followings.difference(followers))
        followers_only = list(followers.difference(followings))

        # Read current followings_only
        with open("./data/followings_only.csv", "r") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')
            followings_only_read = [row for row in reader]

        # Create a fast lookup for whether a user was already in followings_only from disk
        followings_only_read_dict = {
            username: index
            for index, [username, timestamp] in enumerate(followings_only_read)
        }

        # Get whitelist (will be followed forever)
        followings_only_whitelist = set()
        with open("./data/followings_only_whitelist.txt", "r") as f:
            for line in f:
                followings_only_whitelist.add(line.rstrip())

        # Will be written
        followings_only_write = []

        # For unfollowing
        will_unfollow = []

        # New followings_only timestamp begins now
        # Old followings_only timestamp carries over from before
        for username in followings_only:
            if username in followings_only_whitelist:
                continue
            maybeIndex = followings_only_read_dict.get(username)
            if maybeIndex is None:
                followings_only_write.append([username, time.time()])
            else:
                timestamp_str = followings_only_read[maybeIndex][1]
                # Will unfollow followings_only over a week old
                if time.time() - float(timestamp_str) >= WEEK_IN_SECONDS:
                    will_unfollow.append(username)
                else:
                    followings_only_write.append([username, timestamp_str])

        # Unfollow >week followings_onlies
        session.unfollow_users(amount=len(will_unfollow),
                               custom_list_enabled=True,
                               custom_list=will_unfollow,
                               custom_list_param="all",
                               style="FIFO",
                               unfollow_after=None)

        # Save
        with open("./data/followings_only.csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=",", quotechar='"')
            writer.writerows(followings_only_write)

        with open("./data/followers_only.txt", "w") as fout:
            fout.write("\n".join(followers_only))

        # Write current run timestamp
        with open("./data/lastrun.log", "w") as ftime:
            ftime.write(str(time.time()))
    else:
        fancyLog("Lastrun was less than 24 hours ago; skipping followers and followings")

    # session.follow_by_list(followlist=to_follow, times=1, sleep_delay=600, interact=False)

    session.like_by_feed(amount=1000, randomize=False, unfollow=False, interact=False)
