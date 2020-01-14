PlecoViewer can be used to get a graphical analysis of flashcard progress based on Pleco flashcard backup files.

Issues and pull requests are always welcome!

### **Installation**
The project uses Bokeh server. I recommend to use the provided conda environment.

Clone the repository
```
git clone https://github.com/Mr-Pepe/PlecoViewer.git && cd PlecoViewer
```

Copy all the Pleco backups you want to analyze into the backups folder.

Create the conda environment and activate it
```
conda env create -n plecoviewer -f environment.yml
conda activate plecoviewer
```

Install PlecoViewer
```
pip install .
```

Now the application can be run with
```
bokeh serve --show plecoviewer/
```
A browser window should automatically pop up. It might take a few seconds to load all backups.
