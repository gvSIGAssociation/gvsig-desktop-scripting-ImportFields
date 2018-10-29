# encoding: utf-8

import gvsig

from gvsig.libs.formpanel import FormPanel

from org.gvsig.tools import ToolsLocator

class ImportFieldsPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,gvsig.getResource(__file__, "importfields.xml"))
    self.setPreferredSize(400,300)
    self.initComponents()

  def initComponents(self):
    i18n = ToolsLocator.getI18nManager()
  

def showImportFields():
  i18n = ToolsLocator.getI18nManager()
  panel = ImportFieldsPanel()
  panel.showWindow(i18n.getTranslation("_Import_fields"))

def main(*args):
  showImportFields()