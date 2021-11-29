# -*- coding: utf-8 -*-

from imgs import *
#from locales import *

# Importacoes do google colab
from google.colab import drive
from google.colab import widgets as colabwidigets

# Importações Ipywidigets
from ipywidgets import widgets as ipywidgets

# Importações Fastai
from fastai.data.all import *
from fastai.vision.core import *
from fastai.vision import *
from fastai.vision.all import *
from fastai.vision.widgets import *

# Geral
from PIL import Image
import os
import progressbar
import time
import matplotlib.pyplot as plt
import numpy as np

import sys
import gettext

global DIRETORIO_LOCAL

DIRETORIO_LOCAL = os.path.join('/content/', 'locales')
_ = gettext.gettext

def change_lang(lang = 'en'):
    gt = gettext.translation('base', DIRETORIO_LOCAL, languages=[lang])
    gt.install()
    global _
    _ = gt.gettext


# Conexão com o Google Drive
def drive_connect():
  drive.mount('/content/gdrive', force_remount=True)
  drive_connect.root_dir = "/content/gdrive/My Drive"
  print(_('Google Drive conectado com sucesso'))

# Layout e Style
l_txt = ipywidgets.Layout(width='66%')
l_btn = ipywidgets.Layout(width='33%')
l_vbox = ipywidgets.Layout(width='720px')
l_hbox = ipywidgets.Layout(width='90%')
l_req = ipywidgets.Layout(width='95%', height='90px')
l_hidden_red = ipywidgets.Layout(width='90%', visibility = 'hidden')
l_hidden_tra = ipywidgets.Layout(width='90%', visibility = 'hidden')
l_btn_hbox = ipywidgets.Layout(flex_flow='column',align_items='center')
s_desc_wid = {'description_width':'25%'}

# Classes para textos e retornos padronizados
# Texto com link e ancora p/ documentação
class m_Header():
  def __init__(self, header):
        self.header = ipywidgets.HTML(value='<p style=font-family:Arial><b>' + header + '<b/> <a target="_blank" href="https://github.com/gutofranz/colab_visual_layer/blob/main/hints/hints.md#' + header.replace(' ', '-').lower() + '">?</a><p>')
# Mensagem de retorno
class m_Ret():
  def __init__(self, txt, flag):
    if flag == 1:
      self.txt = ipywidgets.HTML(value='<p style="text-align: left;style=font-family:Arial"><span style="color: #339966;">' + txt + '</span></p>')
    if flag == 2:
      self.txt = ipywidgets.HTML(value='<p style="text-align: left;style=font-family:Arial"><span style="color: #ff0000;">' + txt + '</span></p>')

# Função principal
def visual_layer():

  drive_connect()

  # Garante que as variaveis estarão limpas
  _path = None
  _Path = None
  _dls = None
  _learn = None
  _interp = None
  
  pass #display(ipywidgets.Image(value=open("/content/0.png", "rb").read(),format='png')) # Header
    
  # Função para definição do Path
  def build_path(path_f):
    nonlocal _path
    nonlocal _Path
      
    if path_f == "":
      _path = None
      _Path = None

      nonlocal _dls
      _dls = None

      nonlocal _learn
      _learn = None

      nonlocal _interp
      _interp = None

    else:
      _path = path_f
      _Path = Path(path_f) 
        
  # Função para a criação do DataLoader
  def build_data(path_fun, splitter_percent_validation, splitter_bs):
      nonlocal _dls

      data = get_image_files(path_fun)

      # Splitter
      splitter = RandomSplitter(valid_pct=splitter_percent_validation,seed=40)
      splitter(data)
          
      # Transformações:
      ## Dos Itens
      if cb_disable_tfms.value:
        item_tfms = Resize(224, 'squish')
      else:
        item_tfms = [Resize(item_tfms_resize.value, method=item_tfms_resize_mtd.value)]   
      
      ## Do Batch
      if cb_disable_aug.value:
        batch_tfms = None
      else:
        batch_tfms = [*aug_transforms(mult=slider_aug_tfms_multi.value,do_flip=tb_do_flip.value,flip_vert=tb_do_vert.value,max_rotate=sl_Max_Rotate.value,min_zoom=sl_Min_Zoom.value,max_zoom=sl_Max_Zoom.value,max_lighting=sl_Max_Lighting.value,max_warp=sl_Max_warp.value,p_lighting=sl_p_lighting.value,size=224,pad_mode=tb_pad_mode.value), Normalize.from_stats(*imagenet_stats)]

      # Criação do DataBlock
      blocks=(ImageBlock,CategoryBlock)
      
      get_image_files(path_fun)    
      dblock = DataBlock(blocks=blocks,get_items=get_image_files,splitter=splitter,get_y=parent_label,item_tfms=item_tfms,batch_tfms=batch_tfms)
          
      # Criação do DataLoader
      _dls = dblock.dataloaders(path_fun, bs=splitter_bs)
    
  # Função para a criação do Learner    
  def create_learner(model_architecture):
    _metrics = []
    if cb_error_rate.value:
        _metrics.append(error_rate)
    if cb_accuracy.value: 
        _metrics.append(accuracy)

    # Definição dos Callbacks
    defaults.callbacks[1] = Recorder(train_metrics=True)
    defaults.callbacks
    #cbs=[ShowGraphCallback,ActivationStats(with_hist=True),SaveModelCallback(monitor='accuracy')] # esta apresentando erro
    cbs=[ShowGraphCallback,ActivationStats(with_hist=True),SaveModelCallback()]

    # Criação do learner
    nonlocal _learn
    _learn = cnn_learner(_dls,model_architecture,metrics=_metrics,cbs=cbs)

  # Função para a realização do treinamento, cria o Interp após a realização
  def train_data(epochs):
    cbs=[ShowGraphCallback,ActivationStats(with_hist=True),SaveModelCallback()] #monitor='accuracy'
    _learn.fit_one_cycle(epochs,5e-3,cbs=cbs)
    nonlocal _interp 
    _interp = ClassificationInterpretation.from_learner(_learn)

  # Função que converte as imagens em jpg
  def jpg_converter(path):
    if path == "":
      path = _Path 
    listy = os.listdir(path)
    for file in progressbar.progressbar(listy):
        if os.path.isdir(str(path)+"/"+file):
            jpg_converter(str(path)+"/"+file)
        elif not file.split(".")[1] == "jpg":
            Image.open(path + "/" + file).convert('RGB').save("{0}/{1}.jpg".format(path,file.split(".")[0]))

  def total_by_category():
    listy = _Path.ls()
    total = 0
    dicty = {}
    for i in listy:
      if os.path.isdir(i):
        total +=len(os.listdir(i))
        stuff = str(i).split("/")
        dicty[stuff[len(stuff)-1]] = len(os.listdir(i))

    chart_labels = [] 
    chart_quantities = []
    for i in dicty:
      chart_labels.append(i)
      chart_quantities.append(dicty[i])

    x = np.arange(len(chart_labels))
    width = 0.5 
    fig, ax = plt.subplots()
    rects = ax.bar(x, chart_quantities, width)
    ax.set_ylabel(_('Quantidade'))
    ax.set_title(_('Quantidade por categoria'))
    ax.set_xticks(x)
    ax.set_xticklabels(chart_labels)
    ax.set_frame_on(False)
    
    def autolabel(rects):
      """Attach a text label above each bar in *rects*, displaying its height."""
      for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    autolabel(rects)
    opt = ipywidgets.Output()
    with opt:
      plt.show()
    
    i = [opt]
    display(ipywidgets.VBox(i, layout=l_vbox))

  # Criação do painel que vai conter as abas
  tab = colabwidigets.TabBar([_('Análise de requisitos'),_('Preparação de dados'),_('Transfer learning'),_('Avaliação transfer learning'),_('Fine tuning (opcional)'), _('Avaliação fine tuning (opcional)'),_('Predição'), _('Exportação')])

  # Primeira aba: Análise de Requisitos
  with tab.output_to(0, select=False): #):  
    grid0 = colabwidigets.Grid(2,1)

    # Atividade - Exportar modelo
    with grid0.output_to(0,0):
      pass #display(ipywidgets.Image(value=open("/content/2.png", "rb").read(),format='png', layout=l_vbox))

    # Atividade - Exportar modelo
    with grid0.output_to(1,0):

      lbl_tarefa = m_Header(_("Tarefa"))
      txta_tarefa = ipywidgets.Textarea(value='',placeholder=_("Descreva a tarefa \nex. Classificação de imagens aplicado a classificação de seis espécies de árvores nativas de Santa Catarina."),disabled=False,layout=l_req)
      
      lbl_tipotarefa = m_Header(_('Tipo da tarefa'))
      txta_tipotarefa = ipywidgets.Textarea(value='',placeholder=_('Descreva o tipo da tarefa \nex. Single-label classificação de imagens'),disabled=False,layout=l_req)

      lbl_cat = m_Header(_('Categorias'))
      txta_cat1 = ipywidgets.Textarea(value='',placeholder=_('Descrição das categorias \nex. 6 categorias de espécies de árvores nativas/endêmicas de SC/Brasil (Aroeira-vermelha, Capororoca, Embaúba, Jerivá, Mulungu, Pitangueira Experiência) Conjunto de imagens de árvores (tipicamente a vista da árvore toda ou partes dentro do habitat natural (rua, praça, parque etc.)'),disabled=False,layout=l_req)

      lbl_fontededados = m_Header(_('Fonte de dados'))
      txta_fontededados = ipywidgets.Textarea(value='',placeholder=_('Descreva a fonte de dados \nex. Conjunto de dados de árvores disponibilizado pela CnE, Coleta própria via o app “Coleta de imagens CnE”'),disabled=False,layout=l_req)

      lbl_qtddedados = m_Header(_('Quantidade de dados'))
      txta_qtddedados = ipywidgets.Textarea(value='',placeholder=_('Descreva a quantidade de dados \nex. No mínimo 30 imagens para cada categoria'),disabled=False,layout=l_req)
      
      lbl_pdr_img = m_Header(_('Padronização das imagens'))
      txta_pdr_img1 = ipywidgets.Textarea(value='',placeholder=_('Descrição do formato das imagens \nex. Formato: .jpeg, Tamanho: 224x224 pixels'),disabled=False,layout=l_req)

      lbl_rotulacao = m_Header(_('Rotaluação dos dados'))
      txta_rotulacao = ipywidgets.Textarea(value='',placeholder=_('Descreva a rotulação dos dados \nex. Por biólogos (conjunto de dados CnE), por estudantes do ensino médio (coleta própria)'),disabled=False,layout=l_req)

      lbl_desempenho = m_Header(_('Desempenho'))
      txta_desempenho = ipywidgets.Textarea(value='',placeholder=_('Descreva o desempenho desejado \nex. Acurácia (total/por categoria): No mínimo 0.75, F1 score: No mínimo 0.75'),disabled=False,layout=l_req)      

      itens_req = ipywidgets.VBox([ipywidgets.VBox([lbl_tarefa.header, txta_tarefa], layout=l_hbox),
                                   ipywidgets.VBox([lbl_tipotarefa.header, txta_tipotarefa], layout=l_hbox),
                                   ipywidgets.VBox([lbl_cat.header, txta_cat1], layout=l_hbox),
                                   ipywidgets.VBox([lbl_fontededados.header, txta_fontededados], layout=l_hbox),
                                   ipywidgets.VBox([lbl_qtddedados.header, txta_qtddedados], layout=l_hbox),
                                   ipywidgets.VBox([lbl_pdr_img.header, txta_pdr_img1], layout=l_hbox),
                                   ipywidgets.VBox([lbl_rotulacao.header, txta_rotulacao], layout=l_hbox),
                                   ipywidgets.VBox([lbl_desempenho.header, txta_desempenho], layout=l_hbox)],layout=l_vbox)

      display(itens_req)

  # Segunda aba: Dados
  with tab.output_to(1):#, select=False):
    grid1 = colabwidigets.Grid(12,1)
    
    with grid1.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/3.png", "rb").read(),format='png', layout=l_vbox))

    # Definir Path
    with grid1.output_to(1,0):
      lbl_path = m_Header(_('Definição do Path'))
      input_path = ipywidgets.Text(placeholder=_('Insira o caminho do pasta do conjunto de dados no google drive'),value='',layout=l_txt)
      btn_path = ipywidgets.Button(description=_('Carregar Path'), layout=l_btn)
      hbox_path = ipywidgets.HBox([input_path, btn_path], layout=l_hbox)
      vbox_path = ipywidgets.VBox([lbl_path.header, hbox_path], layout=l_vbox)
      display(vbox_path)

      def on_btn_path_clicked(b):
        # Saida da Atividade - Definir Path
        with grid1.output_to(2,0):
          grid1.clear_cell()
          _dir = drive_connect.root_dir + input_path.value
          if Path(_dir).is_dir():
            build_path(_dir)
            msg_ret = m_Ret(_('Path: ') + _dir + _('/ definido com sucesso'), 1)
          else:
            build_path("")
            msg_ret = m_Ret(_('Path: ') + _dir + _('/ não encontrado'), 2)
          display(msg_ret.txt)

      btn_path.on_click(on_btn_path_clicked) 

    # Visarlizar infos do dataset
    with grid1.output_to(3, 0):
      lbl_dataset_info = m_Header(_('Visualizar informações do conjunto de dados'))
      btn_view_total_by_category = ipywidgets.Button(description=_('Ver total por categoria'), layout=l_btn)
      hbox_dataset_info = [lbl_dataset_info.header, ipywidgets.Box([btn_view_total_by_category], layout=l_btn_hbox)]
      vbox_dataset_info = VBox(hbox_dataset_info, layout=l_vbox)
      display(vbox_dataset_info)
        
      def on_btn_view_total_by_category(n):
        with grid1.output_to(4, 0):
          # Saida Visarlizar infos do dataset
          try:
            grid1.clear_cell()
            total_by_category()
          except:
            grid1.clear_cell()
            msg_ret = m_Ret(_('Não foi possível visualizar as informações do conjunto de dados'), 2)
            display(msg_ret.txt)

      btn_view_total_by_category.on_click(on_btn_view_total_by_category)

    # Redimensionamento
    with grid1.output_to(5,0):      
      lbl_transforms = m_Header(_('Redimensionamento'))
      item_tfms_resize = ipywidgets.IntSlider(min = 8,max = 640,step = 8,value = 224,description =_('Tamanho das imagens'),layout=l_hidden_red,style=s_desc_wid)
      item_tfms_resize_mtd = ipywidgets.Dropdown(options=['crop', 'pad', 'squish'],description=_('Método redimensionamento'),layout=l_hidden_red,style=s_desc_wid)
      cb_disable_tfms = ipywidgets.Checkbox(True, description=_('Padrão'), indent=False, layout=l_hbox)
      hbox_resize = [lbl_transforms.header, cb_disable_tfms, item_tfms_resize, item_tfms_resize_mtd]
      vbox_resize = VBox(hbox_resize, layout=l_vbox)
      display(vbox_resize)

      def changed_resize(b):
        if cb_disable_tfms.value == True:
          item_tfms_resize.layout.visibility = 'hidden'
        else:
          item_tfms_resize.layout.visibility = 'visible'

      cb_disable_tfms.observe(changed_resize)
        
    # Transformações e Aumentações
    with grid1.output_to(6,0):
      lbl_augmentations = m_Header(_('Transformações e Aumentações'))
            
      tb_do_flip = ipywidgets.ToggleButtons(options=[(_('Sim'), True), (_('Não'), False)],description=_('Espelhar horizontalmente'),value=True,layout=l_hidden_tra,style=s_desc_wid)
      tb_do_vert = ipywidgets.ToggleButtons(options=[(_('Sim'), True), (_('Não'), False)],description=_('Espelhar verticalmente'),value = False,layout=l_hidden_tra,style=s_desc_wid)
      tb_pad_mode = ipywidgets.ToggleButtons(options=['zeros', 'reflection'],description='Pad Mode',value='reflection',layout=l_hidden_tra,style=s_desc_wid)
      sl_Max_Zoom = ipywidgets.FloatSlider(min=1.0,max=4,step=0.25,value=1.1,description=_('Zoom máximo'), layout=l_hidden_tra, style=s_desc_wid)
      sl_Min_Zoom = ipywidgets.FloatSlider(min=0.5,max=1,step=1,value=0.9,description=_('Zoom mínimo'), layout=l_hidden_tra, style=s_desc_wid)
      sl_Max_Lighting = ipywidgets.FloatSlider(min=0.2,max=1, step=0.1,value=0.2,description=_('Iluminação máxima'), layout=l_hidden_tra, style=s_desc_wid)
      slider_aug_tfms_multi = ipywidgets.FloatSlider(min = 0,max = 3,step = 0.1,value = 1,description_tooltip=_('Intensidade das transformações'),description=_('% de intensidade'),layout=l_hidden_tra,style=s_desc_wid)
      sl_Max_Rotate = ipywidgets.IntSlider(min=0,max=30,step=1,value=10,description=_('Rotação máxima'), layout=l_hidden_tra, style=s_desc_wid)
      sl_p_lighting = ipywidgets.FloatSlider(min=0.25, max=1, step=0.1, value=0.75,description=_('Intensidade iluminação'), layout=l_hidden_tra, style=s_desc_wid)
      sl_Max_warp = ipywidgets.FloatSlider(min=0.1, max=1, step=0.1, value=0.2,description=_('Inclinação'), layout=l_hidden_tra, style=s_desc_wid)
      cb_disable_aug = ipywidgets.Checkbox(True, description=_('Desabilitar'), indent=False)

      hbox_augmentation = [lbl_augmentations.header, cb_disable_aug, sl_Max_Zoom,sl_Min_Zoom,tb_do_flip,tb_do_vert,slider_aug_tfms_multi,sl_Max_Rotate,sl_Max_Lighting,sl_p_lighting,sl_Max_warp]
      vbox_augmentation = VBox(hbox_augmentation, layout=l_vbox)
      display(vbox_augmentation)

      def changed_tfms(b):
        if cb_disable_aug.value == True:
          slider_aug_tfms_multi.layout.visibility = 'hidden'
        else:
          slider_aug_tfms_multi.layout.visibility = 'visible'

      cb_disable_aug.observe(changed_tfms)

    #  Separação de conjunto de dados de treinamento e validação
    with grid1.output_to(7,0):
      lbl_splitter_header = m_Header(_('Separação do conjunto de dados de treinamento e validação'))
      splitter_percent_validation = ipywidgets.FloatSlider(min = 0,max = 1,step = 0.01,value = 0.2,description_tooltip=_('Este item define qual o percentual dos itens que irão compor a amostra de validação'),description=_('% Validação'),layout=l_hbox,style=s_desc_wid)
      hbox_splitter = [lbl_splitter_header.header, splitter_percent_validation]
      vbox_splitter = VBox(hbox_splitter, layout=l_vbox)
      display(vbox_splitter)
        
    # Criar dataloader
    with grid1.output_to(8,0):
      lbl_dataloader = m_Header(_('Criação do dataloader'))
      splitter_bs = ipywidgets.SelectionSlider(options=[8, 16, 32, 64, 128, 256],value=16,description_tooltip=_('Este item define qual será o tamanho do batch'),description=_('Tamanho do batch'),layout=l_hbox,style=s_desc_wid)
      btn_build_data = ipywidgets.Button(description=_('Criar dataloader'), layout=l_btn)
      hbox_dataloader = [lbl_dataloader.header, splitter_bs, ipywidgets.HBox([btn_build_data], layout=l_btn_hbox)]
      vbox_dataloader = VBox(hbox_dataloader, layout=l_vbox)
      display(vbox_dataloader)
        
      def on_btn_build_data_clicked(b):
        # Saída Criar dataloader
        with grid1.output_to(9,0):
          try:
            grid1.clear_cell()
            print(_('Convertendo imagens, aguarde'))
            time.sleep(2)
            # jpg_converter("") # Removido temporariamente pra não ficar alterando o dataset em toda execucao
            grid1.clear_cell()
            print(_('Aguarde, criando dataloader'))
            build_data(_Path, splitter_percent_validation.value, splitter_bs.value)
            time.sleep(2)
            grid1.clear_cell()
            msg_ret = m_Ret(_('Dataloader criado com sucesso'), 1)
            display(msg_ret.txt)
          except:
            grid1.clear_cell()
            nonlocal _dls
            _dls = None
            msg_ret = m_Ret(_('Falha ao criar dataloader'), 2)
            display(msg_ret.txt)
                      
      btn_build_data.on_click(on_btn_build_data_clicked)  
                
    # Visualizar Batch
    with grid1.output_to(10,0):
      lbl_batch_view = m_Header(_('Visualizar batch'))
      slider_show_batch = ipywidgets.IntSlider(min = 1,max = 25,step = 1,value = 3,description_tooltip=_('Permite a visualização de parte do Batch'),description=_('Qtd.'),layout=l_hbox,style=s_desc_wid)
      btn_show_batch = ipywidgets.Button(description=_('Ver batch'), layout=l_btn)
      cb_unique_batch = ipywidgets.Checkbox(False,description=_('Somente variações da mesma imagem?'),layout=l_hbox,style=s_desc_wid)
      hbox_show_batch = [lbl_batch_view.header, slider_show_batch, cb_unique_batch, ipywidgets.HBox([btn_show_batch], layout=l_btn_hbox)]
      vbox_show_batch = ipywidgets.VBox(hbox_show_batch, layout=l_vbox)
      display(vbox_show_batch)
            
      def on_btn_show_batch_clicked(b):
        # Saída Visualizar batch
        with grid1.output_to(11,0):
          try:
            grid1.clear_cell()
            print(_('Carregando batch, aguarde...'))
            time.sleep(3)
            grid1.clear_cell()
            _dls.show_batch(max_n=slider_show_batch.value, unique=cb_unique_batch.value)
          except:
            grid1.clear_cell()
            msg_ret = m_Ret(_('Não foi possível visualizar o batch'), 2)
            display(msg_ret.txt)

      btn_show_batch.on_click(on_btn_show_batch_clicked) 

  # Terceira aba: Treinamento do modelo
  with tab.output_to(2, select=False):  
    grid2 = colabwidigets.Grid(9,1)

    with grid2.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/4.png", "rb").read(),format='png', layout=l_vbox))

    # Arquitetura, Métricas e Learner
    with grid2.output_to(1,0):
      lbl_architecture = m_Header(_('Arquitetura'))
      model_architecture = ipywidgets.Dropdown(options=[('alexnet', models.alexnet),('densenet121', models.densenet121),('densenet161', models.densenet161),('densenet169', models.densenet169),('densenet201', models.densenet201),('resnet18', models.resnet18),('resnet34', models.resnet34),('resnet50', models.resnet50),('resnet101', models.resnet101),('resnet152', models.resnet152),('squeezenet1_0', models.squeezenet1_0),('squeezenet1_1', models.squeezenet1_1),('vgg16_bn', models.vgg16_bn),('vgg19_bn',models.vgg19_bn)],tooltips=[_('Escolha a arquitetura que será utilizada para criar o modelo.')],layout=l_txt,style=s_desc_wid,value = models.resnet18)
      lbl_metrics = m_Header(_('Métricas'))
      cb_error_rate = ipywidgets.Checkbox(value=False,description=_('Taxa de erro'),indent=False)
      cb_accuracy = ipywidgets.Checkbox(value=False,description=_('Acurácia'),indent=False)   
      btn_create_learn = ipywidgets.Button(description=_('Criar learner'),tooltip='',layout=l_btn)    
      vbox_architecture = ipywidgets.VBox([lbl_architecture.header,model_architecture], layout=l_txt)
      vbox_metrics = ipywidgets.VBox([lbl_metrics.header,ipywidgets.HBox([cb_error_rate,cb_accuracy])], layout=l_txt)
      vbox_architecture = ipywidgets.HBox([vbox_architecture, vbox_metrics], layout=l_vbox)
      vbox_learner = ipywidgets.VBox([vbox_architecture, ipywidgets.Box([btn_create_learn], layout=l_btn_hbox)], layout=l_vbox)
      display(vbox_learner)

      def on_btn_create_learn_clicked(b):
        # Saída Criar learner
        with grid2.output_to(2,0):
          try:
            grid2.clear_cell()
            print(_('Criando Learner'))
            grid2.clear_cell()
            create_learner(model_architecture.value)
            grid2.clear_cell()
            msg_ret = m_Ret(_('Learner criado com sucesso'), 1)
            display(msg_ret.txt)  
          except:
            grid2.clear_cell()
            msg_ret = m_Ret(_('Não foi possível criar o learner'), 2)
            display(msg_ret.txt)
            nonlocal _learn
            learn = None
          
      btn_create_learn.on_click(on_btn_create_learn_clicked)  
            
    # Treinamento
    with grid2.output_to(3,0):
      lbl_trainning = m_Header(_('Treinamento do modelo'))
      slider_epochs = ipywidgets.IntSlider(min = 1,max = 50,step = 1,value = 3,description_tooltip=_('Quantidade de epochs para treinar o modelo'),description='Epochs',layout=l_hbox,style=s_desc_wid)            
      btn_train_model = ipywidgets.Button(description=_('Treinar modelo'),tooltip='',layout=l_btn)    
      hbox_trainning = [lbl_trainning.header,slider_epochs,ipywidgets.Box([btn_train_model], layout=l_btn_hbox)]
      vbox_trainning = ipywidgets.VBox(hbox_trainning, layout=l_vbox)
      display(vbox_trainning)
        
      def on_btn_train_model_clicked(b):
        # Saída Executar Treinamento
        with grid2.output_to(4,0):
          try:
            grid2.clear_cell()
            print(_('Iniciando treinamento'))
            time.sleep(2)
            grid2.clear_cell()
            train_data(slider_epochs.value)   
            msg_ret = m_Ret(_('Fim do treinamento do modelo'), 1)
            display(msg_ret.txt)
          except:
            grid2.clear_cell()
            msg_ret = m_Ret(_('Não foi possível treinar o modelo'), 2)
            display(msg_ret.txt)
            nonlocal _interp
            _interp = None

      btn_train_model.on_click(on_btn_train_model_clicked)  

    # Data Cleaning
    with grid2.output_to(5,0):
      lbl_datacleaning = m_Header(_('Data Cleaning (opcional)'))
      btn_data_cleaning = ipywidgets.Button(description=_('Executar Data Cleaning'),tooltip='',layout=l_btn)    
      hbox_datacleaning = [lbl_datacleaning.header, ipywidgets.Box([btn_data_cleaning], layout=l_btn_hbox)]
      vbox_datacleaning = VBox(hbox_datacleaning, layout=l_vbox)
      display(vbox_datacleaning)
        
      def on_btn_data_cleaning_clicked(b):
        # Saída Data Cleaning
        with grid2.output_to(6,0):
          try:
            grid2.clear_cell()
            print(_('Carregando Data Cleaning, agurade...'))
            time.sleep(3)
            grid2.clear_cell()
            cleaner = ImageClassifierCleaner(_learn)
            display(cleaner)
            on_btn_data_cleaning_clicked.cleaner = cleaner
            msg_ret = m_Ret(_('Data Cleaning carregado, faça as alterações e clique em salvar para efetuar as alterações (cuidado, as alterações são permanentes no Drive)'), 1)
            display(msg_ret.txt)
          except:
            grid2.clear_cell()
            msg_ret = m_Ret(_('Não foi possível abrir o Data Cleaning'), 2)
            display(msg_ret.txt)

      btn_data_cleaning.on_click(on_btn_data_cleaning_clicked)

    # Salvar DC
    with grid2.output_to(7,0):
      btn_data_cleaning_exec = ipywidgets.Button(description=_('Salvar alterações do Data Cleaning'),tooltip=_('Efetua as ações feitas no Data Cleaning, CUIDADO Exclusões de itens irão ser permanentes no google drive'),layout=l_btn)
      hbox_datacleaning_save = Box([btn_data_cleaning_exec], layout=l_btn_hbox)
      vbox_datacleaning_save = VBox([hbox_datacleaning_save], layout=l_vbox)
      display(vbox_datacleaning_save)
      
      def on_btn_data_cleaning_exec_clicked(b):
        # Saida Salvar DC
        with grid2.output_to(8,0):
          try:
            grid2.clear_cell()
            print(_('Gravando alterações, aguarde'))
            time.sleep(3)
            grid2.clear_cell()
            for idx in on_btn_data_cleaning_clicked.cleaner.delete(): on_btn_data_cleaning_clicked.cleaner.fns[idx].unlink()
            for idx,cat in on_btn_data_cleaning_clicked.cleaner.change(): shutil.move(str(on_btn_data_cleaning_clicked.cleaner.fns[idx]), path/cat)
            msg_ret = m_Ret(_('Alterações gravadas'), 1)
            display(msg_ret.txt)
          except:
              grid2.clear_cell()
              msg_ret = m_Ret(_('Não foi salvar os resultados do Data Cleaning'), 2)
              display(msg_ret.txt)
        
      btn_data_cleaning_exec.on_click(on_btn_data_cleaning_exec_clicked)

  # Quarta aba: Avaliação do desempenho do Transfer Learning
  with tab.output_to(3, select=False):  
    grid3 = colabwidigets.Grid(9,1)

    with grid3.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/5.png", "rb").read(),format='png', layout=l_vbox))

    # Matriz de confusao
    with grid3.output_to(1,0):
      lbl_c_matrix = m_Header(_('Matriz de confusão'))
      btn_show_c_matrix = ipywidgets.Button(description=_('Ver Matriz de confusão'),tooltip='',layout=l_btn)  
      vbox_c_matrix = ipywidgets.VBox([lbl_c_matrix.header, ipywidgets.Box([btn_show_c_matrix], layout=l_btn_hbox)], layout=l_vbox)
      display(vbox_c_matrix)
    
      def on_btn_show_c_matrix(b):
        # Saida Matriz de confusao
        with grid3.output_to(2,0):
          try:
            grid3.clear_cell()
            print(_('Carregando matriz de confusão, aguarde...'))
            time.sleep(2)
            grid3.clear_cell()
            _interp.plot_confusion_matrix()
          except:
            msg_ret = m_Ret(_('Não foi possível visualizar a matriz de confusão'), 2)
            display(msg_ret.txt)
        
      btn_show_c_matrix.on_click(on_btn_show_c_matrix)  

    # Acuracia por categoria
    with grid3.output_to(3,0):
      lbl_met_cat = m_Header(_('Métricas por categoria'))
      btn_show_met_cat = ipywidgets.Button(description=_('Ver métricas por categoria'),tooltip='',layout=l_btn)   
      vbox_met_cat = ipywidgets.VBox([lbl_met_cat.header, ipywidgets.Box([btn_show_met_cat], layout=l_btn_hbox)], layout=l_vbox)
      display(vbox_met_cat)
    
      def on_btn_show_met_cat(b):
        # Saida Acuracia por categoria
        with grid3.output_to(4,0):
          try:
            grid3.clear_cell()
            print(_('Carregando métricas por categoria, aguarde...'))
            time.sleep(2)
            grid3.clear_cell()
            _interp.print_classification_report()
          except:
            msg_ret = m_Ret(_('Não foi exibir métricas por categoria'), 2)
            display(msg_ret.txt)
        
      btn_show_met_cat.on_click(on_btn_show_met_cat)  

    # Principais perdas
    with grid3.output_to(5,0):
      lbl_t_losses = m_Header(_('Principais perdas'))
      slider_top_losses = ipywidgets.IntSlider(min = 1,max = 15,step = 1,value = 2,description_tooltip=_('Principais perdas'),description=_('Qtd.'),layout=l_hbox,style=s_desc_wid)
      btn_show_top_losses = ipywidgets.Button(description=_('Ver principais perdas'),tooltip='',layout=l_btn)
      hbox_t_losses = ipywidgets.HBox([btn_show_top_losses], layout=l_btn_hbox)
      vbox_t_losses = ipywidgets.VBox([lbl_t_losses.header, slider_top_losses, hbox_t_losses], layout=l_vbox)
      display(vbox_t_losses)

      def on_btn_show_top_losses(b):
        # Saida Principais perdas
        with grid3.output_to(6,0):
          try:
            grid3.clear_cell()
            print(_('Carregando principais perdas, aguarde...'))
            time.sleep(2)
            grid3.clear_cell()
            _interp.plot_top_losses(slider_top_losses.value, figsize=(15,10))
          except:
            grid3.clear_cell()
            msg_ret = m_Ret(_('Não foi possível exibir principais perdas'), 2)
            display(msg_ret.txt)

      btn_show_top_losses.on_click(on_btn_show_top_losses)               

    # Mais confundidos
    with grid3.output_to(7,0):
      lbl_m_confused = m_Header(_('Mais confundidos'))
      slider_most_confused = ipywidgets.IntSlider(min = 1,max = 8,step = 1,value = 1,description = _("vez(es) confundido"),layout=l_hbox,style=s_desc_wid)
      btn_show_most_confused = ipywidgets.Button(description=_('Ver mais confundidos'),tooltip='',layout=l_btn)      
      hbox_m_confused = ipywidgets.HBox([btn_show_most_confused], layout=l_btn_hbox)
      vbox_m_confused = ipywidgets.VBox([lbl_m_confused.header, slider_most_confused, hbox_m_confused], layout=l_vbox)
      display(vbox_m_confused)

      def on_btn_show_most_confused(b):
        #Saída Mais confundidos
        with grid3.output_to(8,0):
          try:
            grid3.clear_cell()
            print(_('Carregando mais confundidos, aguarde...'))
            time.sleep(2)
            grid3.clear_cell()
            most_confused = _interp.most_confused(min_val=slider_most_confused.value)
            for item in most_confused:
              print(_('{0} foi confundida com {1} e esta combinação em particular ocorreu {2} vez(es)'.format(item[0], item[1], str(item[2]))))              
          except:
            grid3.clear_cell()
            msg_ret = m_Ret(_('Não foi possível exibir mais confundidos'), 2)
            display(msg_ret.txt)

      btn_show_most_confused.on_click(on_btn_show_most_confused) 

  # Quinta aba: Fine Tuning
  with tab.output_to(4, select=False):  
    grid4 = colabwidigets.Grid(6,1)

    with grid4.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/6.png", "rb").read(),format='png', layout=l_vbox))

    # Unfreeze e Find lr
    with grid4.output_to(1,0):
      lbl_find_lr = m_Header(_('Encontrar melhor taxa de aprendizagem'))
      btn_unfreeze = ipywidgets.Button(description=_('Descongelar modelo'), layout=l_btn)
      btn_find_lr = ipywidgets.Button(description=_('Encontrar melhor taxa'), layout=l_btn)
      box_find_lr = ipywidgets.VBox([lbl_find_lr.header, ipywidgets.HBox([btn_unfreeze, btn_find_lr], layout=l_btn_hbox)], layout=l_vbox)
      display(box_find_lr)

      def on_btn_unfreeze(b):
        with grid4.output_to(2,0):
          try:
            grid4.clear_cell()
            _learn.unfreeze()
            msg_ret = m_Ret(_('Modelo descongelado com sucesso'), 1)
            display(msg_ret.txt)            
          except:
            grid4.clear_cell()
            msg_ret = m_Ret(_('Não foi possível descongelar modelo'), 2)
            display(msg_ret.txt)

      def on_btn_find_lr(b):
        with grid4.output_to(3,0):
          try:
            grid4.clear_cell()
            lr_min, lr_steep, lr_valley, lr_slide = _learn.lr_find(suggest_funcs=(minimum, steep, valley, slide))
            on_btn_find_lr.lr_valley = lr_valley
            print('lr_min: ', lr_min)
            print('lr_steep: ', lr_steep)
            print('lr_valley: ', lr_valley)
            print('lr_slide: ', lr_slide)
            msg_ret = m_Ret(_('Find lr executado com sucesso'), 1)
            display(msg_ret.txt)
          except:
            grid4.clear_cell()
            msg_ret = m_Ret(_('Não foi possível executar a melhor taxa de aprendizagem'), 2)
            display(msg_ret.txt)

      btn_unfreeze.on_click(on_btn_unfreeze)
      btn_find_lr.on_click(on_btn_find_lr)

    # Treinamento Fine Tuning
    with grid4.output_to(4,0):
      lbl_epochs_ft = m_Header(_('Epochs Fine Tuning'))
      slider_epochs_FT = ipywidgets.IntSlider(min = 1,max = 50,step = 1,value = 3,description = "Epochs",layout=l_hbox,style=s_desc_wid)
      btn_exec2 = ipywidgets.Button(description=_('Treinar modelo otimizado'), layout=l_btn)
      hbox_s_e_ft = ipywidgets.VBox([lbl_epochs_ft.header, slider_epochs_FT, ipywidgets.VBox([btn_exec2], layout=l_btn_hbox)], layout=l_vbox)
      display(hbox_s_e_ft)

      def on_btn_exec2(b):
        with grid4.output_to(5,0):
          # Saida Treinamento Fine Tuning
          try:
              grid4.clear_cell()
              #cbs=[ShowGraphCallback,ActivationStats(with_hist=True),SaveModelCallback(monitor='accuracy')]
              cbs=[ShowGraphCallback,ActivationStats(with_hist=True),SaveModelCallback()]
              _learn.fit_one_cycle(slider_epochs_FT.value,lr_max=on_btn_find_lr.lr_valley, cbs=cbs)
              nonlocal _interp
              _interp = ClassificationInterpretation.from_learner(_learn)
              msg_ret = m_Ret(_('Treinamento fine tuning executado com sucesso'), 1)
              display(msg_ret.txt)
          except:
            grid4.clear_cell()
            msg_ret = m_Ret(_('Não foi possível executar o treinamento do fine tuning'), 2)
            display(msg_ret.txt)
                   
      btn_exec2.on_click(on_btn_exec2)
        
  # Sexta aba: Avaliação do desempenho do fine tuning
  with tab.output_to(5, select=False):
    grid5 = colabwidigets.Grid(9,1)

    with grid5.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/7.png", "rb").read(),format='png', layout=l_vbox))

    # Matriz de confusao ft
    with grid5.output_to(1,0):
      lbl_c_matrix_ft = m_Header(_('Matriz de confusão'))
      btn_show_c_matrix_ft = ipywidgets.Button(description=_('Ver matriz de confusão'),tooltip='',layout=l_btn)   
      vbox_c_matrix_ft = ipywidgets.VBox([lbl_c_matrix_ft.header, ipywidgets.Box([btn_show_c_matrix_ft], layout=l_btn_hbox)], layout=l_vbox)
      display(vbox_c_matrix_ft)
    
      def on_btn_show_c_matrix_ft(b):
        # Saida Matriz de confusao ft
        with grid5.output_to(2,0):
          try:
            grid5.clear_cell()
            print(_('Carregando matriz de confusão, aguarde...'))
            time.sleep(2)
            grid5.clear_cell()
            _interp.plot_confusion_matrix()
          except:
            msg_ret = m_Ret(_('Não foi possível visualizar a matriz de confusão'), 2)
            display(msg_ret.txt)
        
      btn_show_c_matrix_ft.on_click(on_btn_show_c_matrix_ft)  

    # Acuracia por categoria ft
    with grid5.output_to(3,0):
      lbl_met_cat_ft = m_Header(_('Métricas por categoria'))
      btn_show_met_cat_ft = ipywidgets.Button(description=_('Ver métricas por categoria'),tooltip='',layout=l_btn)   
      vbox_met_cat_ft = ipywidgets.VBox([lbl_met_cat_ft.header, ipywidgets.Box([btn_show_met_cat_ft], layout=l_btn_hbox)], layout=l_vbox)
      display(vbox_met_cat_ft)
    
      def on_btn_show_met_cat_ft(b):
        # Saida Acuracia por categoria ft
        with grid5.output_to(4,0):
          try:
            grid5.clear_cell()
            print(_('Carregando métricas por categoria, aguarde...'))
            time.sleep(2)
            grid5.clear_cell()
            _interp.print_classification_report()
          except:
            msg_ret = m_Ret(_('Não foi exibir Métricas por categoria'), 2)
            display(msg_ret.txt)
    
      btn_show_met_cat_ft.on_click(on_btn_show_met_cat_ft)  

    # Principais perdas ft
    with grid5.output_to(5,0):
      lbl_t_losses_ft = m_Header(_('Principais perdas'))
      slider_top_losses_ft = ipywidgets.IntSlider(min = 1,max = 15,step = 1,value = 2,description_tooltip=_('Principais perdas'),description=_('Qtd.'),layout=l_hbox,style=s_desc_wid)
      btn_show_top_losses_ft = ipywidgets.Button(description=_('Ver principais perdas'),tooltip='',layout=l_btn)
      hbox_t_losses_ft = ipywidgets.HBox([btn_show_top_losses_ft], layout=l_btn_hbox)
      vbox_t_losses_ft = ipywidgets.VBox([lbl_t_losses_ft.header, slider_top_losses_ft, hbox_t_losses_ft], layout=l_vbox)
      display(vbox_t_losses_ft)

      def on_btn_show_top_losses_ft(b):
        # Saida Principais perdas ft
        with grid5.output_to(6,0):
          try:
            grid5.clear_cell()
            print(_('Carregando principais perdas, aguarde...'))
            time.sleep(2)
            grid5.clear_cell()
            _interp.plot_top_losses(slider_top_losses_ft.value, figsize=(15,10))
          except:
            grid5.clear_cell()
            msg_ret = m_Ret(_('Não foi possível exibir principais perdas'), 2)
            display(msg_ret.txt)

      btn_show_top_losses_ft.on_click(on_btn_show_top_losses_ft)               

    # Mais confundidos
    with grid5.output_to(7,0):
      lbl_m_confused_ft = m_Header(_('Mais confundidos'))
      slider_most_confused_ft = ipywidgets.IntSlider(min = 1,max = 8,step = 1,value = 1,description = _("vez(es) confundido"),layout=l_hbox,style=s_desc_wid)
      btn_show_most_confused_ft = ipywidgets.Button(description=_('Ver mais confundidos'),tooltip='',layout=l_btn)      
      hbox_m_confused_ft = ipywidgets.HBox([btn_show_most_confused_ft], layout=l_btn_hbox)
      vbox_m_confused_ft = ipywidgets.VBox([lbl_m_confused_ft.header, slider_most_confused_ft, hbox_m_confused_ft], layout=l_vbox)
      display(vbox_m_confused_ft)

      def on_btn_show_most_confused_ft(b):
        # Saida Mais confundidos
        with grid5.output_to(8,0):
          try:
            grid5.clear_cell()
            print(_('Carregando mais confundidos, aguarde...'))
            time.sleep(2)
            grid5.clear_cell()
            most_confused_ft = _interp.most_confused(min_val=slider_most_confused_ft.value)
            for item_ft in most_confused_ft:
              print(_('{0} foi confundida com {1} e esta combinação em particular ocorreu {2} vez(es)'.format(item_ft[0], item_ft[1], str(item_ft[2]))))               
          except:
            grid5.clear_cell()
            msg_ret = m_Ret(_('Não foi possível exibir mais confundidos'), 2)
            display(msg_ret.txt)

      btn_show_most_confused_ft.on_click(on_btn_show_most_confused_ft) 

  # Sétima aba: Predição
  with tab.output_to(6, select=False):  
    grid6 = colabwidigets.Grid(3,1)

    with grid6.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/8.png", "rb").read(),format='png', layout=l_vbox))

    # Predicao com upload
    with grid6.output_to(1,0):
      lbl_prediction = m_Header(_('Predição com upload'))
      btn_file_upload = ipywidgets.FileUpload(layout=l_btn, style=s_desc_wid)
      btn_pred = ipywidgets.Button(description=_('Predição'), layout=l_btn, style=s_desc_wid)
      box_predict = ipywidgets.VBox([lbl_prediction.header, ipywidgets.HBox([btn_file_upload, btn_pred], layout=l_btn_hbox)], layout=l_vbox)
      display(box_predict)

      def on_btn_pred(b):
        # Saida Predicao com upload
        with grid6.output_to(2,0):
          try:
            #grid6.clear_cell()
            print(_('Aguarde, realizando predição...'))
            img = PILImage.create(btn_file_upload.data[0])
            display(img.to_thumb(256,256))
            categorie,__,probs = _learn.predict(img)
            print(_(f"Isto é um(a) {categorie}, com a probabilidade de {probs[0].item():.6f}"))
            msg_ret = m_Ret('', 1)
          except:
            grid6.clear_cell()
            msg_ret = m_Ret(_('Não foi possível realizar a predição da imagem '), 2)

          display(msg_ret.txt)
        
      btn_pred.on_click(on_btn_pred)

  # Oitava aba: Exportação
  with tab.output_to(7, select=False):  
    grid7 = colabwidigets.Grid(4,1)

    with grid7.output_to(0,0):    
      pass #display(ipywidgets.Image(value=open("/content/9.png", "rb").read(),format='png', layout=l_vbox))

    # Exportar modelo PKL
    with grid7.output_to(1,0):
      lbl_export = m_Header(_('Exportação do modelo'))
      export_path = ipywidgets.Text(placeholder=_('Insira (apenas) o caminho de um diretório válido no drive'),value='',layout=l_txt)
      btn_e_path = ipywidgets.Button(description=_('Exportar modelo PKL'), layout=l_btn)
      btn_e_path_onnx = ipywidgets.Button(description=_('Exportar modelo ONNX'), layout=l_btn)
      hbox_export = ipywidgets.HBox([btn_e_path, btn_e_path_onnx], layout=l_btn_hbox)
      vbox_export = ipywidgets.VBox([export_path, hbox_export], layout=l_vbox)
      display(lbl_export.header)
      display(vbox_export)
  
      def on_btn_e_path_clicked(b):
        # Saida Exportar modelo PKL
        with grid7.output_to(2,0):
          grid7.clear_cell()
          _dir_e = "/content/gdrive/My Drive/" + export_path.value
          if Path(_dir_e).is_dir():
            try:
              _learn.model
              _learn.export(_dir_e + 'export_model.pkl')
              msg_ret = m_Ret(_('Exportado para: \'' + _dir_e + 'export_model.pkl com sucesso'), 1)
              display(msg_ret.txt)
            except:
              msg_ret = m_Ret(_('Não foi possível exportar o modelo PKL'), 2)
              display(msg_ret.txt)
          else:
            msg_ret = m_Ret(_('Diretorio: \'' + _dir_e + ' não encontrado'), 2)
            display(msg_ret.txt)
  
      def on_btn_e_onnx_path_clicked(b):
        # Saida Saida Exportar modelo ONNX
        with grid7.output_to(3,0):
          grid7.clear_cell()
          _dir_e_onnx = "/content/gdrive/My Drive/" + export_path.value
          if Path(_dir_e_onnx).is_dir():
            try:
              _learn.model
              _learn.model.eval();
              x = torch.randn(1, 3, 299, 299, requires_grad=False).cuda()
              torch_out = torch.onnx._export(_learn.model, x, _dir_e_onnx + 'export_model_onnx.onnx', export_params=True)
              msg_ret = m_Ret(_('Exportado para: ' + _dir_e_onnx + 'export_model_onnx.onnx com sucesso'), 1)
              display(msg_ret.txt)
            except:
              msg_ret = m_Ret(_('Não foi possível exportar o modelo ONNX'), 2)
              display(msg_ret.txt)
          else:
            msg_ret = m_Ret(_('Diretorio: ' + _dir_e_onnx + ' não encontrado'), 2)
            display(msg_ret.txt)
      
      btn_e_path.on_click(on_btn_e_path_clicked) 
      btn_e_path_onnx.on_click(on_btn_e_onnx_path_clicked) 

print(_('\n\nFim da primeira execução, exectue vulcan_colab.visual_layer() em outra célula de código'))