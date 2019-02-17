# encoding: utf-8

import gvsig

from gvsig import getResource

from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from addons.ImportFields.importFieldsExtension import ImportFieldsExtension

def selfRegister():
  application = ApplicationLocator.getManager()

  #
  # Registramos las traducciones
  i18n = ToolsLocator.getI18nManager()
  i18n.addResourceFamily("text",File(getResource(__file__,"i18n")))

  #
  # Registramos los iconos en el tema de iconos
  icon = File(getResource(__file__,"images","table-import-fields.png")).toURI().toURL()
  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  iconTheme.registerDefault("scripting.ImportFieldsExtension", "action", "table-import-fields", None, icon)

  #
  # Creamos la accion 
  extension = ImportFieldsExtension()
  actionManager = PluginsLocator.getActionInfoManager()
  action = actionManager.createAction(
    extension, 
    "table-import-fields", # Action name
    "_Import_fields", # Text
    "table-import-fields", # Action command
    "table-import-fields", # Icon name
    None, # Accelerator
    508200000, # Position 
    "_Show_the_import_fields_dialog" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "Table/_Import_fields")
  

      
