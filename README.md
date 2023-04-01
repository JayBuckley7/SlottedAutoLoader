# SlottedAutoLoader
This script automates launching slotted plugin when league-of-legends.exe starts

# Installation
Install Python 3.x.
Install the required Python modules:
# Copy code - install prereqs
```pip install psutil pywin32 pywinauto cachetools
```
Download the script and save it to your desired directory.
# Usage
- On start it will try to find your slotted exe, if it can't find it it will ask you where it is and then save the location for next time
- then it will ask you to take a small screenshot of the load button on slotted (so it can find and click load)

-- then if everything loaded correctly it'll just sit in the background and if league opens it will auto launch slotted and then fire the load button off and then hang out till league closes and do it all over again

--you can hard code the paths into the script if you want and it'll stop looking for them
