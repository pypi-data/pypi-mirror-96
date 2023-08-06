# smart-files
### Ashley Casimir, Sean Hawkins, Ben Hill, Karlo Mangubat

## Instructions

### Before We Start

This module utilizes `crontab`.

For Mac ver. 10.15.6 or greater:

1. In order for this module to work properly, we need to grant full-disk access for `cron` upon installation

2. Open Finder and on the top-left corner of the screen, click "Go" and select “Go to folder"

3. Insert this to location: `/usr/sbin/cron` 

4. Select "Go" and locate `cron`

5. Go to System Preferences and then to Security and Privacy

6. Navigate to Full Disk Access and click the lock at the bottom left to unlock

7. Drag `cron` from finder to the list of apps in Full Disk Access. Ensure `cron` is checked prior to closing the window. 

### Quick Start
1. On your Terminal, navigate to the smart-files repo
2. Run `poetry install`
3. Run `poetry run smart-files` to display options

### Add Scheduled Sorting Job
1. Run `poetry run smart-files cron` to display job frequency options. The result is displayed below:
```
Options:
-m, --minutes  Will create a cron job for Smart-files to run every minute
-h, --hour     Will create a cron job for Smart-files to run every hour
-d, --day      Will create a cron job for Smart-files to run once every day
-o, --month    Will create a cron job for Smart-files to run once a month
--help         Show this message and exit.
```
2. Add the desired command at the end of `poetry run smart-files cron`
3. For example, the command for running smart-files every minute would be `poetry run smart-files cron -m`
4. Verify that the crontab job exists by running the command `crontab -l`
> Note: Running a new smart-files job will overwrite the old smart-files job.
### Sort Files
To sort files on an ad hoc basis:
1. Run `poetry run smart-files run`
2. Check Downloads folder and verify that the files are sorted to their respective folders. 

### Display Unsorted Files
To display unsorted files:
1. Run `poetry run smart-files show-files`
2. The files displayed are coming from the Downloads folder, excluding the folders smart-files creates


## Preparations

1. Summary of idea:

- An app that takes all downloaded files and automatically puts them in the proper folder based on the file type. For example, an image (.jpg or .png) would automatically go into the images folder from downloads.

2. Problem or pain point:

- Are you tired of having to organize your downloads manually? Do you just not have time for it? Our app will do this automatically so that the only thing you need to do is download. Our app will automatically filter it into the correct directory.

3. Minimum Viable Product (MVP) definition:

- We will be able to _easily_ prove that common file types for images, videos, standard docs, and software downloads will automatically transfer from the downloads folder to the correct directory. Our app should be able to do this in a very short amount of time to display seamless functionality. In addition, the app should be able to work on all our individual machines. This app will be added as a pip module. This will involve at least:
  - Creating a setup file to help new users download and use as intended.
  - Creating various forms of documentation.
  - Creating a license.
  - Creating a source distribution (meta-data) to ensure program works on everyone’s computer. -Testing and publishing package on PyPl.

## Domain model
- User will have the option to pip install

![domain](img/domain.png)
## Wire frame
![download](img/top-level-wf.png)
![software](img/software-wf.jpeg)
![document](img/doc-wf.jpeg)
![image](img/img-wf.jpeg)
![other](img/other-wf.jpeg)