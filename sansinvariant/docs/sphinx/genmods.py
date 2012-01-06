from __future__ import with_statement
import os.path

MODULE_TEMPLATE=""".. Autogenerated by genmods.py

******************************************************************************
%(name)s
******************************************************************************

:mod:`%(package)s.%(module)s`
==============================================================================

.. automodule:: %(package)s.%(module)s
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:

"""

INDEX_TEMPLATE=""".. Autogenerated by genmods.py

.. _api-index:

##############################################################################
   %(package_name)s
##############################################################################

.. only:: html

   :Release: |version|
   :Date: |today|

.. toctree::

   %(rsts)s
"""


def genfiles(package, package_name, modules, dir='api'):

    if not os.path.exists(dir):
        os.makedirs(dir)

    for module,name in modules:
        with open(os.path.join(dir,module+'.rst'), 'w') as f:
            f.write(MODULE_TEMPLATE%locals())

    rsts = "\n   ".join(module+'.rst' for module,name in modules)
    with open(os.path.join(dir,'index.rst'),'w') as f:
        f.write(INDEX_TEMPLATE%locals())


modules = []
path = os.path.dirname(os.path.join('..', '..', 'sansinvariant'))
path = os.path.join(path, 'src', 'sans','invariant')
list = os.listdir(path)
for item in list:
    if os.path.isfile(os.path.join(path, item)):
        toks = os.path.splitext(os.path.basename(item))
        if toks[1]=='.py' and toks[0] not in ["__init__", "setup"]:
            exec "module = ('%s', '%s')"%(toks[0], toks[0])
            modules.append(module)
package="sans.invariant"
package_name='Reference'
#genfiles(package, package_name, modules)

if __name__ == "__main__":
    genfiles(package, package_name, modules, dir='api')
    print "Sphinx: generate .rst files complete..."