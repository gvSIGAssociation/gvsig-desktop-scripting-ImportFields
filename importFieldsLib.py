# encoding: utf-8

import gvsig
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from org.gvsig.tools.dispose import DisposeUtils

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.fmap.dal import DALLocator
import sys

def main(*args):
    project = gvsig.currentProject() #DefaultProject
    table1 = project.getView("Untitled").getLayer("ny")
    table2 = project.getDocument("tipos")
    field1 = "ADDR_PCT_C"
    field2 = "PK"
    data = [{'idfield':"TIPO", 'idname': "TIPO5", 'use':True}]
    
    processImportFields(table1, field1, table2, field2, data)
    
def processImportFields(table1, field1, table2, field2, data, taskStatus=None):
  ### Init processimportfields"
  # Update ft
  store1 = table1.getFeatureStore()
  store2 = table2.getFeatureStore()
  ft1 = store1.getDefaultFeatureType()
  ft2 = store2.getDefaultFeatureType()
  # Checks
  ## Ningun del nombre de los campos nuevos usados existe ya en la tabla previa
  for d in data:
    if d['use']==True:
      used = ft1.getAttributeDescriptor(d['idname'])
      if used != None:
        logger("Field "+d['idname'] + " already created in table", LOGGER_ERROR)
        return

  # Process
  newft1 = gvsig.createFeatureType(ft1)
  newft2 = gvsig.createFeatureType(ft2)

  for d in data:
    if d["use"]==False: continue
    name = d["idfield"]
    descriptor = newft2.getEditableAttributeDescriptor(name)
    newname = d["idname"]
    descriptor.setName(newname)
    newft1.addLike(descriptor)

  
  try:
    store1.edit()
    store1.update(newft1)
    store1.commit()
  except:
    logger("Not able to update feature type", LOGGER_ERROR)
    return

  # Update values
  try:
    fset2 = store2.getFeatureSet()
    store1.edit()
    if taskStatus != None:
      taskStatus.setRangeOfValues(0, fset2.getSize())
      taskStatus.setCurValue(0)
      taskStatus.add()
    
    for f2 in fset2:
      if taskStatus.isCancellationRequested():
        break
      if taskStatus != None:
        taskStatus.incrementCurrentValue()
      builder = store1.createExpressionBuilder()
      #expFilter = builder.eq(str(field2), f1.get(field1)).toString()
      expFilter = str(field1) + "=" + str(f2.get(field2))
      exp = ExpressionEvaluatorLocator.getManager().createExpression()
      exp.setPhrase(expFilter)
      evaluator = DALLocator.getDataManager().createExpresion(exp)
      #filterValue = str(field2)+"="+str(f1.get(field1))
      fq1 = store1.createFeatureQuery()
      fq1.setFilter(evaluator)
      #for d in data: #need al attributos to get editable valid
      #  if d["use"]==False: continue
      #  fq1.addAttributeName(d["idname"])
      fq1.retrievesAllAttributes()
      fset1 = store1.getFeatureSet(fq1)
      for f1 in fset1:
        ef1 = f1.getEditable()
        for d in data:
          if d["use"]==False: continue
          value = f2.get(d["idfield"])
          ef1.set(d["idname"],value)
        fset1.update(ef1)
      if store1.getPendingChangesCount()>100000:
        store1.commitChanges()
    store1.commit()
  except:
    ex = sys.exc_info()[1]
    logger("Not able to update features value: " + str(ex), LOGGER_ERROR)
    try:
      store1.cancelEditing()
    except:
      logger("Not able to cancel editing", LOGGER_ERROR)
  finally:
    DisposeUtils.disposeQuietly(fset1)
  
  
