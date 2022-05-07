#!/usr/bin/env python

import shutil
import stat
import os


# create a zip file of the source code
# the program can still be executed with 'python filename.zip [ARGS]'
shutil.make_archive('scry_in_progress', 'zip', 'source')

# create a new file with a shebang at the top, then concat the zip file contents to it
with open('scry', 'wb') as scry_final:
    scry_final.write(str.encode('#!/usr/bin/env python\n'))
    with open('scry_in_progress.zip', 'rb') as scry_zip:
        shutil.copyfileobj(scry_zip, scry_final)

# remove the temporary zip file
os.unlink('scry_in_progress.zip')

# make the final file executable
# linux users can then call it with 'scry [ARGS]'
os.chmod('scry', os.stat('scry').st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
