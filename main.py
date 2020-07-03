from instapy import InstaPy
from instapy import smart_run
from dotenv import load_dotenv
load_dotenv()
import os

# login credentials
insta_username = os.getenv("INSTA_USERNAME")  # <- enter username here
insta_password = os.getenv("INSTA_PASSWORD")  # <- enter password here
bep = os.getenv("BROWSER_EXECUTABLE_PATH")

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
session = InstaPy(username=insta_username,
                  password=insta_password,
                  browser_executable_path=bep,
                  headless_browser=False)

with smart_run(session):
    session.like_by_feed(amount=100,
                         randomize=False,
                         unfollow=False,
                         interact=False)
