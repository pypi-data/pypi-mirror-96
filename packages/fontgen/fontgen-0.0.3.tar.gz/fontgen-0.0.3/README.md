
# fontgen  
  
Python package for generating fonts.   
  
## Installation  
  
This is one time process.  
  
Fontgen requires Python 3.8 or later.  
  
### First you need to create a virtual environment for python  
  
On macOS and Linux:  
  
`python3 -m venv venv`  
  
On Windows:  
  
`py -m venv venv`  
  
### Activating a virtual environment  
  
On macOS and Linux:  
  
`source venv/bin/activate`  
  
On Windows:  
  
`.\venv\Scripts\activate`  
  
### Downloading  and Installing fontgen  
  
Run following command
  
`pip install fontgen`
  
## Usage  
  
Make sure the virtual environment is activated.  
  
Refer to [Activating a virtual environment](https://github.com/itfoundry/fontgen#activating-a-virtual-environment)  
  
Set a configuration before running a command for the first time. Refer to democonfig.ini for config format.

Load a configuration if you have any custom configuration.

`fontgen -lc myconfig.ini`

If you don't want to use config file. Tyle this command to set empty config.

`fontgen -lc reset`

Compile a font:  
  
`fontgen -f "Font Family Name" -o var`  
  
For italic version you will have to type "Font Family Name Italic"  
  
For detailed usage, type:  
   
 `fontgen -h`
 
 ## Directory structure
 
You can keep designspace file or glyphs file under masters directory. If it is glyphs file, you can convert it to
designspace by running following command. Make sure to create info.txt file in the directory.

`fontgen -f "Font Family Name" -gd`

    
    / Base Directory (Name of the Directory = Font family name)
        / masters
            /Family Name.designspace (or)
            /Family Name.glyphs
        /info.txt
    
           