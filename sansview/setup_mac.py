"""
This is a setup.py script partly generated by py2applet

Usage:
    python setup.py py2app
"""
from setuptools import setup
import periodictable.xsf
import DataLoader.readers 
from distutils.sysconfig import get_python_lib
import os
import string
import local_config

ICON = local_config.SetupIconFile_mac
DATA_FILES = []
RESOURCES_FILES = []
EXTENSIONS_LIST = []

#Periodictable data file
DATA_FILES = periodictable.data_files()
#add guiframe data file
import sans.guiframe as guiframe
DATA_FILES += guiframe.data_files()
#invariant and calculator help doc
import sans.perspectives.calculator as calculator
DATA_FILES += calculator.data_files()
import sans.perspectives.invariant as invariant
DATA_FILES += invariant.data_files()
import sans.models as models
DATA_FILES += models.data_files()

#CANSAxml reader data files
RESOURCES_FILES.append(os.path.join(DataLoader.readers.get_data_path(),
                                    'defaults.xml'))
# locate file extensions
def find_extension():
    """
    Describe the extensions that can be read by the current application
    """
    try:
        list = []
        EXCEPTION_LIST = ['*', '.', '']
        #(ext, type, name, flags)
        from DataLoader.loader import Loader
        wild_cards = Loader().get_wildcards()
        for item in wild_cards:
            #['All (*.*)|*.*']
            file_type, ext = string.split(item, "|*.", 1)
            if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
                list.append((ext, 'string', file_type))
    except:
        raise
    try:
        file_type, ext = string.split(local_config.APPLICATION_WLIST, "|*.", 1)
        if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
            list.append((ext, 'string', file_type))
    except:
        raise
    try:
        for item in local_config.PLUGINS_WLIST:
            file_type, ext = string.split(item, "|*.", 1)
            if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
                list.append((ext, 'string', file_type)) 
    except:
        raise
    
    return list

EXTENSIONS_LIST = find_extension()
temp = []
for (ext, _, file_type) in EXTENSIONS_LIST:
    dict(CFBundleTypeTypeExtensions=[str(ext)],
         CFBundleTypeIconFile=ICON,
         #CFBundleTypeName=str(file_type),
         CFBundleTypeRole="Viewer")
    temp.append(dict)
    
PLIST = dict(CFBundleDocumentTypes=temp)
    

# Locate libxml2 library
lib_locs = ['/usr/local/lib', '/usr/lib']
libxml_path = None
for item in lib_locs:
    libxml_path_test = '%s/libxml2.2.dylib' % item
    if os.path.isfile(libxml_path_test): 
        libxml_path = libxml_path_test
if libxml_path == None:
    raise RuntimeError, "Could not find libxml2 on the system"

APP = ['sansview.py']
DATA_FILES += ['images','test','plugins','media']
OPTIONS = {'argv_emulation': True,
           'packages': ['lxml','periodictable'],
           'iconfile': ICON,
           'frameworks':[libxml_path],
           'resources': RESOURCES_FILES,
           'plist':PLIST
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    include_package_data= True,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

