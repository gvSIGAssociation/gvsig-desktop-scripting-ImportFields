# encoding: utf-8

import gvsig

from importFields import ImportFieldPanel
from importFieldsLib import processImportFields
from java.awt.event import ActionListener
from org.gvsig.app.project.documents.table.gui import FeatureTableDocumentPanel
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager
from org.gvsig.app.project.documents.table import TableManager
from org.gvsig.tools import ToolsLocator
import thread

from org.gvsig.app.project.documents.table import TableDocument

from org.gvsig.app.project.documents.view import DefaultViewDocument

def main(*args):

  ImportFieldsExtension().execute(None)

class ImportFieldsExtension(ScriptingExtension, ActionListener):
  def __init__(self):
    self.working = False
    
  def canQueryByAction(self):
    return True

  def isEnabled(self,action):
    #if gvsig.currentProject().getDocuments()>1:
    #  for doc in gvsig.currentProject().getDocuments():
    #    if isinstance(doc,FeatureTableDocumentPanel):
    #      return True
    #    elif isinstance(doc,TableDocument):
    #      return True
    #    elif isinstance(doc, DefaultViewDocument):
    #      layers = doc.getMapContext().hasLayers()
    #      return True
    #return False
    if gvsig.currentDocument(TableManager.TYPENAME)!=None:
      doc = gvsig.currentDocument(TableManager.TYPENAME).getMainWindow()
      return isinstance(doc, FeatureTableDocumentPanel)
    return False
    
  def isVisible(self,action):
    #if gvsig.currentProject().getDocuments()>1:
    #  for doc in gvsig.currentProject().getDocuments():
    #    if isinstance(doc,FeatureTableDocumentPanel):
    #      return True
    #    elif isinstance(doc,TableDocument):
    #      return True
    #    elif isinstance(doc, DefaultViewDocument):
    #      layers = doc.getMapContext().hasLayers()
    #      return True
    #return False
    if gvsig.currentDocument(TableManager.TYPENAME)!=None:
      doc = gvsig.currentDocument(TableManager.TYPENAME).getMainWindow()
      return isinstance(doc, FeatureTableDocumentPanel)
    return False
    
  def execute(self,actionCommand, *args):
    self.panel = ImportFieldPanel()
    self.panel.setPreferredSize(400,300)
    i18nManager = ToolsLocator.getI18nManager()
    winmgr = ToolsSwingLocator.getWindowManager()
    self.taskStatus = ToolsLocator.getTaskStatusManager().createDefaultSimpleTaskStatus(i18nManager.getTranslation("_Import_fields"))
    self.taskStatus.setAutoremove(True)
    
    self.dialog = winmgr.createDialog(
      self.panel.asJComponent(),
      i18nManager.getTranslation("_Import_fields"),
      i18nManager.getTranslation("_Select_fields_to_import_into_table"),
      winmgr.BUTTONS_OK_CANCEL
    )
    self.dialog.addActionListener(self)
    self.dialog.show(WindowManager.MODE.WINDOW)
    
  def actionPerformed(self,*args):
    winmgr = ToolsSwingLocator.getWindowManager()
    if self.dialog.getAction()==winmgr.BUTTON_CANCEL:
      self.taskStatus.terminate()
      return
    if self.dialog.getAction()==winmgr.BUTTON_OK:
      table1 = self.panel.getTable1()
      table2 = self.panel.getTable2()
      field1 = self.panel.getField1().getName()
      field2 = self.panel.getField2().getName()
  
      data = self.panel.getFieldsToUse()
      translator = self.panel.getTranslator()
      thread.start_new_thread(self.process, (table1, field1, table2, field2, data, translator))
    

  def process(self, table1, field1, table2, field2, data, translator):
    processImportFields(table1, field1, table2, field2, data, translator, self.taskStatus)
    self.taskStatus.terminate()
  