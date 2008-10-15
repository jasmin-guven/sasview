"""
 Installation script for SANS models

  - To compile and install:
      python setup.py install
  - To create distribution:
      python setup.py bdist_wininst
  - To create odb files:
      python setup.py odb

"""
import sys

def createODBcontent(class_name):
    """
        Return the content of the Pyre odb file for a given class
        @param class_name: Name of the class to write an odb file for [string]
        @return: content of the file [string]
    """
    content  = "\"\"\"\n"
    content += "  Facility for SANS model\n\n"
    content += "  WARNING: THIS FILE WAS AUTOGENERATED AT INSTALL TIME\n"
    content += "           DO NOT MODIFY\n\n"
    content += "  This code was written as part of the DANSE project\n"
    content += "  http://danse.us/trac/sans/\n"
    content += "  @copyright 2007:"
    content += "  Mathieu Doucet (University of Tennessee), for the DANSE project\n\n"
    content += "\"\"\"\n"
    content += "def model():\n"
    content += "    from ScatteringIntensityFactory import ScatteringIntensityFactory\n"
    content += "    from sans.models.%s import %s\n" % (class_name, class_name)
    content += "    return ScatteringIntensityFactory(%s)('%s')\n"\
                 % (class_name, class_name)

    return content

def createODBfiles():
    """
       Create odb files for all available models
    """
    from sans.models.ModelFactory import ModelFactory
    
    class_list = ModelFactory().getAllModels()
    for name in class_list:
        odb = open("sans/models/pyre/%s.odb" % name, 'w')
        odb.write(createODBcontent(name))
        odb.close()
        print "sans/models/pyre/%s.odb created" % name
        
#
# Proceed with installation
#

# First, create the odb files
if len(sys.argv) > 1 and sys.argv[1].lower() == 'odb':
    print "Creating odb files"
    try:
        createODBfiles()
    except:    
        print "ERROR: could not create odb files"
        print sys.exc_value
    sys.exit()

# Then build and install the modules
from distutils.core import setup, Extension


# Build the module name
srcdir  = "sans/models/c_extensions"
igordir = "libigor"

print "Installing SANS models"


setup(
    name="models",
    version = "0.1",
    description = "Python module for SANS scattering models",
    author = "Mathieu Doucet",
    author_email = "doucet@nist.gov",
    url = "http://danse.us/trac/sans",
    
    # Place this module under the sans package
    #ext_package = "sans",
    
    # Use the pure python modules
    package_dir = {"sans_extension":"sans/models/c_extensions"},
    
    packages = ["sans","sans.models","sans.models.test",
                "sans_extension","sans.models.pyre"],
    
    ext_modules = [ Extension("sans_extension.c_models",
     sources = [
        "sans/models/c_models/c_models.cpp",
        #srcdir+"/CSphereModel.c",
        #srcdir+"/sphere.c",
        "sans/models/c_models/CSphereModel.cpp",
        "sans/models/c_models/sphere.cpp",
        #srcdir+"/CCylinderModel.c",
        "sans/models/c_models/CCylinderModel.cpp",
        "sans/models/c_models/cylinder.cpp",
        "sans/models/c_models/parameters.cpp",
        "sans/models/c_models/dispersion_visitor.cpp",
        srcdir+"/cylinder.c",
        #srcdir+"/CCoreShellCylinderModel.c",
        "sans/models/c_models/CCoreShellCylinderModel.cpp",
        "sans/models/c_models/coreshellcylinder.cpp",
        srcdir+"/core_shell_cylinder.c",
        #srcdir+"/CCoreShellModel.c",
        #srcdir+"/core_shell.c",
        "sans/models/c_models/CCoreShellModel.cpp",
        "sans/models/c_models/coreshellsphere.cpp",
        #srcdir+"/CEllipsoidModel.c",
        "sans/models/c_models/CEllipsoidModel.cpp",
        "sans/models/c_models/ellipsoid.cpp",        
        srcdir+"/ellipsoid.c",
        #srcdir+"/CEllipticalCylinderModel.c",
        "sans/models/c_models/CEllipticalCylinderModel.cpp",
        "sans/models/c_models/ellipticalcylinder.cpp",                
        srcdir+"/elliptical_cylinder.c",
        srcdir+"/disperser.c",
        igordir+"/libCylinder.c",
        igordir+"/libSphere.c",
        srcdir+"/gaussian.c",
        srcdir+"/CGaussian.c",
        srcdir+"/lorentzian.c",
        srcdir+"/CLorentzian.c"
            ],
         include_dirs=[igordir,srcdir,"sans/models/c_models"])])
        