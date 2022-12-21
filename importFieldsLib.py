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
from org.gvsig.tools.namestranslator import NamesTranslator
from org.gvsig.fmap.dal.feature import FeatureStore

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))
   
def main(*args):
    project = gvsig.currentProject() #DefaultProject
    table1 = project.getView(u"Untitled").getLayer("puntos_norep")
    table2 = project.getDocument("tabla")
    field1 = "campo2"
    field2 = "Punto"

    #data = [{'idfield':"Tipo", 'idname': id_generator()}]
    data = [{'idfield':"Tipo", 'idname': id_generator()},
            {'idfield':"Latitud", 'idname':id_generator()}
    ]
    
    processImportFields(table1, field1, table2, field2, data)
    
def processImportFields(tableTarget, fieldTarget, tableSource, fieldSource, data, translator, taskStatus=None):
  fsetTarget = None
  fsetSource = None
  try:
    ### Init processimportfields"
    # Update ft
    #translator = NamesTranslator.createTrimTranslator(11)
    
    
    storeTarget = tableTarget.getFeatureStore()
    storeSource = tableSource.getFeatureStore()
    ftTarget = storeTarget.getDefaultFeatureType()
    ftSource = storeSource.getDefaultFeatureType()
  
    #Names translator init
    #for attr in ftTarget:
    #  translator.addSource(attr.getName())
    #
    if storeTarget==storeSource:
      logger("Can't use same store for import tables", LOGGER_ERROR)
      return
    # Checks
    ## Ningun del nombre de los campos nuevos usados existe ya en la tabla previa
    for d in data:
      used = ftTarget.getAttributeDescriptor(d['idname'])
      if used != None:
        logger("Field "+d['idname'] + " already created in table", LOGGER_ERROR)
        return
  
    # Process
    newftTarget = gvsig.createFeatureType(ftTarget)
    newftSource = gvsig.createFeatureType(ftSource)
  
    featTypeChanged = False
    for d in data:
      name = d["idfield"]
      newname = d["idname"]
      size = d["size"]
      used = ftTarget.getAttributeDescriptor(newname)
      if used != None:
        continue
      descriptor = newftSource.getEditableAttributeDescriptor(name)
      descriptor.setName(newname)
      descriptor.setSize(size)
      newftTarget.addLike(descriptor)
      featTypeChanged = True
    if featTypeChanged:
      try:
        storeTarget.edit()
        storeTarget.update(newftTarget)
        storeTarget.commit()
      except:
        logger("Not able to update feature type", LOGGER_ERROR)
        return


    # Update values
    storeTarget.edit()
    fsetSource = tableSource.getFeatureStore().getFeatureSet()
    
    if taskStatus != None:
      taskStatus.setRangeOfValues(0, fsetSource.getSize())
      taskStatus.setCurValue(0)
      taskStatus.add()
  
    for fSource in fsetSource:
      if taskStatus!=None and taskStatus.isCancellationRequested():
        break
      if taskStatus != None:
        taskStatus.incrementCurrentValue()
      # QUERY
      builder = storeTarget.createExpressionBuilder()
      ## Eq expression
      expFilter = builder.eq(
            builder.column(fieldTarget),
            builder.constant(fSource.get(fieldSource))
            ).toString()
  
      exp = ExpressionEvaluatorLocator.getManager().createExpression()
      exp.setPhrase(expFilter)
      evaluator = DALLocator.getDataManager().createExpresion(exp)
      #filterValue = str(field2)+"="+str(fTarget.get(fieldTarget))
      fqTarget = storeTarget.createFeatureQuery()
      fqTarget.setFilter(evaluator)
      
      #for d in data: #need al attributos to get editable valid
      #  if not ftSource.getAttributeDescriptor(d["idfield"]).isReadOnly():
      #    fq1.addAttributeName(d["idname"])
      #defaultGeometry =  ftTarget.getDefaultGeometryAttributeName()
      #fqTarget.addAttributeName(defaultGeometry)
      fqTarget.retrievesAllAttributes()
      
      # UPDATE VALUES
      fsetTarget = storeTarget.getFeatureSet(fqTarget)
      for ftTarget in fsetTarget:
        efTarget = ftTarget.getEditable()
        for d in data:
          if not newftTarget.getAttributeDescriptor(d["idname"]).isReadOnly():
            value = fSource.get(d["idfield"])
            efTarget.set(d["idname"],value)
        fsetTarget.update(efTarget)
      DisposeUtils.disposeQuietly(fsetTarget)
      if storeTarget.canCommitChanges() and storeTarget.getPendingChangesCount()>100000:
        storeTarget.commitChanges()
    storeTarget.finishEditing()
  except:
    ex = sys.exc_info()[1]
    logger("Not able to update features value: " + str(ex), LOGGER_ERROR)
    DisposeUtils.disposeQuietly(fsetTarget)
    DisposeUtils.disposeQuietly(fsetSource)
    FeatureStore.cancelEditingQuietly(storeTarget)
  finally:
    DisposeUtils.disposeQuietly(fsetSource)
  
  
