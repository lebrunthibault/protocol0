> A super cool explorer for your ableton sets

# Goal
Let's drop this stupid and generic os explorer and make it easy to browse, listen and add metadata to all the ableton sets stored in a directory.
The web app makes the following things possible :
- sort sets by : name, most recent modification, stars (see below), commented (see below)
- preview sets that have been exported to audio with a nice player
- rank sets by assigning them stars (0 to 5)
- add a commentary to the set
- assign a "stage" to the set depending on if it's an idea, a work in progress or a pre-release.
The stages are named : draft, beta and release
- archive or restore a set (in fact move it to an archive folder)
- soft delete an archived set (in fact move it to a trash folder)
- be able to do all of this on archived sets as well as "released" sets (sets present in a specific release folder)

All this is done without opening the set. 
The metadata data is stored in a json file that has the set name with a .json extension.

# Install
The app is bundled as 2 docker images.
You should install docker and then run the 2 images (one for the frontend, one for the backend)

- [Install docker](https://docs.docker.com/engine/install/)
- Run the backend with : `docker run -p 8000:8000 -v "<YOUR_SETS_FOLDER>:/sets" -d thibaultlebrun/p0_web_backend:development`
and replace `YOUR_SETS_FOLDER` with your sets folder (e.g. "D:\sets")
- Run the frontend with : `docker run -p 8080:8080 -v -d thibaultlebrun/p0_web_frontend:development`
- Access the web app at `localhost:8080`

## Folder layout
The web app expects the following layout for the sets present in a *single* root directory
- A `tracks` folder for all work in progress sets
- An `other\archive` folder for archived sets
- An `other\trash` folder for soft deleted sets
- An `other\released` folder for released sets

This layout might be made configurable later from the app.
