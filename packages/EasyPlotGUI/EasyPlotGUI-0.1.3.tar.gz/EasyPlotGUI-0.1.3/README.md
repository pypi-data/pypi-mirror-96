# EasyPlotGUI
 Python library that makes it easy to have a Qt GUI with a matplotlib widget made in QtDesigner implemented on a script.

 # Installation

 ```
 pip install EasyPlotGUI
 ```

 # Easy implementation process
 1. Create GUI on QtDesigner based on `mpl_gui.ui`
 1. Compile your ui to Python with `pyuic5 ./your_file.ui -o ./your_ui.py `
 1. Import `EasyPlotGUI` as parent class (see example of usage)
 1. Overwrite `update_graph()` with graph to be generated; and `update_interactivity()` with GUI elements interaction

 Check out the example on `./example.py`.

 ## QtDesigner
 ### Installation with pip
QtDesigner is a Graphical tool for creating Guided User Interfaces that can either be downloaded with Qt Creator or with the library `pyqt5-tools`.

Lightest and fastest way to get QtDesigner is to install `pyqt5-tools`. For this, execute:

```
pip install pyqt5-tools
```

After the installation, the `designer.exe` executable should be found in:

```
Python3X\Lib\site-packages\pyqt5_tools\Qt\bin\designer.exe
```

I suggest creating a shortcut for it, for easier execution or adding the folder to the path, so that it can be called as just `designer` from the terminal/shell.

### UI with Matplotlib Creation

Use the `mpl_gui.ui` file on QtDesigner as a starting point for the GUI with Matplotlib integrated. Just keep in mind that the names of every object added to the User Interface are those you will have to call on the Python script.

The only important thing in this .ui file is the MplWidget object. The MplWidget is the widget created to link matplotlib to Qt. Do not delete it.

![Example output](./test_example.png "Example output")

# Step by step - Creating a User Interface

## 1. Create a new file (MainWindow) on Qt Designer
![alt](step1.png)

## 2. Add a QWidget to it

![alt](step2.gif)

## 3. Promote the widget to MplWidget

Right click on the widget that was just added and click on *Promote to...* . The class name has to be **MplWidget** and the header file **EasyPlotGUI** so that the Python script can link it. Click on *Add* to add the new promoted class, then select it and click on *Promote*.

![alt](step3.gif)

## 4. Add your UI elements

Add the desired element. The name of the elemen (*mySlider* in the example) is what you'll call in your class (`self.ui.mySlider.value()` gives the value of the slider).

![alt](step4.gif)

Now save the file. It should have a `.ui` extension.

## 5. Compile the `.ui` into a `.py`

```
pyuic5 ./your_file.ui -o ./your_ui.py
```

## 6. Import it in your class

```python
from EasyPlotGUI import EasyPlotGUI
import your_ui

import numpy as np

class MyClass(EasyPlotGUI):
    def __init__(self):
        super().__init__(your_ui)
        self.window_title = "My GUI Name"
        self.icon_path = "logo.png"

        # initialize Graph variables for first plot
        self.f = 1

    def update_interactivity(self):
        self.ui.mySlider.valueChanged.connect(self.change_frequency)

    def change_frequency(self):
        self.f = self.ui.mySlider.value()
        self.update_graph()

    def update_graph(self):
        x = np.linspace(0, 1)
        y = np.sin(2*np.pi*self.f*x)

        self.ax.clear()
        self.ax.plot(x, y, label="Sine")
        self.ax.legend()
        self.ax.set_title('Sine Wave')
        self.draw()

    # calling it
if __name__ == "__main__":
    my_gui=MyClass()
    my_gui.show_gui()
```
