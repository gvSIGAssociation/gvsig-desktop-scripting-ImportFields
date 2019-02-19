# encoding: utf-8

import gvsig
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from org.gvsig.tools.dispose import DisposeUtils

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.fmap.dal import DALLocator
import sys
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))
   
def main(*args):
    project = gvsig.currentProject() #DefaultProject
    table1 = project.getView("Untitled").getLayer("templayer")
    table2 = project.getDocument("tipos")
    field1 = "TIPO"
    field2 = "TIPO"

   
    data = [{'idfield':"Field1", 'idname': id_generator()},
            {'idfield':"Field2", 'idname':id_generator()}
    ]
    
    processImportFields(table1, field1, table2, field2, data)
    
def processImportFields(table1, field1, table2, field2, data, taskStatus=None):
  ### Init processimportfields"
  # Update ft
  store1 = table1.getFeatureStore()
  store2 = table2.getFeatureStore()
  ft1 = store1.getDefaultFeatureType()
  ft2 = store2.getDefaultFeatureType()
  if store1==store2:
    logger("Can't use same store for import tables", LOGGER_ERROR)
    return
  # Checks
  ## Ningun del nombre de los campos nuevos usados existe ya en la tabla previa
  for d in data:
    used = ft1.getAttributeDescriptor(d['idname'])
    if used != None:
      logger("Field "+d['idname'] + " already created in table", LOGGER_ERROR)
      return

  # Process
  newft1 = gvsig.createFeatureType(ft1)
  newft2 = gvsig.createFeatureType(ft2)

  for d in data:
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
  store1.edit()
  fset2 = table2.getFeatureStore().getFeatureSet()
  
  if taskStatus != None:
    taskStatus.setRangeOfValues(0, fset2.getSize())
    taskStatus.setCurValue(0)
    taskStatus.add()

  for f2 in fset2:
    if taskStatus!=None and taskStatus.isCancellationRequested():
      break
    if taskStatus != None:
      taskStatus.incrementCurrentValue()
    # QUERY
    builder = store1.createExpressionBuilder()
    ## Eq expression
    expFilter = builder.eq(
          builder.column(field1),
          builder.constant(f2.get(field2))
          ).toString()

    exp = ExpressionEvaluatorLocator.getManager().createExpression()
    exp.setPhrase(expFilter)
    evaluator = DALLocator.getDataManager().createExpresion(exp)
    #filterValue = str(field2)+"="+str(f1.get(field1))
    fq1 = store1.createFeatureQuery()
    fq1.setFilter(evaluator)
    
    #for d in data: #need al attributos to get editable valid
    #  if not ft2.getAttributeDescriptor(d["idfield"]).isReadOnly():
    #    fq1.addAttributeName(d["idname"])
    #defaultGeometry =  ft1.getDefaultGeometryAttributeName()
    #fq1.addAttributeName(defaultGeometry)
    fq1.retrievesAllAttributes()
    
    # UPDATE VALUES
    fset1 = store1.getFeatureSet(fq1)
    for f1 in fset1:
      ef1 = f1.getEditable()
      for d in data:
        if newft1.getAttributeDescriptor(d["idname"]).isReadOnly():
          #logger("Field is read only", LOGGER_WARN) 
          continue
        value = f2.get(d["idfield"])
        ef1.set(d["idname"],value)
      fset1.update(ef1)
    if store1.canCommitChanges() and store1.getPendingChangesCount()>100000:
      store1.commitChanges()
  store1.commit()
  try:
    pass
  except:
    ex = sys.exc_info()[1]
    logger("Not able to update features value: " + str(ex), LOGGER_ERROR)
    try:
      DisposeUtils.disposeQuietly(fset1)
      DisposeUtils.disposeQuietly(fset2)
      store1.cancelEditing()
    except:
      logger("Not able to cancel editing", LOGGER_ERROR)
  finally:
    DisposeUtils.disposeQuietly(fset1)
    DisposeUtils.disposeQuietly(fset2)
  
  
