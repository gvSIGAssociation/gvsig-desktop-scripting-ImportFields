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
from java.lang import Boolean, String, Integer
from javax.swing import JScrollPane
from javax.swing import ScrollPaneConstants
from java.awt import BorderLayout
from java.awt.geom import Point2D
from java.lang import Object
from javax.swing import DefaultComboBoxModel
from org.gvsig.tools.namestranslator import NamesTranslator
from org.gvsig.fmap.mapcontext.layers.vectorial import FLyrVect
from org.gvsig.fmap.dal.swing import DALSwingLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.app.project.documents.view import ViewDocument
from org.gvsig.app.project.documents.table import TableDocument
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from addons.ImportFields.importFieldsLib import processImportFields
from javax.swing import JTable
from javax.swing.table import AbstractTableModel
from org.gvsig.tools.swing.api.windowmanager import WindowManager
import thread

class ImportAttribute():
  def __init__(self, attr, nameTranslator):
    self.attr = attr #DefaultEditableFeatureAttributeDescriptor
    self.nameTranslator = nameTranslator
    self.toImport = True
    self.size = attr.getSize()
  def getName(self):
    return self.attr.getName()
  def getNewName(self):
    return self.nameTranslator.getAllTranslations(self.attr.getName())[-1]
  def setImport(self, toImport):
    self.toImport = toImport
  def getImport(self):
    return self.toImport
  def setNewName(self, newName, translatorIndexesSecondFt, blockedFieldNames):
    sourceIndex = translatorIndexesSecondFt[self.getName()]
    if (newName in blockedFieldNames):
      return
    self.nameTranslator.setTranslation(sourceIndex, newName)
  def setSize(self, size):
    self.size = size
  def getSize(self):
    return self.size

    
class MyDefaultTableModel(AbstractTableModel):
  def __init__(self, panel, attributes, translator, translatorIndexesSecondFt, blockedFieldNames, columnNames):
    self.attributes = attributes
    self.translator = translator
    self.columnNames = columnNames
    self.panel = panel
    if translatorIndexesSecondFt == None:
      translatorIndexesSecondFt = {}
    self.translatorIndexesSecondFt = translatorIndexesSecondFt
    if blockedFieldNames == None:
      blockedFieldNames = []
    self.blockedFieldNames = blockedFieldNames
  
  def getData(self):
    data = []
    for attr in self.attributes:
      lstAttr = []
      lstAttr.append(attr.getName())
      lstAttr.append(attr.getNewName())
      lstAttr.append(attr.getImport())
      lstAttr.append(attr.getSize())
      data.append(lstAttr)
    return data
  
  def setValueAt(self, aValue, rowIndex, columnIndex):
    myattr = self.attributes[rowIndex]
    if (columnIndex == 1):
      if (aValue in self.blockedFieldNames):
         i18nManager = ToolsLocator.getI18nManager()
         self.panel.messageController.setText(i18nManager.getTranslation("_Field_already_exists_in_base_layer")+": "+aValue)
         return
      myattr.setNewName(aValue, self.translatorIndexesSecondFt, self.blockedFieldNames)
    elif (columnIndex == 2):
      myattr.setImport(aValue)
    elif (columnIndex == 3):
      myattr.setSize(aValue)
      
  def getValueAt(self, rowIndex, columnIndex):
    myattr = self.attributes[rowIndex]
    if (columnIndex == 0):
      return myattr.getName()
    elif (columnIndex == 1):
      return myattr.getNewName()
    elif (columnIndex == 2):
      return myattr.getImport()
    elif (columnIndex == 3):
      return myattr.getSize()
    return None
    
  def isCellEditable(self, row, column):
    if column==0:
      return False
    else:
      return True

  def getColumnName(self, columnIndex):
    return self.columnNames[columnIndex]
    
  def getColumnClass(self, column):
    if column==2:
      return Boolean
    elif column==3:
      return Integer
    else:
      return String
      
  def getRowCount(self):
    return len(self.attributes)
    
  def getColumnCount(self):
    return len(self.columnNames)
    
class ImportFieldPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"importFields.xml"))
    self.lastTable = None
    i18Swing = ToolsSwingLocator.getToolsSwingManager()
    self.ft1 = None
    self.ft2 = None
    self.blockedNames = []
    
    i18Swing.translate(self.lblImportFields)
    i18Swing.translate(self.lblTable1)
    i18Swing.translate(self.lblField1)
    i18Swing.translate(self.lblTable2)
    i18Swing.translate(self.lblField2)
    
    swm = DALSwingLocator.getSwingManager()
    
    self.pickerFields1 = swm.createAttributeDescriptorPickerController(self.cmbField1)
    self.pickerFields2 = swm.createAttributeDescriptorPickerController(self.cmbField2)
    self.messageController = ToolsSwingLocator.getToolsSwingManager().createMessageBarController(self.lblMessage, 10000);

    allDocuments = self.getAllValidDocuments(None)
    if len(allDocuments)<2:
      logger("Not able to find 2 tables to execute the tool", LOGGER_INFO)
      return
    self.cmbTable1.setModel(DefaultComboBoxModel(allDocuments))
    self.cmbTable1.setSelectedIndex(0)
    self.cmbTable1_change()
    self.ft1 = self.cmbTable1.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    self.ft2 = self.cmbTable2.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    
    self.pickerFields1.setFeatureType(self.ft1)
    self.pickerFields2.setFeatureType(self.ft2)
    self.setLayer(self.cmbTable2.getSelectedItem())
    self.regenerateTranslator()
    self.setPreferredSize(400,300)
    
    
  def cmbTable2_change(self,*args):
    newLayer=self.cmbTable2.getSelectedItem()
    self.regenerateTranslator()
    self.setLayer(newLayer)
    self.ft2 = self.cmbTable2.getSelectedItem().getFeatureStore().getDefaultFeatureType()
    self.pickerFields2.setFeatureType(self.ft2)
    
    
  def cmbTable1_change(self,*args):
    table1Item =  self.cmbTable1.getSelectedItem()
    self.ft1 = table1Item.getFeatureStore().getDefaultFeatureType()
    allDocuments = self.getAllValidDocuments(table1Item)
    model = DefaultComboBoxModel(allDocuments)
    self.cmbTable2.setModel(model)
    if len(allDocuments)>1:
      self.cmbTable2.setSelectedIndex(1)
    else:
      self.cmbTable2.setSelectedIndex(0)
    self.cmbTable2_change()
    
    self.regenerateTranslator()
    self.pickerFields1.setFeatureType(self.ft1)
    
     
  def regenerateTranslator(self):
     self.translatorIndexesSecondFt = {}
     self.translator = NamesTranslator.createTrimTranslator(10)
     self.blockedNames = []
     if (self.ft1!=None):
       for attr in self.ft1:
         self.translator.addSource(attr.getName())
         self.blockedNames.append(attr.getName())
     if (self.ft2!=None):
       for attr in self.ft2:
          position = self.translator.addSource(attr.getName())
          self.translatorIndexesSecondFt[attr.getName()] = position
       
  def getAllValidDocuments(self, documentException=None):
    application = ApplicationLocator.getManager()
    project = application.getCurrentProject()
    mlayer = gvsig.currentLayer()
    docs = project.getDocuments()
    all = []
    try:
      for doc in docs:
        #print doc, type(doc)
        if isinstance(doc, ViewDocument):
            for layer in doc.getMapContext().getLayers():
              #print "--", layer==mlayer, layer.getName()
              if isinstance(layer, FLyrVect):
                if documentException!=layer:
                  all.append(layer)
        elif isinstance(doc, TableDocument):
          #print "--", doc
          if doc.getAssociatedLayer()==None:
            if documentException!=doc:
                all.append(doc)
    except :
      ex = sys.exc_info()[1]
      print "Error", ex.__class__.__name__, str(ex)

    return all
  
  def setLayer(self, layer):
    i18nManager = ToolsLocator.getI18nManager()
    columnNames = [
                   i18nManager.getTranslation("_Field"),
                   i18nManager.getTranslation("_Target_field_name"),
                   i18nManager.getTranslation("_Import"),
                   i18nManager.getTranslation("_Size")
                   ]

    featureType = layer.getFeatureStore().getDefaultFeatureType()
    #propertyFields = [[attr.getName(), attr.getName(), True] for attr in featureType]

    propertyFields = []
    for attr in featureType:
      eAttr = DALLocator.getDataManager().createFeatureAttributeDescriptor(attr.getName(), attr.getType())
      eAttr.copyFrom(attr.getCopy())
      propertyFields.append(ImportAttribute(eAttr, self.translator))
    
    model = MyDefaultTableModel(self, propertyFields, self.translator, self.translatorIndexesSecondFt, self.blockedNames, columnNames)
    self.tblFields.setModel(model)
    
  def getFieldsToUse(self):
    data = self.tblFields.getModel().getData()
    #print "DATA:", data
    newdata = []
    for d in data:
      newdic = {}
      if d[2]==True:
        newdic['idfield'] = d[0]
        newdic['idname'] = d[1]
        newdic['size'] = d[3]
        newdata.append(newdic)
    print "FIELTOUSE:", newdata
    return newdata
    
  def getTable1(self):
    return self.cmbTable1.getSelectedItem()
  def getTable2(self):
    return self.cmbTable2.getSelectedItem()
  def getField1(self):
    return self.pickerFields1.get()
  def getField2(self):
    return self.pickerFields2.get()
  def getTranslator(self):
    return self.translator

  def process(self, dialog, taskStatus):
    winmgr = ToolsSwingLocator.getWindowManager()
    if dialog.getAction()==winmgr.BUTTON_CANCEL:
      taskStatus.terminate()
      return
    if dialog.getAction()==winmgr.BUTTON_OK:
      table1 = self.getTable1()
      table2 = self.getTable2()
      field1 = self.getField1().getName()
      field2 = self.getField2().getName()
  
      data = self.getFieldsToUse()
      translator = self.getTranslator()
      thread.start_new_thread(self.__process, (table1, field1, table2, field2, data, translator, taskStatus))
    

  def __process(self, table1, field1, table2, field2, data, translator, taskStatus):
    processImportFields(table1, field1, table2, field2, data, translator, taskStatus)
    taskStatus.terminate()


def main(*args):
    panel = ImportFieldPanel()
    i18nManager = ToolsLocator.getI18nManager()
    winmgr = ToolsSwingLocator.getWindowManager()
    taskStatus = ToolsLocator.getTaskStatusManager().createDefaultSimpleTaskStatus(i18nManager.getTranslation("_Import_fields"))
    taskStatus.setAutoremove(True)
    
    dialog = winmgr.createDialog(
      panel.asJComponent(),
      i18nManager.getTranslation("_Import_fields"),
      i18nManager.getTranslation("_Select_fields_to_import_into_table"),
      winmgr.BUTTONS_OK_CANCEL
    )
    dialog.addActionListener(lambda e:panel.process(dialog, taskStatus))
    dialog.show(WindowManager.MODE.WINDOW)
  
