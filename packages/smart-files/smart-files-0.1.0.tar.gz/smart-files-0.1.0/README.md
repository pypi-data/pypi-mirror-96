# smart-files

## Instructions

This project uses Python Poetry as a virtual environment in order to run

### Ashley Casimir, Sean Hawkins, Ben Hill, Karlo Mangubat

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