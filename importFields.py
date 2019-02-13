# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from org.gvsig.tools.swing.api import ToolsSwingLocator
from javax.swing import DefaultListModel
from java.awt.event import MouseEvent
from javax.swing import ButtonGroup

import sys

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.evaluator import EvaluatorData

from java.lang import Double
from java.net import URI
from org.gvsig.tools import ToolsLocator
from java.util import Date
from java.net import URL
from java.math import BigDecimal
from java.lang import Float
from java.io import File
from org.gvsig.tools.dataTypes import DataTypes
from javax.swing.table import DefaultTableModel
from javax.swing import JTable
from org.gvsig.tools.evaluator import EvaluatorException
from java.lang import Boolean, String
from javax.swing import JScrollPane
from javax.swing import ScrollPaneConstants
from java.awt import BorderLayout
from java.awt.geom import Point2D
from java.lang import Object
from javax.swing import DefaultComboBoxModel


from org.gvsig.fmap.dal.swing import DALSwingLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.app.project.documents.view import ViewDocument
from org.gvsig.app.project.documents.table import TableDocument
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
class MyDefaultTableModel(DefaultTableModel):
  def isCellEditable(self, row, column):
    if column==0:
      return False
    else:
      return True
    
class ImportFieldsSelectTable(JTable):
  def __init__(self, model):
    self.setModel(model)
    
  def getColumnClass(self, column):
    if column==2:
        return Boolean
    else:
        return String

class ImportFieldPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"importFields.xml"))
    self.lastTable = None
    i18Swing = ToolsSwingLocator.getToolsSwingManager()
    
    i18Swing.translate(self.lblFields)
    
    #self.cboTypeReport.removeAllItems()
    i18nManager = ToolsLocator.getI18nManager()
    
    #self.cboTypeReport.addItem(ReportFormatType(i18nManager.getTranslation("_By_table"),0))
    #self.cboTypeReport.addItem(ReportFormatType(i18nManager.getTranslation("_With_two_columns"),1))

    #if layer != None:
    #  self.setLayer(layer)
    swm = DALSwingLocator.getSwingManager()
    
    self.pickerFields1 = swm.createAttributeDescriptorPickerController(self.cmbField1)
    self.pickerFields2 = swm.createAttributeDescriptorPickerController(self.cmbField2)

    allDocuments = self.getAllValidDocuments()
    if len(allDocuments)==0:
      logger("Not able to find 2 tables to execute the tool", LOGGER_INFO)
      return
    self.cmbTable2.setModel(DefaultComboBoxModel(allDocuments))
    if len(allDocuments)>0:
      self.cmbTable2.setSelectedIndex(1)
    else:
      self.cmbTable2.setSelectedIndex(0)
    self.cmbTable1.setModel(DefaultComboBoxModel(allDocuments))
    self.cmbTable1.setSelectedIndex(0)
    ft1 = self.cmbTable1.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    ft2 = self.cmbTable2.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    
    self.pickerFields1.setFeatureType(ft1)
    self.pickerFields2.setFeatureType(ft2)
    self.setLayer(self.cmbTable2.getSelectedItem())
    
  def cmbTable2_change(self,*args):
    newLayer=self.cmbTable2.getSelectedItem()
    self.setLayer(newLayer)
    ft2 = self.cmbTable2.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    self.pickerFields2.setFeatureType(ft2)
    
  def cmbTable1_change(self,*args):
    ft1 = self.cmbTable1.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    self.pickerFields1.setFeatureType(ft1)
    
  def getAllValidDocuments(self):
    application = ApplicationLocator.getManager()
    project = application.getCurrentProject()
    mlayer = gvsig.currentLayer()
    views = project.getDocuments()
    all = []
    for view in views:
      #print view, type(view)
      if isinstance(view, ViewDocument):
          #print view, type(view)
          for layer in view.getMapContext().getLayers():
            #print "--", layer==mlayer, layer.getName()
            all.append(layer)
      elif isinstance(view, TableDocument):
        #print "--", view
        all.append(view)
    return all
  
  def setLayer(self, layer):
    i18nManager = ToolsLocator.getI18nManager()
    columnNames = [
                   i18nManager.getTranslation("_Field_name"),
                   i18nManager.getTranslation("_Name_to_show"),
                   i18nManager.getTranslation("_Show")
                   ]

    featureType = layer.getFeatureStore().getDefaultFeatureType()
    propertyFields = [[attr.getName(), attr.getName(), True] for attr in featureType]
    print propertyFields

    model = MyDefaultTableModel(propertyFields, columnNames)
    table = ImportFieldsSelectTable(model)
    table.setAutoResizeMode(3)

    pane = JScrollPane(table)
    pane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS)
    
    self.jplTable.removeAll()
    self.jplTable.setLayout(BorderLayout())
    self.jplTable.add(pane, BorderLayout.CENTER)
    self.jplTable.repaint()
    self.jplTable.updateUI()
      
  def getFieldsToUse(self):
    table =  self.jplTable.getComponents()[0].getComponents()[0].getComponents()[0]
    data = table.getModel().getDataVector()
    return data
    
def main(*args):
  panel = ImportFieldPanel()
  panel.setPreferredSize(400,300)

  winmgr = ToolsSwingLocator.getWindowManager()
  dialog = winmgr.createDialog(
    panel.asJComponent(),
    "ReportByPoint test",
    "ReportByPoint information",
    winmgr.BUTTONS_OK_CANCEL
  )
  dialog.show(winmgr.MODE.DIALOG)
  if dialog.getAction()==winmgr.BUTTON_OK:
    panel.save()
    print "Ok"
    print "Show field: "
  else:
    print "Cancel"
  