import json
import os
from .BaseServer import AduneoError
from .BaseServer import BaseHandler
from .Configuration import Configuration

class Help(BaseHandler):
  
  help_json = None
  
  
  def help_window_definition():
    
    """Retourne le code HTML et Javascript de la fenêtre d'affichage de l'aide
    
    :return: code HTML
    :rtype: str
    
    .. notes::
      mpham 23/04/2021
    """
    
    return """
      <link rel="stylesheet" href="/css/dragWindow.css">
      <script src="/javascript/help.js"></script>
    
      <div id="helpWindow" class="dragWindow" onmousedown="startDrag(this, event)">
        <div class="dragHeader"><span id="helpHeader"></span><span style="float: right; cursor: pointer;" onclick="closeDrag(this)">&#x2716;</span></div>
        <div id="helpContent" class="dragContent">
        </div>
      </div>
      """

  
  def send_help(self):
    
    """
    Retourne les rubriques d'aide sous forme de JSON
      "header": "..."
      "content" : "...'
      
    mpham 13/04/2021
    """
  
    help_id = self.get_query_string_param('id', '')
    
    Help.help_json = None
    if Help.help_json is None:
    
      conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
      help_filepath = conf_dir+'/help.json'

      with open(help_filepath, encoding='utf8') as json_file:
        Help.help_json = json.load(json_file)

    help_item = Help.help_json.get(help_id)
    if help_item is None:
      raise AduneoError('help entry '+help_id+' not found in help.json')

    language = 'en'
      
    response = {}
    response['header'] = help_item.get('header_'+language)
    response['content'] = help_item.get('content_'+language)

    self.send_json(response)
