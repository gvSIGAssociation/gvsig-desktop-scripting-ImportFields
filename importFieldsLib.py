# encoding: utf-8

import gvsig
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR
from org.gvsig.tools.dispose import DisposeUtils

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.fmap.dal import DALLocator

def main(*args):
    project = gvsig.currentProject() #DefaultProject
    table1 = project.getView("Untitled").getLayer("lineas")
    table2 = project.getDocument("tipos")
    field1 = "ID"
    field2 = "PK"
    data = [{'idfield':'PK','idname': 'PKN', 'use':False},
        {'idfield':"TIPO", 'idname': "TIPON", 'use':True},
        {'idfield':"NOMBRE", 'idname': "NOMBREN",'use':False}]
    
    processImportFields(table1, field1, table2, field2, data)
    
def processImportFields(table1, field1, table2, field2, data):
  print "### Init processimportfields"
  print table1, field1, table2, field2, data

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
  fset1 = store1.getFeatureSet()
  store1.edit()
  for f1 in fset1:
    builder = store1.createExpressionBuilder()
    #expFilter = builder.eq(str(field2), f1.get(field1)).toString()
    expFilter = str(field2) + "=" + str(f1.get(field1))
    exp = ExpressionEvaluatorLocator.getManager().createExpression()
    exp.setPhrase(expFilter)
    evaluator = DALLocator.getDataManager().createExpresion(exp)
    #filterValue = str(field2)+"="+str(f1.get(field1))
    fq2 = store2.createFeatureQuery()
    fq2.setFilter(evaluator)
    fq2.retrievesAllAttributes()
    feature2 = store2.getFeatureSet(fq2).first()
    if feature2 != None:
      ef1 = f1.getEditable()
      for d in data:
        if d["use"]==False: continue
        value = feature2.get(d["idfield"])
        ef1.set(d["idname"],value)
      fset1.update(ef1)
  store1.commit()
  
  DisposeUtils.disposeQuietly(fset1)
  
  
