# encoding: utf-8

import gvsig
from importFields import ImportFieldPanel
from importFieldsLib import processImportFields
from java.awt.event import ActionListener
from org.gvsig.app.project.documents.table.gui import FeatureTableDocumentPanel
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager
from org.gvsig.app.project.documents.view import DefaultViewDocument
from org.gvsig.tools import ToolsLocator
import thread

from org.gvsig.app.project.documents.table import TableDocument

def main(*args):
  store1 = gvsig.currentLayer().getFeatureStore()
  builder = store1.createExpressionBuilder()
    
def testEnabledDocuments(*args):
  if gvsig.currentProject().getDocuments()>1:
    for doc in gvsig.currentProject().getDocuments():
      if isinstance(doc,FeatureTableDocumentPanel):
        print True
      elif isinstance(doc,TableDocument):
        print True
      elif isinstance(doc, DefaultViewDocument):
        layers = doc.getMapContext().hasLayers()
        return True
      print doc, type(doc)
  print False