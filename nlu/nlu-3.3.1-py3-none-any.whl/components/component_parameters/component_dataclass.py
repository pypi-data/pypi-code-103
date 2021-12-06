from typing import List, Dict, Set, Dict, Tuple, Optional, Any, Callable, Dict
from dataclasses import dataclass, field

# TODO pre-defined schema time for extracotrs
# TODO universe module with all overview files, components and namespaces in this sexy format

print('lol')

# from build.lib.nlu.components.component_parameters.component_dataclass import NLP_HC_ANNO

"""
Contains dataclases which represent Extractors and their configuration

"""

""" Cool ideas but maybe overkill
- What abotu multiple exctracotrs? Make attribute extractor attrivbute a luist of methods? People of can just write phat mehtods? Buy what about combing n
- white/black list based application of specific methods to specirfic keywords . 
- What if you want multiple output cols, one per extractor method? 

"""
"""
The new NLU 3.3.0 gives you 2000+ % Speedup , 50x faster saving times and 60 + New models in  X+ languages!
Additionally, 2 tutorial videos are out

Make sure to check them out !  


This is all Mainly for Pipe BUlding Logic

Pipe exraction logic may be held otherwhere, but some fields may be reflected relevant to it here 
"""
from nlu.pipe.extractors.extractor_configs_OS import *
from nlu.pipe.col_substitution.col_substitution_OS import *
from sparknlp.internal import AnnotatorTransformer
from typing import List, Dict, Set, Dict, Tuple, Optional, Any, Union
from typing import Callable
from typing import List, Dict, Set, Dict, Tuple, Optional
from dataclasses import dataclass, field, make_dataclass
from enum import Enum
# TODO add TRAINABLE Nodes, these are not the same as fitted and treaded differently
# TODO add exractor field with pointer to applicable extracotrs!?
# TODO need PROVIER and LICENSE and COMOPUTATION input/output contexT?
# TODO master parant calss to inherint from Should take accapteble Feature Universe Types for in/Out and Acceptable Anno Universe types?
"""
# TODO COOL FEATURE :
Simple ExternalNode to extend for public facing usiers

Enables creation of custom Spark NLP Pipelines, the ExternalNodes become embelished in a way that they fit into Spark NLP/Vanilla Spark Pipes and support Distribution in clusters!!!
    -Boom!

 
"""

"""
A Node Is just an Annotator
A Feature is just a input OR the outputi of an annotator
A Feature-Node is a Triplet, (Anno, Ins,Outs) aka graph triplet?

"""

# TODO REMOVE SUBSTUTIONS OR MAKE THEM GLOBAL!!!
"""TODO FIXED EXPLOSION LOGIC: 
If there are multiple Annotators of Sub/Super levels,
we can still get clean output by Exploding Row-wise on the col whose corrosponding value is LONGES

Since we always explode on array cols, the question is which to explode,
In the easy case, we can zip(token, stem, lema)
but
zip(token, stem, clean_tokens)
can fail in PANDAS (but not spark) because not equal lengths !!!
So we must check for each row, which which col is longest and explode on that..

Or just view it as seperate output level and leave it as that

But aaalso multiple NERS have the SAME!!! Issue!!
How to handle 

s = "Billy has history of cancer, leukima, low blood pressure"
nlu.load('med_ner ner.names').predict(s)
med_entities = ['cancer', 'leukima', 'low blood pressure']
name_entities = ['Billy']
So Now there are 2 explode and display options
1 Row per name_entity or 1 row per med entity?
OOOR We do god Damn Padding Like spark Would do???

-->
|med_ner_chunk    |name_ner_chunk| Full sentence |
|-----------------|--------------|---------------|
| cancer          | Billy        | Billy has.... |
| leukima         | None         | Billy has.... |
| low blod..      | None         | Billy has.... |







"""
"""OCR NOTES


Ultimate DAG Structure
DAG algo basically keeps adding dependencies and exploring until reaching
TEXT which is BEGINNING of path

We should be FIRST computing the path, then optimize (double crossings etc..)
and then physically invoke it 



## PDF PRocessing
Pdf2Text : text+path -> text+pagenum


Col Types
"""
"""FEATURE IDEA 
NLP PROPHET: 
We can re-create every model in modelshub, IF we have the link to dataset.
This now is a train/test dataset for a Meta-ML engine
X = Pipe-Config
Y = Pipe-Accuracy
"""
"""HF DATASET MODEL SNAP:
Loop over all Datasets in HF Datasets and Generate a model and auto-upload to
modelshub!
"""
# Helper Classes for Type Checking and IDE Compiler Hints because NewType lib does not support typeChecking
class JslUniverse(str): pass# I.e. OCR, NLP, NLP-HC, NLP-AUDIO?
class LanguageIso(str): pass## Lang ISO TODO
class ComputeContext(str): pass
class ComponentBackend(str): pass
class ExternalFeature(str): pass # Any JSL generated and provided
class ExternalAnno(str): pass # external or from 3rd Party Lib
class JslFeature(str): pass # Any JSL generated Feature
class JslAnnoRef(str): pass # Any JSL Anno reference. Unique Name defined by NLU to identify a specific class. Not using actual JVM/PY class name to make it language agnostic
class NlpLevel(str): pass  # OutputLevel of a NLP annotator
class JslAnnoPyClass(str): pass
class JslAnnoJavaClass(str): pass
class LicenseType(str): pass
# TODO remove dataclass?

class DatasetReferences:
    def get_url_reference(self):pass
    def get_paper_reference(self):pass
    def get_language(self):pass
    def get_task(self):pass

class EnumExtended(Enum):
    @classmethod
    def get_iterable_values(cls):
        # get_iterable_values = lambda x :  [v.value for v in x]
        """Returns iterable list of values from dataclass"""
        return [v.value for v in list(cls)]


class NluSpell(EnumExtended):
    def get_lang(self):pass
    def get_ano_class(self):pass
    def get_nlp_ref(self):pass
    def get_dataset(self):pass
    def get_model_size(self):pass


class JSL_UNIVERSES(EnumExtended):
    """Defines a Node in a ML Dependency Feature Graph.
    Anno= Node, In = In arrous, Out = out Arrows
    Each NLU Component will output one of these
    NODE = Anno Class
    INPUTS = Array of ML-Features
    OUTPUTS = Array of ML-Features

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    ocr = JslUniverse('ocr')
    hc =  JslUniverse('hc')
    open_source = JslUniverse('open_source')

@dataclass
class Licenses(EnumExtended):
    """Defines a Node in a ML Dependency Feature Graph.
    Anno= Node, In = In arrous, Out = out Arrows
    Each NLU Component will output one of these
    NODE = Anno Class
    INPUTS = Array of ML-Features
    OUTPUTS = Array of ML-Features

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    ocr = LicenseType('ocr')
    hc =  LicenseType('hc')
    open_source = LicenseType('open_source')

@dataclass
class ComponentBackend(EnumExtended):
    """Defines a Node in a ML Dependency Feature Graph.
    Anno= Node, In = In arrous, Out = out Arrows
    Each NLU Component will output one of these
    NODE = Anno Class
    INPUTS = Array of ML-Features
    OUTPUTS = Array of ML-Features

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    ocr = ComponentBackend('spark ocr')
    hc =  ComponentBackend('spark hc')
    open_source = ComponentBackend('spark nlp')
    external = ComponentBackend('external')

@dataclass
class ComputeContexts(EnumExtended):
    """Se of
    """
    spark =  ComputeContext('spark')
    pandas =  ComputeContext('pandas')
    numpy =  ComputeContext('numpy')
    modin =  ComputeContext('modin')
    py_arrow =  ComputeContext('py_arrow')

@dataclass
class FeatureNode:  # or Mode Node?
    """Defines a Node in a ML Dependency Feature Graph.
    Anno= Node, In = In arrous, Out = out Arrows
    Each NLU Component will output one of these
    NODE = Anno Class
    INPUTS = Array of ML-Features
    OUTPUTS = Array of ML-Features

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """

    """:cvar
    
    nlu.detect_lang=True # Global
    nlu.default_lang='en' , 'xx', 'auto_detect' # Global
    nlu.optimization_strategy = 'speed'
    nlu.load('pdf2text lemmatimze sentiment').predict(pdf, detect_lang=True) # Dynamically load ENG/DE models by detectling
    
    text -> document -> Tok -> .... Sentiment
    
    nlu.load('jpg2text   med_ner').predict('
    nlu.load(ocr =True, 'med_ner').predict('/path/to/img.jpg') # 
    
    jpg->  jpg2pdf 
    jpg->  jpg2text
    jpg->  jpgResacle 
    
    nlu.loadl('image_rotate image_autoscale image2text med_ner).predict(pdf)
    
    pdf->  (image_rotate image_autoscale image2text)      -> med_ner 
    
   pdf->  (image_rotate image_autoscale image2text)->Spell      -> med_ner 
   pdf->  (image_rotate image_autoscale image2text)Lema->Stem->->Spell      -> med_ner 


    nlu.load('image_rotate med_ner').predict(INPUT_NODE)
    
    input_node->  image_rotate->( img2text->)med_ner 
    
    


    analze inpt data which effect pipeline search/generation + Lang detect from data
    optimize for accuracy/speed/balance
    Accuracy for papaer 
    speed for edge fast case 
    balance for most users 
    
    
    """
    JSL_generator_anno_class: JslAnnoRef  # JSL Annotator that can generate this Triplet. Could be from OCR/JSL-Internal/Spark-NLP
    ins: List[JslFeature]  # JSL Annotator that can generate this Triplet
    outs: List[JslFeature]  # JSL Annotator that can generate this Triplet
# TODOD make this the UNIVERSE package!!!!

## TODO extra config for getting "to which sentence did chunk/x/y/z belong to?"
## TODO What abotu PARAMTERIXED extractor methods, like get_k_confidence for lang classifier??
# TODO integrate
# TODO reflect SUB-TOKEN and SUPER-TOKEN output levels and analgous for sentence/document/chunk??



@dataclass
class NLP_DOMAINS(str,EnumExtended):
    HEALTHCARE = 'healthcare'
    CLINICAL = 'clinical'
    RADIOLOGY = 'radiology'
    REDDIT = 'reddit'
    TWITTER = 'twitter'
    MARKETING = 'marketing'

@dataclass
class NLP_LEVELS(NlpLevel,EnumExtended):
    """:cvar
    XXX_SUPER is a N to M Mapping, with M <= N
    XXX_SUB is a N to M mapping, with M >=N
    no prefix implies a N to N mapping to be expected
    """
    DOCUMENT = NlpLevel('document')
    CHUNK = NlpLevel('chunk')
    SUB_CHUNK = NlpLevel('sub_chunk')
    SUPER_CHUNK = NlpLevel('super_chunk')
    SENTENCE = NlpLevel('sentence')
    RELATION = NlpLevel('relation')
    TOKEN = NlpLevel('token')
    SUB_TOKEN = NlpLevel('sub_token')
    SUPER_TOKEN = NlpLevel('super_token')

    INPUT_DEPENDENT_DOCUMENT_CLASSIFIER = NlpLevel('INPUT_DEPENDENT_DOCUMENT_CLASSIFIER')

@dataclass
class OCR_OUTPUT_LEVELS(str,EnumExtended):
    # PAGES ARE LIKE TOKENS!! Book is full document!

    PAGES = 'pages'# Generate 1 output per PAGE in each input document. I.e if 2 PDFs input with 5 pages each, gens 10 rows. 1 to many mapping
    FILE = 'file' # Generate 1 output per document, I.e. 2 PDFS with 5 pages each gen 2 Row, 1 to one mapping
    OBJECT = 'object' # Generate 1 output row per detected Object in Input document. I.e. if 2 PDFS with 5 Cats each, generates 10 rows. ---> REGION or Not?
    CHARACTER = 'character' # Generate 1 oputput row per OCR'd character, I.e. 2 PDFS with 100 Chars each, gens 100 Rows.
    TABLE = 'table' # 1 Pandas DF per Table.

# myCustomComponent = MyCustomNode
# Auto-retrain all common problems with NLU and NEW embeds! --> Free models with each new Embeds and retran entire molhub
dfs = nlu.load('extract_tables ').predict('mypdf') # --> Pandas DF returns 1 Row Per Table detected. But each row easily Unpackable to extra Pandas DF that represents the table
for df in dfs.tables: nlu.load('sent').predict(df)
for df in dfs : nlu.fit(df).upload(metadata) # Tuesday session! Upload all models BAR Plot distribution of Tasks!
"""

Generate Dataset Topic and TASK distribution
If many finacne datasets -> Fin NLP Lib!
View What HF can do what we cannot do


nlu.load_dataset()
"""

nlu.load('pdf2text med_ner').predict(ocr_level ='page', nlp_level ='document') # EACH PAGE is a seperate doc/row
nlu.load('pdf2text med_ner').predict(ocr_level ='file', nlp_level ='document') # EACH FILE is a seperate doc/row
nlu.load('pdf2text med_ner').predict(ocr_level ='object', nlp_level ='document') # EACH OBJ is a seperate doc/row
"""
Does work with table extraction?

10pages --> 

"""

@dataclass
class NLP_ANNO_TYPES(str,EnumExtended):
    # TODO high level info on Anno types
    # DOCUMENT_XX can be sbustituted for SENTENCE
    TOKEN_CLASSIFIER = 'token_classifier'
    CHUNK_CLASSIFIER = 'chunk_classifier'  # ASSERTION/ NER GENERATES THESE but DOES NOT TAKE THEM IN!!!
    DOCUMENT_CLASSIFIER = 'document_classifier'
    RELATION_CLASSIFIER = 'relation_classifier'  # Pairs of chunks
    TOKEN_EMBEDDING = 'token_embedding'
    CHUNK_EMBEDDING = 'chunk_embedding'
    DOCUMENT_EMBEDDING = 'document_embedding'

@dataclass
class NlpFeatureNode:  # or Mode Node? (FeatureNode)
    """A node representation for a Spark OCR Annotator
    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """

    # TODO quickfix str remove
    node: Union[JslAnnoRef] # JSL Annotator that can generate this Triplet. Could be from OCR/JSL-Internal/Spark-NLP
    ins: List[JslFeature]  # JSL Annotator that can generate this Triplet
    outs: List[JslFeature]  # JSL Annotator that can generate this Triplet


""" node representations for a  Annotators
Used to cast the pipeline dependency resolution algorithm into an abstract grpah
"""
class NlpHcFeatureNode(FeatureNode): pass
class OcrFeatureNode(FeatureNode):pass


# TODO, encode feature wether has storage_ref or not?
# TODO update more granular
@dataclass
class NLP_FEATURES(JslFeature,EnumExtended):
    """
    NLP Feature aka Annotator Types
        ---> TODO even more granualar, chunk/entity, RELATION and more!
    """
    NLP_GENERATED_RAW_TEXT = JslFeature("nlp_generated_raw_text") #STems from an nlp annotator in the NLP lib, i.e. Fnisher or so. Generates NO JSL-Annotation Schema for result df. Just 1 str per orw
    DOCUMENT = JslFeature("document")
    SENTENCE = JslFeature("sentence")
    TOKEN = JslFeature("token")
    WORDPIECE = JslFeature("wordpiece")
    ANY = JslFeature("any")
    ANY_FINISHED = JslFeature("any_finished")
    ANY_EMBEDDINGS = JslFeature("any_embeddings")
    FINISHED_EMBEDDINGS = JslFeature("word_embeddings")
    WORD_EMBEDDINGS = JslFeature("word_embeddings")
    CHUNK_EMBEDDINGS = JslFeature("chunk_embeddings")
    SENTENCE_EMBEDDINGS = JslFeature("sentence_embeddings")
    CATEGORY = JslFeature("category")
    DATE = JslFeature("date")
    MULTI_DOCUMENT_CLASSIFICATION = JslFeature('multi_document_classification')
    DOCUMENT_CLASSIFICATION = JslFeature('multi_document_classification')
    TOKEN_CLASSIFICATION = JslFeature('multi_document_classification')
    SENTIMENT = JslFeature("sentiment")
    POS = JslFeature("pos")
    CHUNK = JslFeature("chunk")
    NAMED_ENTITY_IOB = JslFeature("named_entity_iob")
    NAMED_ENTITY_CONVERTED = JslFeature("named_entity_converted")
    NEGEX = JslFeature("negex")
    DEPENDENCY = JslFeature("dependency")
    LABELED_DEPENDENCY = JslFeature("labeled_dependency")
    LANGUAGE = JslFeature("language")
    NODE = JslFeature("node")
    DUMMY = JslFeature("dummy")
@dataclass
class OCR_FEATURE(JslFeature,EnumExtended):
    """
    NLP Feature aka Annotator Types
    TODO
    """

    BINARY_IMG = JslFeature("bin_img")  # img -
    BINARY_PDF = JslFeature("bin_pdf")  # pdf
    BINARY_PPT = JslFeature("bin_ppt")  # Powerpoint
    BINARY_PDF_PAGE = JslFeature("bin_pdf_page")  # just a page
    BINARY_DOCX = JslFeature("bin_docx")  # pdf2text -
    BINARY_DOCX_PAGE = JslFeature("bin_docx_page")  # just a page
    BINARY_TOKEN = JslFeature("bin_hocr")  # img -
    BINARY_DICOM = JslFeature("bin_dicom")  # DICOM image
    DICOM_METADATA = JslFeature("dicom_metadata")  # DICOM metadata (json formatted)

    FILE_PATH = JslFeature("path") # TODO this is externalL???
    TEXT = JslFeature("text")  # TODO should be same class as the spark NLP ones TODO EXTERNANMALLL??


    TEXT_ENTITY = JslFeature('text_entity')  # chunk/entity
    TEXT_DOCUMENT = JslFeature("text_document")  # TODO should be same class as the spark NLP ones
    TEXT_DOCUMENT_TOKENIZED = JslFeature("text_tokenized")  # TODO should be same class as the spark NLP ones
    HOCR = JslFeature("bin_hocr")  # img -

    # All OCR_* features are structs generated from OCR lib
    FALL_BACK = JslFeature("fall_back")  #
    OCR_IMAGE = JslFeature("ocr_image")  # OCR struct image representation
    OCR_PAGE_MATRIX = JslFeature("ocr_page_matrix")  # OCR struct image representation
    OCR_POSITIONS = JslFeature("ocr_positions")  # OCR struct POSITION representation # TODO is POSITIONS==COORDINATES???
    OCR_REGION = JslFeature("ocr_region")  # OCR array of POSITION struct
    OCR_TEXT = JslFeature("ocr_text")  # raw text extracted by OCR anno like PDFtoImage
    OCR_TABLE = JslFeature("ocr_table")  # OCR extracted table TODO array of COORDINATES/POSITION?
    OCR_TABLE_CELLS = JslFeature("ocr_table_cells")  # OCR extracted table  TODO array of COORDINATES/POSITION??
    OCR_MAPPING = JslFeature("ocr_table")  # TODO wat is MPAPING???
    PAGE_NUM = JslFeature("page_num")  # TODO is this just int or some struct?

    JSON_FOUNDATION_ONE_REPORT = JslFeature("json_foundation_one_report")

    PREDICTION_TEXT_TABLE = JslFeature("prediction_text_lable")  # TODO is this just int or some struct?
    PREDICTION_CONFIDENCE = JslFeature("prediction_confidence")  # TODO is this just int or some struct?
@dataclass
class NLP_HC_FEATURES(JslFeature,EnumExtended):
    """
    NLP Feature aka Annotator Types
        ---> TODO even more granualar, chunk/entity, RELATION and more!
    """
    DOCUMENT = JslFeature("document")
    TOKEN = JslFeature("token")
    WORDPIECE = JslFeature("wordpiece")
    WORD_EMBEDDINGS = JslFeature("word_embeddings")
    SENTENCE_EMBEDDINGS = JslFeature("sentence_embeddings")
    CATEGORY = JslFeature("category")
    DATE = JslFeature("date")
    ENTITY = JslFeature("entity")
    SENTIMENT = JslFeature("sentiment")
    POS = JslFeature("pos")
    CHUNK = JslFeature("chunk")
    NAMED_ENTITY = JslFeature("named_entity")
    NEGEX = JslFeature("negex")
    DEPENDENCY = JslFeature("dependency")
    LABELED_DEPENDENCY = JslFeature("labeled_dependency")
    LANGUAGE = JslFeature("language")
    NODE = JslFeature("node")
    DUMMY = JslFeature("dummy")

@dataclass
class EXTERNAL_NODES(str,EnumExtended):
    """
    Start Node definitions for the NLU Pipeline Graph completion logic
    These are analogus to the various input types NLU may accept
    """
    RAW_TEXT = ExternalFeature('str')
    NON_WHITESPACED_TEXT = ExternalFeature('non_whitespaced_text') # i.e. Chinese, Russian, etc..

    # TODO define how its derivable, i.e Accepted input types that can be converted to spark DF types
    # str_array = 'str_array'
    #
    # pandas_df = 'pandas_df'
    # pd_series = 'pandas_series'
    #
    # np_array = 'pandas_series'
    #
    # img_path = 'pandas_series'
    # file_path = 'file_path' # todo more granuar, i.e. by file type?

class NLP_NODES(JslAnnoRef,EnumExtended):
    """All avaiable Feature nodes in NLP..
    LVL 0 Abstraction

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    # Visual Document Understanding

    BIG_TEXT_MATCHER = JslAnnoRef('big_text_matcher')
    CHUNK2DOC = JslAnnoRef('chunk2doc')
    CHUNK_EMBEDDINGS = JslAnnoRef('chunk_embeddings')
    CHUNK_TOKENIZER = JslAnnoRef('chunk_tokenizer')
    CHUNKER = JslAnnoRef('chunker')
    CLASSIFIER_DL = JslAnnoRef('classifier_dl')
    CONTEXT_SPELL_CHECKER = JslAnnoRef('context_spell_checker')
    DATE_MATCHER = JslAnnoRef('date_matcher')
    UNTYPED_DEPENDENCY_PARSER = JslAnnoRef('untyped_dependency_parser')
    TYPED_DEPENDENCY_PARSER = JslAnnoRef('typed_dependency_parser')
    DOC2CHUNK = JslAnnoRef('doc2chunk')
    DOC2VEC = JslAnnoRef('doc2vec') # TODO ADD NODE!!


    DOCUMENT_ASSEMBLER = JslAnnoRef('document_assembler')
    DOCUMENT_NORMALIZER = JslAnnoRef('document_normalizer')
    EMBEDDINGS_FINISHER = JslAnnoRef('embeddings_finisher')
    ENTITY_RULER = JslAnnoRef('entitiy_ruler')
    FINISHER = JslAnnoRef('FINISHER')
    GRAPH_EXTRACTION = JslAnnoRef('graph_extraction')
    GRAPH_FINISHER = JslAnnoRef('graph_finisher')
    LANGUAGE_DETECTOR_DL = JslAnnoRef('language_detector_dl')
    LEMMATIZER = JslAnnoRef('lemmatizer')
    MULTI_CLASSIFIER_DL = JslAnnoRef('multi_classifier_dl')
    MULTI_DATE_MATCHER = JslAnnoRef('multi_date_matcher')
    N_GRAMM_GENERATOR = JslAnnoRef('n_gramm_generator')
    NER_CONVERTER = JslAnnoRef('ner_converter')
    NER_CRF = JslAnnoRef('ner_crf')
    NER_DL = JslAnnoRef('ner_dl')
    NER_OVERWRITER = JslAnnoRef('ner_overwriter')
    NORMALIZER = JslAnnoRef('normalizer')
    NORVIG_SPELL_CHECKER = JslAnnoRef('norvig_spell_checker')
    POS = JslAnnoRef('pos')
    RECURISVE_TOKENIZER = JslAnnoRef('recursive_tokenizer')
    REGEX_MATCHER = JslAnnoRef('regex_matcher')
    REGEX_TOKENIZER = JslAnnoRef('regex_tokenizer')
    SENTENCE_DETECTOR = JslAnnoRef('sentence_detector')
    SENTENCE_DETECTOR_DL = JslAnnoRef('sentence_detector_dl')
    SENTENCE_EMBEDDINGS = JslAnnoRef('sentence_embeddings')
    STEMMER = JslAnnoRef('stemmer')
    STOP_WORDS_CLEANER = JslAnnoRef('stop_words_cleaner')
    SYMMETRIC_DELETE_SPELLCHECKER = JslAnnoRef('symmetric_delete_spellchecker')
    TEXT_MATCHER = JslAnnoRef('text_matcher')
    TOKEN2CHUNK = JslAnnoRef('token2chunk')
    TOKEN_ASSEMBLER = JslAnnoRef('token_assembler')
    TOKENIZER = JslAnnoRef('tokenizer')
    SENTIMENT_DL = JslAnnoRef('sentiment_dl')
    SENTIMENT_DETECTOR = JslAnnoRef('sentiment_detector')
    VIVEKN_SENTIMENT = JslAnnoRef('vivekn_sentiment')
    WORD_EMBEDDINGS = JslAnnoRef('word_embeddings')
    WORD_SEGMENTER = JslAnnoRef('word_segmenter')
    YAKE_KEYWORD_EXTRACTION = JslAnnoRef('yake_keyword_extraction')
    ALBERT_EMBEDDINGS = JslAnnoRef('albert_embeddings')
    ALBERT_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('albert_for_token_classification')
    BERT_EMBEDDINGS = JslAnnoRef('bert_embeddings')
    BERT_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('bert_for_token_classification')
    BERT_SENTENCE_EMBEDDINGS = JslAnnoRef('bert_sentence_embeddings')
    DISTIL_BERT_EMBEDDINGS = JslAnnoRef('distil_bert_embeddings')
    DISTIL_BERT_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('distil_bert_for_token_classification')
    DISTIL_BERT_FOR_SEQUENCE_CLASSIFICATION = JslAnnoRef('distil_bert_for_sequence_classification')
    BERT_FOR_SEQUENCE_CLASSIFICATION = JslAnnoRef('bert_for_sequence_classification')
    ELMO_EMBEDDINGS = JslAnnoRef('elmo_embeddings')
    LONGFORMER_EMBEDDINGS = JslAnnoRef('longformer_embeddings')
    LONGFORMER_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('longformer_for_token_classification')
    MARIAN_TRANSFORMER = JslAnnoRef('marian_transformer')
    ROBERTA_EMBEDDINGS = JslAnnoRef('roberta_embeddings')
    ROBERTA_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('roberta_for_token_classification')
    ROBERTA_SENTENCE_EMBEDDINGS = JslAnnoRef('roberta_for_token_classification')
    T5_TRANSFORMER = JslAnnoRef('t5_transformer')
    UNIVERSAL_SENTENCE_ENCODER = JslAnnoRef('universal_sentence_encoder')
    XLM_ROBERTA_EMBEDDINGS = JslAnnoRef('xlm_roberta_embeddings')
    XLM_ROBERTA_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('xlm_roberta_for_token_classification')
    XLM_ROBERTA_SENTENCE_EMBEDDINGS = JslAnnoRef('xlm_roberta_sentence_embeddings')
    XLNET_EMBEDDINGS = JslAnnoRef('xlnet_embeddings')
    XLNET_FOR_TOKEN_CLASSIFICATION = JslAnnoRef('xlnet_for_token_classification')

    ## APPROACHES TODO INTEGRATE
    TRAINABLE_VIVEKN_SENTIMENT = JslAnnoRef('trainable_vivekn_sentiment')
    TRAINABLE_SENTIMENT_DL = JslAnnoRef('trainable_sentiment_dl')
    TRAINABLE_CLASSIFIER_DL = JslAnnoRef('trainable_classifier_dl')
    TRAINABLE_MULTI_CLASSIFIER_DL = JslAnnoRef('trainable_multi_classifier_dl')
    TRAINABLE_NER_DL = JslAnnoRef('trainable_ner_dl')
    TRAINABLE_NER_CRF = JslAnnoRef('trainable_ner_crf')
    TRAINABLE_POS = JslAnnoRef('trainable_pos')
    TRAINABLE_DEP_PARSE_TYPED = JslAnnoRef('trainable_dependency_parser') # TODO NODE!!
    TRAINABLE_DEP_PARSE_UN_TYPED = JslAnnoRef('trainable_dependency_parser_untyped') # TODO NODE!!
    TRAINABLE_DOC2VEC = JslAnnoRef('trainable_doc2vec') # TODO NDOE!!!
    TRAINABLE_ENTITY_RULER =  JslAnnoRef('trainable_entity_ruler') # TODO NDOE!!!
    TRAINABLE_LEMMATIZER =  JslAnnoRef('trainable_lemmatizer') # TODO NDOE!!!
    TRAINABLE_NORMALIZER =  JslAnnoRef('trainable_normalizer') # TODO NDOE!!!
    TRAINABLE_NORVIG_SPELL_CHECKER =  JslAnnoRef('trainable_norvig_spell') # TODO NDOE!!!
    TRAINABLE_RECURISVE_TOKENIZER =  JslAnnoRef('trainable_recursive_tokenizer') # TODO NDOE!!!
    TRAINABLE_REGEX_MATCHER =  JslAnnoRef('trainable_regex_tokenizer') # TODO NDOE!!!
    TRAINABLE_SENTENCE_DETECTOR_DL =  JslAnnoRef('trainable_sentence_detector_dl') # TODO NDOE!!!
    TRAINABLE_SENTIMENT =  JslAnnoRef('trainable_sentiment') # TODO NDOE!!!
    TRAINABLE_WORD_EMBEDDINGS =  JslAnnoRef('trainable_word_embeddings') # TODO NDOE!!!
    TRAINABLE_SYMMETRIC_DELETE_SPELLCHECKER =  JslAnnoRef('trainable_symmetric_spell_checker') # TODO NDOE!!!
    TRAINABLE_TEXT_MATCHER =  JslAnnoRef('trainable_text_matcher') # TODO NDOE!!!
    TRAINABLE_TOKENIZER =  JslAnnoRef('trainable_tokenizer') # TODO NDOE!!!
    TRAINABLE_WORD_SEGMENTER =  JslAnnoRef('trainable_word_segmenter') # TODO NDOE!!!


@dataclass
class NLP_HC_NODES(EnumExtended):  # or Mode Node?
    """All avaiable Feature nodes in OCR

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    # Visual Document Understanding

@dataclass
class OCR_NODES(EnumExtended):  # or Mode Node?
    """All avaiable Feature nodes in OCR

    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    # Visual Document Understanding
    VISUAL_DOCUMENT_CLASSIFIER = JslAnnoRef('visual_document_classifier')
    VISUAL_DOCUMENT_NER = JslAnnoRef('visual_document_NER')

    # Object Detection
    IMAGE_HANDWRITTEN_DETECTOR = JslAnnoRef('image_handwritten_detector')

    # TABLE Processors/Recognition
    IMAGE_TABLE_DETECTOR = JslAnnoRef('image_table_detector')
    IMAGE_TABLE_CELL_DETECTOR = JslAnnoRef('image_table_cell_detector')
    IMAGE_TABLE_CELL2TEXT_TABLE = JslAnnoRef('image_table_cell2text_table')

    # PDF Processing
    PDF2TEXT = JslAnnoRef('pdf2text')
    PDF2IMAGE = JslAnnoRef('pdf2image')
    IMAGE2PDF = JslAnnoRef('image2pdf')
    TEXT2PDF = JslAnnoRef('text2pdf')
    PDF_ASSEMBLER = JslAnnoRef('pdf_assembler')
    PDF_DRAW_REGIONS = JslAnnoRef('pdf_draw_regions')
    PDF2TEXT_TABLE = JslAnnoRef('pdf2text_table')

    # DOCX Processing
    DOC2TEXT = JslAnnoRef('doc2text')
    DOC2TEXT_TABLE = JslAnnoRef('doc2text_table')
    DOC2PDF = JslAnnoRef('doc2pdf')
    PPT2TEXT_TABLE = JslAnnoRef('ppt2text_table')
    PPT2PDF = JslAnnoRef('ppt2pdf')

    # DICOM Processing
    DICOM2IMAGE = JslAnnoRef('dicom2image')
    IMAGE2DICOM = JslAnnoRef('IMAGE2DICOM')

    # Image Pre-Processing
    BINARY2IMAGE = JslAnnoRef('binary2image')
    GPU_IMAGE_TRANSFORMER = JslAnnoRef('GPU_IMAGE_TRANSFORMER')
    IMAGE_BINARIZER = JslAnnoRef('image_binarizer')
    IMAGE_ADAPTIVE_BINARIZER = JslAnnoRef('image_adaptive_binarizer')
    IMAGE_ADAPTIVE_THRESHOLDING = JslAnnoRef('image_adaptive_thresholding')
    IMAGE_SCALER = JslAnnoRef('image_scaler')
    IMAGE_ADAPTIVE_SCALER = JslAnnoRef('image_adaptive_scaler')
    IMAGE_SKEW_CORRECTOR = JslAnnoRef('image_skew_corrector')
    IMAGE_NOISE_SCORER = JslAnnoRef('image_noise_scorer')
    IMAGE_REMOVE_OBJECTS = JslAnnoRef('image_remove_objects')
    IMAGE_MORPHOLOGY_OPERATION = JslAnnoRef('image_morphology_operation')
    IMAGE_CROPPER = JslAnnoRef('image_cropper')
    IMAGE2REGION = JslAnnoRef('image2region')
    IMAGE_LAYOUT_ANALZYER = JslAnnoRef('image_layout_analyzer')
    IMAGE_SPLIT_REGIONS = JslAnnoRef('image_split_regions')
    IMAGE_DRAW_REGIONS = JslAnnoRef('image_draw_regions')

    # Character Recognition
    IMAGE2TEXT = JslAnnoRef('image2text')
    IMAGE2TEXTPDF = JslAnnoRef('image2textpdf')
    IMAGE2HOCR = JslAnnoRef('image2hocr')
    IMAGE_BRANDS2TEXT = JslAnnoRef('image_brands2text')

    # Other
    POSITION_FINDER = JslAnnoRef('position_finder')
    UPDATE_TEXT_POSITION = JslAnnoRef('update_text_position')
    FOUNDATION_ONE_REPORT_PARSER = JslAnnoRef('foundation_one_report_parser')
    HOCR_DOCUMENT_ASSEMBLER = JslAnnoRef('hocr_document_assembler')
    HOCR_TOKENIZER = JslAnnoRef('hocr_tokenizer')

class NLP_FEATURE_NODES(EnumExtended):  # or Mode Node?
    """All avaiable Feature nodes in Spark NLP
    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """
    # Visual Document Understanding
    E = EXTERNAL_NODES
    A = NLP_NODES
    F = NLP_FEATURES
    BIG_TEXT_MATCHER = NlpFeatureNode(A.BIG_TEXT_MATCHER, [F.DOCUMENT, F.TOKEN], [F.CHUNK])
    CHUNK2DOC = NlpFeatureNode(A.CHUNK2DOC, [F.CHUNK], [F.DOCUMENT])
    CHUNK_EMBEDDINGS = NlpFeatureNode(A.CHUNK_EMBEDDINGS, [F.CHUNK, F.WORD_EMBEDDINGS], [F.CHUNK_EMBEDDINGS])
    CHUNK_TOKENIZER = NlpFeatureNode(A.CHUNK_TOKENIZER, [F.CHUNK], [F.TOKEN])
    CHUNKER = NlpFeatureNode(A.CHUNKER, [F.DOCUMENT, F.POS], [F.CHUNK])
    CLASSIFIER_DL = NlpFeatureNode(A.CLASSIFIER_DL, [F.SENTENCE_EMBEDDINGS], [F.CATEGORY])
    CONTEXT_SPELL_CHECKER = NlpFeatureNode(A.CONTEXT_SPELL_CHECKER, [F.TOKEN], [F.TOKEN])
    DATE_MATCHER = NlpFeatureNode(A.DATE_MATCHER, [F.DOCUMENT], [F.DATE])
    DEPENDENCY_PARSER = NlpFeatureNode(A.UNTYPED_DEPENDENCY_PARSER, [F.DOCUMENT, F.POS, F.TOKEN], [F.DEPENDENCY])
    TYPED_DEPENDENCY_PARSER = NlpFeatureNode(A.TYPED_DEPENDENCY_PARSER, [F.TOKEN, F.POS, F.DEPENDENCY], [F.LABELED_DEPENDENCY])
    DOC2CHUNK = NlpFeatureNode(A.DOC2CHUNK, [F.DOCUMENT], [F.CHUNK])
    DOCUMENT_ASSEMBLER = NlpFeatureNode(A.DOCUMENT_ASSEMBLER, [E.RAW_TEXT], [F.DOCUMENT])
    DOCUMENT_NORMALIZER = NlpFeatureNode(A.DOCUMENT_NORMALIZER, [F.DOCUMENT], [F.DOCUMENT])
    EMBEDDINGS_FINISHER = NlpFeatureNode(A.EMBEDDINGS_FINISHER, [F.ANY_EMBEDDINGS], [F.FINISHED_EMBEDDINGS])
    # ENTITY_RULER = NlpFeatureNode(A.ENTITY_RULER, [F.], [F.]) # TODO??
    FINISHER = NlpFeatureNode(A.FINISHER, [F.ANY], [F.ANY_FINISHED])
    GRAPH_EXTRACTION = NlpFeatureNode(A.GRAPH_EXTRACTION, [F.DOCUMENT, F.TOKEN, F.NAMED_ENTITY_IOB], [F.NODE])
    # GRAPH_FINISHER = NlpFeatureNode(A.GRAPH_FINISHER, [F.], [F.])
    LANGUAGE_DETECTOR_DL = NlpFeatureNode(A.LANGUAGE_DETECTOR_DL, [F.DOCUMENT], [F.LANGUAGE])
    LEMMATIZER = NlpFeatureNode(A.LEMMATIZER, [F.TOKEN], [F.TOKEN])
    MULTI_CLASSIFIER_DL = NlpFeatureNode(A.MULTI_CLASSIFIER_DL, [F.SENTENCE_EMBEDDINGS], [F.MULTI_DOCUMENT_CLASSIFICATION])
    MULTI_DATE_MATCHER = NlpFeatureNode(A.MULTI_DATE_MATCHER, [F.DOCUMENT], [F.DATE])
    N_GRAMM_GENERATOR = NlpFeatureNode(A.N_GRAMM_GENERATOR, [F.TOKEN], [F.CHUNK])
    NER_CONVERTER = NlpFeatureNode(A.NER_CONVERTER, [F.NAMED_ENTITY_IOB], [F.NAMED_ENTITY_CONVERTED])
    NER_CRF = NlpFeatureNode(A.NER_CRF, [F.DOCUMENT, F.TOKEN, F.WORD_EMBEDDINGS], [F.NAMED_ENTITY_IOB])
    NER_DL = NlpFeatureNode(A.NER_DL, [F.DOCUMENT, F.TOKEN, F.WORD_EMBEDDINGS], [F.NAMED_ENTITY_IOB])
    NER_OVERWRITER = NlpFeatureNode(A.NER_OVERWRITER, [F.NAMED_ENTITY_IOB], [F.NAMED_ENTITY_IOB])
    NORMALIZER = NlpFeatureNode(A.NORMALIZER, [F.TOKEN], [F.TOKEN])
    NORVIG_SPELL_CHECKER = NlpFeatureNode(A.NORVIG_SPELL_CHECKER, [F.TOKEN], [F.TOKEN])
    POS = NlpFeatureNode(A.POS, [F.TOKEN, F.DOCUMENT], [F.POS])
    RECURISVE_TOKENIZER = NlpFeatureNode(A.RECURISVE_TOKENIZER, [F.DOCUMENT], [F.TOKEN])
    REGEX_MATCHER = NlpFeatureNode(A.REGEX_MATCHER, [F.DOCUMENT], [F.CHUNK])
    REGEX_TOKENIZER = NlpFeatureNode(A.REGEX_TOKENIZER, [F.DOCUMENT], [F.TOKEN])
    SENTENCE_DETECTOR = NlpFeatureNode(A.SENTENCE_DETECTOR, [F.DOCUMENT], [F.SENTENCE])
    SENTENCE_DETECTOR_DL = NlpFeatureNode(A.SENTENCE_DETECTOR_DL, [F.DOCUMENT], [F.SENTENCE])
    SENTENCE_EMBEDDINGS = NlpFeatureNode(A.SENTENCE_EMBEDDINGS, [F.DOCUMENT, F.WORD_EMBEDDINGS], [F.SENTENCE_EMBEDDINGS])

    SENTIMENT_DL = NlpFeatureNode(A.SENTIMENT_DL, [F.SENTENCE_EMBEDDINGS], [F.DOCUMENT_CLASSIFICATION])
    # SENTENCE_DETECTOR = NlpFeatureNode(A.SENTENCE_DETECTOR, [F.TOKEN, F.DOCUMENT], [F.DOCUMENT_CLASSIFICATION])
    STEMMER = NlpFeatureNode(A.STEMMER, [F.TOKEN], [F.TOKEN])
    STOP_WORDS_CLEANER = NlpFeatureNode(A.STOP_WORDS_CLEANER, [F.TOKEN], [F.TOKEN])
    SYMMETRIC_DELETE_SPELLCHECKER = NlpFeatureNode(A.SYMMETRIC_DELETE_SPELLCHECKER, [F.TOKEN], [F.TOKEN])
    TEXT_MATCHER = NlpFeatureNode(A.TEXT_MATCHER, [F.DOCUMENT, F.TOKEN], [F.CHUNK])
    TOKEN2CHUNK = NlpFeatureNode(A.TOKEN2CHUNK, [F.TOKEN], [F.CHUNK])
    TOKEN_ASSEMBLER = NlpFeatureNode(A.TOKEN_ASSEMBLER, [F.DOCUMENT, F.TOKEN], [F.DOCUMENT])
    TOKENIZER = NlpFeatureNode(A.TOKENIZER, [F.DOCUMENT], [F.TOKEN])
    VIVEKN_SENTIMENT = NlpFeatureNode(A.VIVEKN_SENTIMENT, [F.TOKEN, F.DOCUMENT], [F.DOCUMENT_CLASSIFICATION])
    WORD_EMBEDDINGS = NlpFeatureNode(A.WORD_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    WORD_SEGMENTER = NlpFeatureNode(A.WORD_SEGMENTER, [F.DOCUMENT], [F.TOKEN])
    YAKE_KEYWORD_EXTRACTION = NlpFeatureNode(A.YAKE_KEYWORD_EXTRACTION, [F.TOKEN], [F.CHUNK])

    ## TODO CHANGE TRANSFORMERS TO NER_IOB ???
    ALBERT_EMBEDDINGS = NlpFeatureNode(A.ALBERT_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    ALBERT_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.ALBERT_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    BERT_EMBEDDINGS = NlpFeatureNode(A.BERT_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    BERT_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.BERT_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    BERT_SENTENCE_EMBEDDINGS = NlpFeatureNode(A.BERT_SENTENCE_EMBEDDINGS, [F.DOCUMENT], [F.SENTENCE_EMBEDDINGS])
    DISTIL_BERT_EMBEDDINGS = NlpFeatureNode(A.DISTIL_BERT_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    DISTIL_BERT_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.DISTIL_BERT_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    ELMO_EMBEDDINGS = NlpFeatureNode(A.ELMO_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    LONGFORMER_EMBEDDINGS = NlpFeatureNode(A.LONGFORMER_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    LONGFORMER_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.LONGFORMER_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    MARIAN_TRANSFORMER = NlpFeatureNode(A.MARIAN_TRANSFORMER, [F.DOCUMENT], [F.DOCUMENT])
    ROBERTA_EMBEDDINGS = NlpFeatureNode(A.ROBERTA_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    ROBERTA_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.ROBERTA_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    ROBERTA_SENTENCE_EMBEDDINGS = NlpFeatureNode(A.ROBERTA_SENTENCE_EMBEDDINGS, [F.DOCUMENT], [F.SENTENCE_EMBEDDINGS])
    T5_TRANSFORMER = NlpFeatureNode(A.T5_TRANSFORMER, [F.DOCUMENT], [F.DOCUMENT])
    UNIVERSAL_SENTENCE_ENCODER = NlpFeatureNode(A.UNIVERSAL_SENTENCE_ENCODER, [F.DOCUMENT], [F.SENTENCE_EMBEDDINGS])
    XLM_ROBERTA_EMBEDDINGS = NlpFeatureNode(A.XLM_ROBERTA_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    XLM_ROBERTA_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.XLM_ROBERTA_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])
    XLM_ROBERTA_SENTENCE_EMBEDDINGS = NlpFeatureNode(A.XLM_ROBERTA_SENTENCE_EMBEDDINGS, [F.DOCUMENT], [F.SENTENCE_EMBEDDINGS])
    XLNET_EMBEDDINGS = NlpFeatureNode(A.XLNET_EMBEDDINGS, [F.DOCUMENT, F.TOKEN], [F.WORD_EMBEDDINGS])
    XLNET_FOR_TOKEN_CLASSIFICATION = NlpFeatureNode(A.XLNET_FOR_TOKEN_CLASSIFICATION, [F.DOCUMENT, F.TOKEN], [F.TOKEN_CLASSIFICATION])

@dataclass
class OCR_FEATURE_NODES(EnumExtended):  # or Mode Node?
    """All avaiable Feature nodes in OCR
    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """

    # Visual Document Understanding
    A = OCR_NODES
    F = OCR_FEATURE
    VISUAL_DOCUMENT_CLASSIFIER = OcrFeatureNode(A.VISUAL_DOCUMENT_CLASSIFIER, [F.HOCR, F.FILE_PATH],[F.PREDICTION_TEXT_TABLE, F.PREDICTION_CONFIDENCE])
    # VISUAL_DOCUMENT_NER = OcrFeatureNode(A.VISUAL_DOCUMENT_NER, [OcrFeature.HOCR, OcrFeature.FILE_PATH], [NlpFeature.NER_Annotation]) # TODO NlpFeature Space!

    # Object Detection
    IMAGE_HANDWRITTEN_DETECTOR = OcrFeatureNode(A.IMAGE_HANDWRITTEN_DETECTOR, [F.OCR_IMAGE, ], [F.OCR_REGION])

    # TABLE Processors/Recognition TODO REGION==CELL>??
    IMAGE_TABLE_DETECTOR = OcrFeatureNode(A.IMAGE_TABLE_DETECTOR, [F.OCR_IMAGE, ],[F.OCR_TABLE])  # TODO REGION or TABLE??? IS IT THE SAME???
    IMAGE_TABLE_CELL_DETECTOR = OcrFeatureNode(A.IMAGE_TABLE_CELL_DETECTOR, [F.OCR_IMAGE, ],[F.OCR_TABLE_CELLS])  # TODO REGION or TABLE??? IS IT THE SAME???
    IMAGE_TABLE_CELL2TEXT_TABLE = OcrFeatureNode(A.IMAGE_TABLE_CELL2TEXT_TABLE, [F.OCR_IMAGE, F.OCR_TABLE_CELLS],[F.OCR_TABLE])  # TODO OUPUT!! REGION or TABLE??? IS IT THE SAME???

    # TODO are POSITIOns  and REGIONS the same??? Regions is an ARRAY of PSOTISIONS. BUT is REGION=== TABLE??? Samefor CELLs
    # PDF Processing
    PDF2TEXT = OcrFeatureNode(A.PDF2TEXT, [F.BINARY_PDF, F.FILE_PATH], [F.TEXT, F.PAGE_NUM])
    PDF2IMAGE = OcrFeatureNode(A.PDF2IMAGE, [F.BINARY_PDF, F.FILE_PATH, F.FALL_BACK], [F.OCR_IMAGE, F.PAGE_NUM])
    IMAGE2PDF = OcrFeatureNode(A.IMAGE2PDF, [F.OCR_IMAGE, F.FILE_PATH], [F.BINARY_PDF])
    TEXT2PDF = OcrFeatureNode(A.TEXT2PDF, [F.OCR_POSITIONS, F.OCR_IMAGE, F.OCR_TEXT, F.FILE_PATH, F.BINARY_PDF],[F.BINARY_PDF])
    PDF_ASSEMBLER = OcrFeatureNode(A.PDF_ASSEMBLER, [F.BINARY_PDF_PAGE, F.FILE_PATH, F.PAGE_NUM], [F.BINARY_PDF])
    PDF_DRAW_REGIONS = OcrFeatureNode(A.PDF_DRAW_REGIONS, [F.BINARY_PDF, F.FILE_PATH, F.OCR_POSITIONS], [F.BINARY_PDF])
    PDF2TEXT_TABLE = OcrFeatureNode(A.PDF2TEXT_TABLE, [F.BINARY_PDF, F.FILE_PATH, ], [F.OCR_TABLE])

    # DOCX Processing
    DOC2TEXT = OcrFeatureNode(A.DOC2TEXT, [F.BINARY_DOCX, F.FILE_PATH, ], [F.TEXT, F.PAGE_NUM])
    DOC2TEXT_TABLE = OcrFeatureNode(A.DOC2TEXT_TABLE, [F.BINARY_DOCX, F.FILE_PATH], [F.OCR_TABLE])
    DOC2PDF = OcrFeatureNode(A.DOC2PDF, [F.BINARY_DOCX, F.FILE_PATH], [F.BINARY_PDF])
    PPT2TEXT_TABLE = OcrFeatureNode(A.PPT2TEXT_TABLE, [F.BINARY_PPT, F.FILE_PATH], [F.OCR_TABLE])
    PPT2PDF = OcrFeatureNode(A.PPT2PDF, [F.BINARY_PPT, F.FILE_PATH], [F.BINARY_PDF])

    # DICOM Processing
    DICOM2IMAGE = OcrFeatureNode(A.DICOM2IMAGE, [F.BINARY_DICOM, F.FILE_PATH],[F.OCR_IMAGE, F.PAGE_NUM, F.DICOM_METADATA])
    IMAGE2DICOM = OcrFeatureNode(A.IMAGE2DICOM, [F.OCR_IMAGE, F.FILE_PATH, F.DICOM_METADATA], [F.BINARY_DICOM])
    # Image Pre-Processing
    BINARY2IMAGE = OcrFeatureNode(A.BINARY2IMAGE, [F.BINARY_IMG, F.FILE_PATH], [F.OCR_IMAGE])
    GPU_IMAGE_TRANSFORMER = OcrFeatureNode(A.GPU_IMAGE_TRANSFORMER, [F.OCR_IMAGE], [F.OCR_IMAGE])

    IMAGE_BINARIZER = OcrFeatureNode(A.IMAGE_BINARIZER, [F.OCR_IMAGE], [F.OCR_IMAGE])
    IMAGE_ADAPTIVE_BINARIZER = OcrFeatureNode(A.IMAGE_ADAPTIVE_BINARIZER, [F.OCR_IMAGE], [F.OCR_IMAGE])
    IMAGE_ADAPTIVE_THRESHOLDING = OcrFeatureNode(A.IMAGE_ADAPTIVE_THRESHOLDING, [F.OCR_IMAGE], [F.OCR_IMAGE])
    IMAGE_SCALER = OcrFeatureNode(A.IMAGE_SCALER, [F.OCR_IMAGE], [F.OCR_IMAGE])
    IMAGE_ADAPTIVE_SCALER = OcrFeatureNode(A.IMAGE_ADAPTIVE_SCALER, [F.OCR_IMAGE], [F.OCR_IMAGE])
    IMAGE_SKEW_CORRECTOR = OcrFeatureNode(A.IMAGE_SKEW_CORRECTOR, [F.OCR_IMAGE], [F.OCR_IMAGE])

    # TODO THESE ALL BLOW??? Region???
    IMAGE_NOISE_SCORER = OcrFeatureNode(A.IMAGE_NOISE_SCORER, [F.OCR_IMAGE, F.OCR_REGION],[F.OCR_IMAGE])  # TODO WHAT IS REGION???? There is no schema for that
    IMAGE_REMOVE_OBJECTS = OcrFeatureNode(A.IMAGE_REMOVE_OBJECTS, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE_MORPHOLOGY_OPERATION = OcrFeatureNode(A.IMAGE_MORPHOLOGY_OPERATION, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE_CROPPER = OcrFeatureNode(A.IMAGE_CROPPER, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE2REGION = OcrFeatureNode(A.IMAGE2PDF, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE_LAYOUT_ANALZYER = OcrFeatureNode(A.IMAGE_LAYOUT_ANALZYER, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE_SPLIT_REGIONS = OcrFeatureNode(A.IMAGE_SPLIT_REGIONS, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO
    IMAGE_DRAW_REGIONS = OcrFeatureNode(A.IMAGE_DRAW_REGIONS, [F.OCR_IMAGE], [F.OCR_IMAGE])  # TODO

    # Character Recognition .. TODO these should be correct but not 100% sure about the positions
    IMAGE2TEXT = OcrFeatureNode(A.IMAGE2TEXT, [F.OCR_IMAGE], [F.TEXT, F.OCR_POSITIONS])  # TODO
    IMAGE2TEXTPDF = OcrFeatureNode(A.IMAGE2TEXTPDF, [F.OCR_IMAGE, F.FILE_PATH, F.PAGE_NUM],[F.BINARY_PDF])  # TODO is output just normal binary PDF? Not 100% sure
    IMAGE2HOCR = OcrFeatureNode(A.IMAGE2HOCR, [F.OCR_IMAGE],[F.HOCR])  # TODO is ouput HOCR format as in HOCR_DOCUMENT_ASSAMBLER???
    IMAGE_BRANDS2TEXT = OcrFeatureNode(A.IMAGE_BRANDS2TEXT, [F.OCR_IMAGE], [F.OCR_POSITIONS, F.TEXT,F.OCR_IMAGE])  # TODO what is the STRUCTURE of output image_brand ??? OCR_IE??

    # Other
    ## Find Positions of text in image
    POSITION_FINDER = OcrFeatureNode(A.POSITION_FINDER, [F.TEXT_ENTITY, F.OCR_PAGE_MATRIX],[F.OCR_POSITIONS])  # TODO COORDINATE==POSITION??
    ##  TODO Updates text at a position? I.e. Change the text at given corodinates BUT THEN why is output position???
    UPDATE_TEXT_POSITION = OcrFeatureNode(A.POSITION_FINDER, [F.OCR_POSITIONS, F.TEXT_ENTITY],[F.OCR_POSITIONS])  # TODO COORDINATE==POSITION??
    ## Cancer Document Test parser. Required Text of Header Field of something
    FOUNDATION_ONE_REPORT_PARSER = OcrFeatureNode(A.FOUNDATION_ONE_REPORT_PARSER, [F.OCR_TEXT, F.FILE_PATH],[F.JSON_FOUNDATION_ONE_REPORT])

    # HOCR
    HOCR_DOCUMENT_ASSEMBLER = OcrFeatureNode(A.HOCR_TOKENIZER, [F.HOCR], [F.TEXT_DOCUMENT])
    HOCR_TOKENIZER = OcrFeatureNode(A.HOCR_TOKENIZER, [F.HOCR], [F.TEXT_DOCUMENT_TOKENIZED])


@dataclass # TODO!!!
class NLP_HC_FEATURE_NODES(EnumExtended):  # or Mode Node?
    """All avaiable Feature nodes in OCR
    Used to cast the pipeline dependency resolution algorithm into an abstract grpah
    """

    # Visual Document Understanding
    A = OCR_NODES
    F = OCR_FEATURE
    # HOCR
    HOCR_DOCUMENT_ASSEMBLER = OcrFeatureNode(A.HOCR_TOKENIZER, [F.HOCR], [F.TEXT_DOCUMENT])
    HOCR_TOKENIZER = OcrFeatureNode(A.HOCR_TOKENIZER, [F.HOCR], [F.TEXT_DOCUMENT_TOKENIZED])


@dataclass
class ComponentConstructorArgs:
    """
    Arguments for creating a NLU component

    """
    # TODO encode output_level
    ## TODO pretty __repr__ or __to__string() method! Leverage  SparkNLPExtractor fields
    # These 4 Params are required for construction, rest is optional.. deducted dynamically from nlu_ref to build any type of NluComponent
    nlp_ref: str
    nlu_ref: str
    anno_class: JslAnnoRef  # Input/Output TYPE # What annotator class is the model for ? IMMUTABLE
    lang: str = 'en'
    bucket: Optional[str] = None # None for OpenSource and ??? fopr healthcare


    reason: str = ''  # Why was this component added to the pipe. TODO integrate/optional
    is_licensed: bool = False
    get_default_model: bool = True  # Input/Output TYPE  # Should load default model for this Component class? If true, will ignore nlu/nlp ref
    get_trainable_model: bool = False  # Input/Output TYPE  # Should load default model for this Component class? If true, will ignore nlu/nlp ref
    model: AnnotatorTransformer = None  # Optionally a Spark NLP Annotator can be provided and wrapped as component. If provided, no annotator wi be created.
    infer_anno_class: bool = False  # Wether to use input param anno_class or to deduct it from nlu ref and nlp ref, i.e. Type Deduction TODO this is currently called do_ref_checks
    loaded_from_pretrained_pipe: bool = False  # If loaded from pretrained Spark NLP pipeline. In this case model param should not be None
@dataclass
class NluComponent: # TODO just call this NLU componentt?
    # TODO this should also Contain Extractors and col NAMING utils and PANDAS COL NAMES because why not put it here!!!!!
    # TODO we could extract the class Signature programmatically and make it avaiable like a Json like soldity intervaes.. Then do pyvm Shenanigans..;)
    """Contains various metadata about the loaded component"""
    # TODO def __

    name : str # Name for this anno
    type: str  # this tells us which kind of component this is
    get_default_model : Optional[Callable[[],AnnotatorTransformer]] # Returns Concrete JSL Annotator object.
    get_pretrained_model : Optional[Callable[[str,str,str], AnnotatorTransformer]] # Returns Concrete JSL Annotator object. May by None lang,name, bukcet
    get_trainable_model : Optional[Callable[[],AnnotatorTransformer]] # Returns Concrete JSL Annotator object. May by None  # todo a bit redundant because we also have trainable ndoes.. Maybe instead define get_trainable_component() that gives the comp hhandle to the trainable thing twith get_model() method?
    # TODO BAD LAZY SIGNATURE ADDEF FOR CALLABLES BELLOW
    pdf_extractor_methods : Dict[str,Callable[[],any]] # Extractor method applicable to Pandas DF for getting pretty outputs
    # sdf_extractor_methods : Dict[str,Callable[[],any]] # Extractor method applicable to Spark  DF for getting pretty outputs # TODO NOT IN BUILD
    pdf_col_name_substitutor : Callable[[],any] # substitution method for renaming final cols to somthing redable
    # sdf_col_name_substitutor : Optional[Callable[[],any]] # substitution method for renaming final cols to somthing redable # TODO  NOT IN BUILD
    output_level: NlpLevel   # Output level of the component for data transformation logic or call it putput mapping??
    node : NlpFeatureNode  # Graph node
    description: str  # general annotator/model/component/pipeline info
    provider: str  # Who provides the implementation of this annotator, Spark-NLP for base. Would be
    license: LicenseType  # open source or private
    computation_context: str  # Will this component do its computation in Spark land (like all of Spark NLP annotators do) or does it require some other computation engine or library like Tensorflow, Numpy, HuggingFace, etc..
    output_context: str  # Will this components final result
    trainable: bool
    jsl_anno_class: JslAnnoRef # JSL Annotator Class this belongs to
    jsl_anno_py_class: JslAnnoPyClass # JSL Annotator Class this belongs to
    jsl_anno_java_class: JslAnnoJavaClass # JSL Annotator Class this belongs to
    language: [LanguageIso] = None
    constructor_args : ComponentConstructorArgs = None # Args used to originally create this component
    nlu_ref: str = None
    nlp_ref: str = None
    in_types: List[JslFeature] = None
    out_types: List[JslFeature] = None
    in_types_default: List[JslFeature] = None
    out_types_default: List[JslFeature] = None
    spark_input_column_names: List[str] = None
    spark_output_column_names: List[str] = None
    paramMap : Dict[Any,Any] = None
    paramSetterMap : Dict[Any,Any] = None
    paramGetterMap : Dict[Any,Any] = None
    model: AnnotatorTransformer  = None # Any anno class. Needs to be Any, so we can cover unimported HC models
    storage_ref: Optional[str] = None
    storage_ref_nlu_ref_resolution: Optional[str] = None # nlu_ref corrosponding to storage_ref
    loaded_from_pretrained_pipe: bool = False # If this component was derived from a pre-build SparkNLP pipeline or from NLU
    has_storage_ref: bool = False
    storage_ref_consumer: bool = False
    storage_ref_producer: bool = False

    # def __init__(self):
    #     in_types: List[JslFeature] = self.node.outs
    #     out_types: List[JslFeature] = self.node.ins
    #     in_types_default: List[JslFeature] = self.node.outs
    #     out_types_default: List[JslFeature] = self.node.ins
    #     spark_input_column_names: List[str] = self.node.outs
    #     spark_output_column_names: List[str] = self.node.ins


    def __str__(self):return f'Component({self.name}, {self.type})' # TODO more? Make it nice readable in debugger



#### Helper Accesors/ Collective Universes
class JSL_FEATURE(EnumExtended):
    # All possible Edges in a graph. We use names seperate from classNames to identify nodes, because it makes this language agnostic and not biased towards Scala/Py api..
    OCR = OCR_FEATURE
    NLP = NLP_FEATURES
    NLP_HC = NLP_HC_FEATURES

class JSL_NODES(EnumExtended):
    # All possible Nodes
    OCR = OCR_NODES
    NLP = NLP_NODES
    NLP_HC = NLP_HC_NODES

class JSL_FEATURE_NODES(EnumExtended):
    # All possible Nodes
    OCR = OCR_FEATURE_NODES
    NLP = NLP_FEATURE_NODES
    NLP_HC = NLP_HC_FEATURE_NODES ##? ? TODO!!!!!!


class AnnoClassRef:
    A_O = OCR_NODES
    A_H = None # NLP_HC_ANNO
    A_N = NLP_NODES
    # Py class names are not unique across libs unless we use full class path
    JSL_anno2_py_class : Dict[JslAnnoRef, JslAnnoPyClass] = {

        NLP_NODES.BIG_TEXT_MATCHER :  'sparknlp.annotator.BigTextMatcher',
        A_N.CHUNK2DOC :  'sparknlp.base.Chunk2Doc',
        A_N.CHUNK_EMBEDDINGS :  'sparknlp.annotator.ChunkEmbeddings',
        A_N.CHUNK_TOKENIZER :  'sparknlp.annotator.Tokenizer',
        A_N.CHUNKER :  'sparknlp.common.AnnotatorModel',
        A_N.CLASSIFIER_DL : 'sparknlp.annotator.ClassifierDLModel',
        A_N.CONTEXT_SPELL_CHECKER :  'sparknlp.annotator.ContextSpellCheckerApproach',
        A_N.DATE_MATCHER :  'sparknlp.annotator.DateMatcher',
        A_N.UNTYPED_DEPENDENCY_PARSER : 'sparknlp.annotator.DependencyParserApproach',
        A_N.TYPED_DEPENDENCY_PARSER :  'sparknlp.annotator.DependencyParserModel',
        A_N.DOC2CHUNK :  'sparknlp.base.Doc2Chunk',
        A_N.DOC2VEC :  'sparknlp.annotator.Doc2VecModel',

        A_N.DOCUMENT_ASSEMBLER :  'sparknlp.base.DocumentAssembler',
        A_N.DOCUMENT_NORMALIZER :  'sparknlp.base.DocumentAssembler',
        A_N.EMBEDDINGS_FINISHER :  'sparknlp.base.EmbeddingsFinisher',
        A_N.ENTITY_RULER :  'sparknlp.annotator.EntityRulerModel',
        A_N.FINISHER :  'sparknlp.base.Finisher',
        A_N.GRAPH_EXTRACTION :  'sparknlp.annotator.GraphExtraction',
        A_N.GRAPH_FINISHER :  'sparknlp.base.GraphFinisher',
        A_N.LANGUAGE_DETECTOR_DL :  'sparknlp.annotator.LanguageDetectorDL',
        A_N.LEMMATIZER :  'sparknlp.annotator.LemmatizerModel',
        A_N.MULTI_CLASSIFIER_DL :  'sparknlp.annotator.MultiClassifierDLModel',
        A_N.MULTI_DATE_MATCHER :  'sparknlp.annotator.MultiDateMatcher',
        A_N.N_GRAMM_GENERATOR :  'sparknlp.annotator.NGramGenerator',
        A_N.NER_CONVERTER :  'sparknlp.annotator.NerConverter',
        A_N.NER_CRF :  'sparknlp.annotator.NerCrfModel',
        A_N.NER_DL :  'sparknlp.annotator.NerDLModel',
        A_N.NER_OVERWRITER :  'sparknlp.annotator.NerOverwriter',
        A_N.NORMALIZER :  'sparknlp.annotator.NormalizerModel',
        A_N.NORVIG_SPELL_CHECKER :  'sparknlp.annotator.NorvigSweetingModel',
        A_N.POS :  'sparknlp.annotator.PerceptronModel',
        A_N.RECURISVE_TOKENIZER :  'sparknlp.annotator.RecursiveTokenizerModel',

        A_N.REGEX_MATCHER :  'sparknlp.annotator.RegexMatcherModel',
        A_N.REGEX_TOKENIZER :  'sparknlp.annotator.RegexTokenizer',
        A_N.SENTENCE_DETECTOR :  'sparknlp.annotator.SentenceDetector',
        A_N.SENTENCE_DETECTOR_DL :  'sparknlp.annotator.SentenceDetectorDLModel',
        A_N.SENTENCE_EMBEDDINGS :  'sparknlp.annotator.SentenceEmbeddings',
        A_N.STEMMER :  'sparknlp.annotator.Stemmer',
        A_N.STOP_WORDS_CLEANER :  'sparknlp.annotator.StopWordsCleaner',
        A_N.SYMMETRIC_DELETE_SPELLCHECKER :  'sparknlp.annotator.SymmetricDeleteModel',
        A_N.TEXT_MATCHER :  'sparknlp.annotator.TextMatcherModel',
        A_N.TOKEN2CHUNK :  'sparknlp.annotator.Token2Chunk',
        A_N.TOKEN_ASSEMBLER :  'sparknlp.base.TokenAssembler',
        A_N.TOKENIZER :  'sparknlp.annotator.TokenizerModel',
        A_N.SENTIMENT_DL :  'sparknlp.annotator.SentimentDLModel',
        A_N.SENTIMENT_DETECTOR :  'sparknlp.annotator.SentimentDetectorModel',
        A_N.VIVEKN_SENTIMENT :  'sparknlp.annotator.ViveknSentimentModel',
        A_N.WORD_EMBEDDINGS :  'sparknlp.annotator.WordEmbeddingsModel',
        A_N.WORD_SEGMENTER :  'sparknlp.annotator.WordSegmenterModel',
        A_N.YAKE_KEYWORD_EXTRACTION :  'sparknlp.annotator.YakeKeywordExtraction',
        A_N.ALBERT_EMBEDDINGS :  'sparknlp.annotator.AlbertEmbeddings',
        A_N.ALBERT_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.AlbertForTokenClassification',
        A_N.BERT_EMBEDDINGS :  'sparknlp.annotator.BertEmbeddings',
        A_N.BERT_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.BertForTokenClassification',
        A_N.BERT_SENTENCE_EMBEDDINGS :  'sparknlp.annotator.BertSentenceEmbeddings',
        A_N.DISTIL_BERT_EMBEDDINGS :  'sparknlp.annotator.DistilBertEmbeddings',
        A_N.DISTIL_BERT_FOR_SEQUENCE_CLASSIFICATION :  'sparknlp.annotator.DistilBertForSequenceClassification',
        A_N.BERT_FOR_SEQUENCE_CLASSIFICATION :  'sparknlp.annotator.DistilBertForSequenceClassification',
        A_N.ELMO_EMBEDDINGS :  'sparknlp.annotator.ElmoEmbeddings',
        A_N.LONGFORMER_EMBEDDINGS :  'sparknlp.annotator.LongformerEmbeddings',
        A_N.LONGFORMER_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.MarianTransformer',
        A_N.MARIAN_TRANSFORMER :  'sparknlp.annotator.MarianTransformer',
        A_N.ROBERTA_EMBEDDINGS :  'sparknlp.annotator.RoBertaEmbeddings',
        A_N.ROBERTA_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.RoBertaForTokenClassification',
        A_N.ROBERTA_SENTENCE_EMBEDDINGS :  'sparknlp.annotator.RoBertaSentenceEmbeddings',
        A_N.T5_TRANSFORMER :  'sparknlp.annotator.T5Transformer',
        A_N.UNIVERSAL_SENTENCE_ENCODER :  'sparknlp.annotator.UniversalSentenceEncoder',
        A_N.XLM_ROBERTA_EMBEDDINGS :  'sparknlp.annotator.XlmRoBertaEmbeddings',
        A_N.XLM_ROBERTA_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.XlmRoBertaForTokenClassification',
        A_N.XLM_ROBERTA_SENTENCE_EMBEDDINGS :  'sparknlp.annotator.XlmRoBertaSentenceEmbeddings',
        A_N.XLNET_EMBEDDINGS :  'sparknlp.annotator.XlnetEmbeddings',
        A_N.XLNET_FOR_TOKEN_CLASSIFICATION :  'sparknlp.annotator.XlnetForTokenClassification',

        A_N.TRAINABLE_VIVEKN_SENTIMENT :  'sparknlp.annotator.ViveknSentimentApproach',
        A_N.TRAINABLE_SENTIMENT :  'sparknlp.annotator.SentimentDetector',
        A_N.TRAINABLE_SENTIMENT_DL :  'sparknlp.annotator.SentimentDLApproach',
        A_N.TRAINABLE_CLASSIFIER_DL : 'sparknlp.annotator.ClassifierDLApproach',
        A_N.TRAINABLE_MULTI_CLASSIFIER_DL :  'sparknlp.annotator.MultiClassifierDLApproach',
        A_N.TRAINABLE_NER_DL :  'sparknlp.annotator.NerDLApproach',
        A_N.TRAINABLE_NER_CRF :  'sparknlp.annotator.NerCrfApproach',

        A_N.TRAINABLE_POS :  'sparknlp.annotator.PerceptronApproach',
        A_N.TRAINABLE_DEP_PARSE_TYPED : 'sparknlp.annotator.DependencyParserApproach',
        A_N.TRAINABLE_DEP_PARSE_UN_TYPED : 'sparknlp.annotator.TypedDependencyParserApproach',
        A_N.TRAINABLE_DOC2VEC :  'sparknlp.annotator.Doc2VecApproach',
        A_N.TRAINABLE_ENTITY_RULER :  'sparknlp.annotator.EntityRulerApproach',
        A_N.TRAINABLE_LEMMATIZER :  'sparknlp.annotator.Lemmatizer',
        A_N.TRAINABLE_NORMALIZER :  'sparknlp.annotator.Normalizer',
        A_N.TRAINABLE_NORVIG_SPELL_CHECKER :  'sparknlp.annotator.NorvigSweetingApproach',
        A_N.TRAINABLE_RECURISVE_TOKENIZER :  'sparknlp.annotator.RecursiveTokenizer',
        A_N.TRAINABLE_REGEX_MATCHER :  'sparknlp.annotator.RegexMatcher',
        A_N.TRAINABLE_SENTENCE_DETECTOR_DL : 'sparknlp.annotator.SentenceDetectorDLApproach',
        A_N.TRAINABLE_WORD_EMBEDDINGS :  'sparknlp.annotator.WordEmbeddings',
        A_N.TRAINABLE_SYMMETRIC_DELETE_SPELLCHECKER : 'sparknlp.annotator.SymmetricDeleteApproach',
        A_N.TRAINABLE_TEXT_MATCHER : 'sparknlp.annotator.TextMatcher',
        A_N.TRAINABLE_TOKENIZER :  'sparknlp.annotator.Tokenizer',
        A_N.TRAINABLE_WORD_SEGMENTER :  'sparknlp.annotator.WordSegmenterApproach',



    }

    # Java references Programmatically generated find_java_class_definition_line() (TODO)
    JSL_anno_ref_2_java_class : Dict[JslAnnoRef, JslAnnoJavaClass]= {

        A_N.CLASSIFIER_DL:'TODO'
    }


# TODO Feature resolution!!! Sometimes there are multiple candidates for a feature, which one to pick?
# ==> Use entire pipe state for resoluton and not only the component itselF???







class NluComponentFactory():

    def __init__(self, c_args : ComponentConstructorArgs):
        """
        Constrcut 1 Single NLU Component. If used for pretrained pipe, this neeeds a extra clean up call on the final pipe object
        May construct trainable components
        """
        # Gets
        # 1. Verify Ref is correct or deduct it
        if c_args.infer_anno_class :
            c_args.anno_class = 'todo infer..'
            NotImplementedError("TODO")

        # Intelij type inference fails here unless we re-create the component type :( but near 0 overhead so yay
        # Grab the Base Empty Component for this. TODO make sure this makes fresh objects and NOT POINTERS!!
        component = anno2compInfo[JslAnnoRef(c_args.anno_class)]
        component.constructor_args = c_args
        # 2. Load Annotator Class into JVM and to component if its not loaded from Pretrained Spark NLP Pipe
        if c_args.model and c_args.loaded_from_pretrained_pipe:
            component.model = c_args.model
            component.loaded_from_pretrained_pipe = True
        else :
            if c_args.get_default_model :
                component.model = component.get_default_model()
            elif c_args.get_trainable_model :
                component.model = component.get_trainable_model()
            else:
                component.model = component.get_trainable_model(c_args.lang,c_args.nlp_ref,c_args.bucket)
            # TOOD handle HDDl oad here??


        # 3. Set Input/Output Col Names (Only afterwards possible) and only for loaded_from_pretrained_pipe because these are the only cols we may not overwrite
        if c_args.loaded_from_pretrained_pipe:
            NotImplementedError("TODO")

        if c_args.is_licensed: # If Nlu ref was licensed, update license relevant fields
            component.license
            # TODO different in OCR???
            component.provider = ComponentBackend.hc,
            component.license = Licenses.hc,
        # THESE ATTRIBUTES ARE SET BY FACTORY! TODO

        component.language = c_args.lang,
        component.nlu_ref = c_args.nlu_ref,
        component.nlp_ref = c_args.nlp_ref,
        component.in_types = component.node.ins,
        component.out_types = component.node.outs,
        component.in_types_default = component.node.ins,
        component.out_types_default =  component.node.outs,

        # 4. Do the extra shit in  __set_missing_model_attributes__() from SparkNLUComponent ?
        component = NluComponentFactory.__set_missing_model_attributes__(component)
        if component.has_storage_ref : component.storage_ref = component.model.getStorageRef()
        # component.paramMap = None, # Can get away without for now
        # component.paramSetterMap = None, # Can get away without for now
        # component.paramGetterMap = None, # Can get away without for now

        # TODO, resolve right away? Maybe as optional parameter, because we still want to support users  giving custom emebeds
        component.storage_ref_nlu_ref_resolution = None,

        # TODO only for pipelien!! AFTER construction of the entire thing!!!
        # return ComponentUtils.set_storage_ref_attribute_of_embedding_converters(PipeUtils.set_column_values_on_components_from_pretrained_pipe(constructed_components, nlp_ref, language,path))

    def __set_missing_pipe_attributes__(components: List[NluComponent], c_args:ComponentConstructorArgs, path=None):
        """
        Set missing attributes on pipeline loaded from pretrained SparkNLP Stack or Disk Stored Pipe
        :param c_args:
        :param path:
        :return:
        """
        from nlu.pipe.utils.component_utils import ComponentUtils
        from nlu.pipe.utils.pipe_utils import PipeUtils
        return ComponentUtils.set_storage_ref_attribute_of_embedding_converters(
            PipeUtils.set_column_values_on_components_from_pretrained_pipe(
                components, c_args.nlp_ref, c_args.lang,path))

    def __set_missing_model_attributes__(component:NluComponent)->NluComponent:
        '''
        For a given Spark NLP model this model will extract the poarameter map and search for input/output/label columns and set them on the model.
        This is a workaround to undefined behaviour when getting input/output/label columns
        :param : The model for which the attributes should be set
        :return: model with attributes properly set
        '''
        # TODO for Pipeline Models we should be also RE-SET spark_input/output cols!! I.e. read from disc..
        # For nlu generated models it does not matter because it can change col names at wil
        model = NluComponent.model
        for k in model.extractParamMap():
            if "inputCol" in str(k):
                if isinstance(model.extractParamMap()[k], str):
                    if model.extractParamMap()[k] == 'embeddings':  # swap name so we have uniform col names
                        model.setInputCols('word_embeddings')
                    component.spark_input_column_names = [model.extractParamMap()[k]]
                else:
                    if 'embeddings' in model.model.extractParamMap()[k]:  # swap name so we have uniform col names
                        new_cols = model.model.extractParamMap()[k]
                        new_cols.remove("embeddings")
                        new_cols.append("word_embeddings")
                        model.setInputCols(new_cols)
                    component.spark_input_column_names = model.extractParamMap()[k]

            if "outputCol" in str(k):
                if isinstance(model.model.extractParamMap()[k], str):
                    if model.model.extractParamMap()[k] == 'embeddings':  # swap name so we have uniform col names
                        model.model.setOutputCol('word_embeddings')
                    component.spark_output_column_names = [model.extractParamMap()[k]]
                else:
                    if 'embeddings' in model.extractParamMap()[k]:  # swap name so we have uniform col names
                        new_cols = model.extractParamMap()[k]
                        new_cols.remove("embeddings")
                        new_cols.append("word_embeddings")
                        model.model.setOutputCol(new_cols)
                    component.spark_output_column_names = model.extractParamMap()[k]


            # if "labelCol" in str(k):
            #     if isinstance(self.model.extractParamMap()[k], str) :
            #         self.component_info['spark_label_column_names'] =  [self.model.extractParamMap()[k]]
            #     else :
            #         self.component_info['spark_label_column_names'] =  self.model.extractParamMap()[k]
            return component




anno2compInfo:Dict[JslAnnoRef, NluComponent] = {} # Todo
@dataclass
class NLP_COMPONENT_OLD():
    from nlu import ClassifierDl
    # Encapsulate all components
    A = NLP_NODES
    T = NLP_ANNO_TYPES
    F = NLP_FEATURES
    L = NLP_LEVELS
    ACR = AnnoClassRef
    # Map each Component to its component info
    c = {
        # A.BIG_TEXT_MATCHER : ComponentInfo(),
        A.CHUNK2DOC : '',
        A.CHUNK_EMBEDDINGS : '',
        A.CHUNK_TOKENIZER : '',
        A.CHUNKER : '',
        A.CLASSIFIER_DL : NluComponent(
            name = A.CLASSIFIER_DL,
            type = T.DOCUMENT_CLASSIFIER,
            get_default_model = ClassifierDl.get_default_model,
            get_pretrained_model = ClassifierDl.get_pretrained_model,
            get_trainable_model = ClassifierDl.get_trainable_model,
            pdf_extractor_methods = {'default': default_classifier_dl_config,'default_full': default_full_config,},
            pdf_col_name_substitutor = substitute_classifier_dl_cols,
            output_level = L.INPUT_DEPENDENT_DOCUMENT_CLASSIFIER,
            node = NLP_FEATURE_NODES.CLASSIFIER_DL,
            description = 'todo',
            provider = ComponentBackend.open_source,
            license = Licenses.open_source,
            computation_context = ComputeContexts.spark,
            output_context = ComputeContexts.spark,
            trainable = False,
            jsl_anno_class = A.CLASSIFIER_DL,
            jsl_anno_py_class = ACR.JSL_anno2_py_class[A.CLASSIFIER_DL],
            jsl_anno_java_class =ACR.JSL_anno_ref_2_java_class[A.CLASSIFIER_DL],
            spark_input_column_names = None,
            spark_output_column_names = None,
            has_storage_ref= False,
            storage_ref_consumer= False,
            storage_ref_producer= False,

        ),
        A.CONTEXT_SPELL_CHECKER : '',
        A.DATE_MATCHER : '',
        A.UNTYPED_DEPENDENCY_PARSER : '',
        A.TYPED_DEPENDENCY_PARSER : '',
        A.DOC2CHUNK : '',
        A.DOCUMENT_ASSEMBLER : '',
        A.DOCUMENT_NORMALIZER : '',
        A.EMBEDDINGS_FINISHER : '',
        A.ENTITY_RULER : '',
        A.FINISHER : '',
        A.GRAPH_EXTRACTION : '',
        A.GRAPH_FINISHER : '',
        A.LANGUAGE_DETECTOR_DL : '',
        A.LEMMATIZER : '',
        A.MULTI_CLASSIFIER_DL : '',
        A.MULTI_DATE_MATCHER : '',
        A.N_GRAMM_GENERATOR : '',
        A.NER_CONVERTER : '',
        A.NER_CRF : '',
        A.NER_DL : '',
        A.NER_OVERWRITER : '',
        A.NORMALIZER : '',
        A.NORVIG_SPELL_CHECKER : '',
        A.POS : '',
        A.RECURISVE_TOKENIZER : '',
        A.REGEX_MATCHER : '',
        A.REGEX_TOKENIZER : '',
        A.SENTENCE_DETECTOR : '',
        A.SENTENCE_DETECTOR_DL : '',
        A.SENTENCE_EMBEDDINGS : '',
        A.STEMMER : '',
        A.STOP_WORDS_CLEANER : '',
        A.SYMMETRIC_DELETE_SPELLCHECKER : '',
        A.TEXT_MATCHER : '',
        A.TOKEN2CHUNK : '',
        A.TOKEN_ASSEMBLER : '',
        A.TOKENIZER : '',
        A.SENTIMENT_DL : '',
        A.SENTIMENT_DETECTOR : '',
        A.VIVEKN_SENTIMENT : '',
        A.WORD_EMBEDDINGS : '',
        A.WORD_SEGMENTER : '',
        A.YAKE_KEYWORD_EXTRACTION : '', }







## Pipe Generation
def get_iterable_NLP_nodes()->List[NLP_FEATURE_NODES]:
    """Get an iterable list of every NLP Feature Node"""
    pass
def get_iterable_NLP_HC_nodes()->List[NLP_FEATURE_NODES]:
    """Get an iterable list of every NLP Feature Node"""
    pass
def get_iterable_feature_nodes(universe:List[Union[JslUniverse, List[JslUniverse]]])->List[Union[NlpFeatureNode, NlpHcFeatureNode, OcrFeatureNode]]:
    """Get an iterable list of every NLP Feature Node in a universe.
    If List of Universes is provided, it will merge all the universes into one large,
    i.e. merging them all into a large list

    """
    if isinstance(universe,List):
        pass
    elif isinstance() : pass

    # TODO filter nodes by applicable license
    nodes = NLP_FEATURE_NODES.get_iterable_values().get_iterable_values() \
            +NLP_HC_FEATURE_NODES.get_iterable_values() \
            +OCR_FEATURE_NODES.get_iterable_values()
    return nodes

# TODO work NLU-EXPERT FILE into Pipe-Generation Logic!


def pre_graph_completion_connector(pipe_to_fix:List[NluComponent]):
    """
    If multiple nlu_references are loaded in one call, nlu will try to connect the components in an orderd fashion.
    ONLY for components originating from non-pipe stacks?
    from left to right while respecting the `Logical Pipeline Operators` below:

    NLU pipeline composition Operators
    Whitespace-Operator, i.e. " " --> N-Hop Join
        nlu.load('glove classifier_dl')

    Arrow-Operator, i.e. "->" --> HARD-Join
    nlu.load('lemma->spell->T5  lemma->stem-> ')

    Pipeline Concatination, i.e. pipe1 + pipe1
    p1 = nlu.load('sentiment')
    p2 = nlu.load('emotion')
    p3 = p1+p2


    We could look N hops back, depending on annotator
    :return:
    """
    if len(pipe_to_fix) <= 1 : return pipe_to_fix
    new_pipe = []
    while pipe_to_fix:
        c1 = pipe_to_fix.pop(0)
        c2 = pipe_to_fix.pop(0)

        find_connection_candidates(c1,c2,2)


    pass

def find_connection_candidates(start:NluComponent, target:NluComponent, hops:int)->List[List[NluComponent]]:
    """Try to connect 2 JSl-Nodes Nodes by adding N-Hops many bridge JSL-Nodes between them
    Since there could be multiple options to arrive at the destionation, multiple paths are returned
    """

    pass

def find_connection_candidates(start:Union[NluComponent,ExternalFeature], between:NluComponent, target:NluComponent, hops:int)->List[List[NluComponent]]:
    """

    target_node = 'sentiment'
    p = nlu.load(target_node)

    start_node = 'Hello abstract world!'
    p.predict(start_node)

    On a high level,
    NLU finds a path between the external input_node defined by predict
    and the internal target_node defined by the the nlu_reference.

    Nodes between start and target are represented by Annotators.
    nlu.load('node1 node2 finalNode').predict('start') can be called with multiple refs, which will
    constrain the path from target to finalNode, to go over node1 and afterwards to node2, with as
    little as possible BRIDGES between them!

    If nlu.load(nlu_spell) is called with multiple spells,



    # Node connectivity

    ## Bridges
    If a Node generates at least ONE feature consumed by another node,
    they may be viewed as a bridge that makes travel from one node to the other possible.

    ## N-Hop Connectivity
    2 Nodes may not be connected directly via output and input features.
    For this scenario, N-Hops are defined, which enables multiple bridges to form a larger bridge


    """
    nodes = get_iterable_feature_nodes()
    # TODO external node is TARGEt and internal is SOURCE/START!!Makes more sense because thats how we build the graph
    paths = []
    candidates = [[start]] # TODO external Feature should be a Node? Just has a outs field
     # TODO define missing_input_types() for pipe generation
    while candidates:
        current_path = candidates.pop()
        current_node = current_path[-1]
        if target in current_path[-1] : paths.append(current_path)

        node2explore:FeatureNode
        """
        TODO Double backtrack, this is like finding the shortest path on a graph, but sometimes we have to take
        MULTPLE edges at the same time, where choice in feature producers gives different result
        
        i.e. classifierDL has ins Sentence, Document, Token
        Sentence can resolve to SentenceDetectorDL, SentenceDetector
        Document can to document
        Token can to Tokenizer, RegexTokenizer, MatchTokenzer
        
        CITY SCHNITZELJAG/ SCAVENGER HUNT
        
        We are starting in city S and want to visit city T. 
        We are a working tavler and only may travelling via working.
        
        
        Before we can leave a City C, we must peform a list of tasks K[C] in the city.
        There are O[K_i] options to perform a particular task K_i for a city.
        We must fulfill each todo by choosing one of the options for performing it.
        
        Each of these tasks brings us to a new City, with new tasks todo.
        This is how we live our schnitzel live, peforming todos in one city to the next, until we arrive at Target city.
        
        Once we are at target city, we still have to make sure to finish all open TODOs in visited cities.
        
        We are also a Smart Schnitzel fanatic, so we want to plan ahead and want to map out 
        every unique path in live, that cold bring us to the target city.
        
        
        Thats NLU, chasing the magical spells, starting from text and ending at magic ;)
        
        
        
        
        Problem Can be viewed like planning a RoadTrip where we start in one City and  want to end in a particular target city. 
        Additionally, there are  N cities to visits inbetween, and in each City, there are C[N] Things todo.
        For each thing C[N] todo, there are K[C[N]] Options .
        
        We need to visit every city and for every item on the TODO list, we must do the thing,
        by peforming one to the corrosponding TODO's valid options. 
        I.e. each todo can be fulfilled various ways.

        Also, in each city B, thats not in C[N] but which we are visiting we must fulfill a specific todo list

        
        This is a complete abstraction of the graph problem.
        We are looking to generate every possible combination of Paths that  
        
        
        """
        for input_feature in current_node.in_types:
            # For each feature loop over each node and see if they can connect to a birdge
            SAT_feature_producers = [] # partial solution matches for Path, but complete solution for bridge
            for node2explore in nodes :
                if node2explore in current_path : continue

                if input_feature in node2explore.outs:
                    #partial candidate Match!
                    candidates.append(current_path + [node2explore])





def complete_graph(start:NluComponent):
    print("Completing graph", start)


    required_features = [start.in_types]
    while required_features:
        # 1. Check what is missing in pipe
        get_missing_features()

        # 2. Resolve missing Features

        # 3. Update Stuff

        # 4. Extra Pipe Logic, I.e add missing stuff

        # TODO 1 hop connection logic
        # load('glove classifier_dl')
        # Need to connect 2 nodes with intermediate nodes
        # --> If



def test_graph_completion():

    args = ComponentConstructorArgs('sentiment_dl_twitter', 'en.sentiment',
                                    NLP_NODES.CLASSIFIER_DL,
                                    'en',
                                    get_default_model=True
                                    )

    c = NluComponentFactory(args)
    complete_graph(c)

"""SMall problems with NLP Expert AUto ML:
1. We do not store Learning Rate, Batch Size, etc.. Learning parameters..
    1.1 We can run some benchmarks to find them or manually aggregate them
2. 
     
"""

#
# #Class Utils
# def extract_all_attributes_with_type_from_obj(obj:Any,attr_type:Any)->List[str]:
#     """Extracts a list of attribues which have a specific type"""
#     itrbl = []
#     for v in dir(obj):
#         if isinstance(getattr(obj,v),attr_type ):
#             itrbl.append(eval(f'{obj}.{v}'))
#     return itrbl
#
#
# def get_iterable(obj:Any,attr_type:Any)->List[str]:
#     """Extracts a list of attribues which have a specific type"""
#     extract_all_attributes_with_type_from_obj
#
#     return itrbl


#
# @dataclass
# class NLP_TRAINABLE_PROBLEM:
#     NLP_ANNO.TRAINABLE_VIVEKN_SENTIMENT = ViveknSentimentApproach
#     = SentimentDLApproach
#     = ClassifierDLApproach
#     = MultiClassifierDLApproach
#     = NerDLApproach
#     = PerceptronApproach


"""Pseudo Resolution

1. Map NLU ref to NLP ref and Build NLP component c 
2. check inputs of c. For each input, resolve to the default dependency, with respect to storage ref and language (Recursve on 2)
3. Done?




"""

"""
OC API
Allow Only file Paths or also Pd Dataframes with binary img data or img matrices?

Potential references
2 Options : 
NOT AUTO INSTALL 
# Should NLU automatically check if iput is a Path, IF ocr component are loaded? or should it be extra path param?
# Load all images in folder ocr_fun. If pdf2text is loaded, grabs only .pdf files.  By default searches folder recursively. Optinally can also pass regex ?



nlu.load('pdf2text').predict('~/images/ocr_fun/`)




nlu.load('pdf2text').predict('~/images/ocr_fun/`, recurisve=False) # No nested search
nlu.load('pdf2text').predict('~/images/ocr_fun/myfile.pdf`, recurisve=False) # No nested search
nlu.load('pdf2text').predict(['~/images/ocr_fun/myfile.pdf`,'~/images/ocr_fun/myfile2.pdf`], recurisve=False) # No nested search

df = pd.DataFrame({'img_path': ['~/images/ocr_fun/myfile.pdf`,'~/images/ocr_fun/myfile2.pdf`.]})

nlu.load('doc2text').predict(df)
nlu.load('img2text')


"""


# NLP EXPERT NOTES BELOW!!
## TODO DATASET MODEL PARAMETERS
# Model References should point to NLU alias references/defaults. This way, if underyling models get updated and there are new reccomended models, we just update the NLU reference and it effect all configs in the expert
#
# nlu.set_optimize_goal('fast')
# nlu.set_optimize_goal('accurate')
# # for each alias .fast and .accurate options. i.e. ner.fast or ner.accurate or ner.balanced
# # --> just use benchmarks
# # Transfer Learning on Medical NER and resolver possible
# # Train/test/val , if lang not coverd, use multi-lang
# # Lang classifier no embeds, low mem!
# # WordCoverage for Embeddings to pick best embeddings. Look at OOV metadata to know if coverd
# # model identifier maps to configs
# # Only save the classifier Model OOOR save the entire Pipe
# # Create Extra Metadata to create entire pipe from scratch. Load data from cache pretrained
# # Add flag for ONLINE/OFFLINE (and add docs about cache pretrained)`
# # Add Configure memory and cores
# nlu.load('train.sentiment', optimze_for='balanced', memory={}).predict(df)  # DEFAULT <----
# nlu.load('train.sentiment', optimze_for='speed').predict(df)
# nlu.load('train.sentiment', optimze_for='accuracy').predict(df)
# pipe = nlu.load('train.sentiment')  # auto lang and domain classify
# pipe.predict(df)
#
# pipe.save('my/model')
# pipe = nlu.load('my/model')
# df = nlu.load('my/model').predict
#
# nlu.load("remove_background remove_noise pdf2text lemma xx.robterta train.classifier")
# # LANG - > DOMAIN -> Problem ->
# # ---> Start making list of all NLP domains we cover
# # LR/Batchhsizes not on fited model stored
# nlp_expert = {
#     'en':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'fast': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing_pipe': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS],
#                             # ideally we define the input/outputs here, so there are no ambigous cases, but can be optional because tedious
#                             'preprocess_input_mapping': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                          NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'accurate': {{}},  # ...
#                     'balanced': {{}},  # ...
#
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'fast': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'accurate': {{}},  # ...
#                     'balanced': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                             'input_level': 'document',  # Or sentence
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'sentence_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                             'input_level': 'token',
#                         },
#                         'preprocessing': {
#
#                             'tokenize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings'],
#                             'input_mappings':
#                                 {
#                                     'tokens': 'spellcheck',
#                                     'spellcheck': 'lemmatize',
#                                     'lemmatize': 'word_embeddings',
#                                     'word_embeddings': 'ner_dl',
#
#                                 }
#
#                                 ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#     'fr':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#     'de':
#         {
#             'healthcare': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                                 # TODO for each annotator a param object/class?
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.LEMMATIZER: {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             NLP_ANNO.ELMO_EMBEDDINGS: {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#                             'preprocess_order': [NLP_ANNO.CONTEXT_SPELL_CHECKER, NLP_ANNO.LEMMATIZER,
#                                                  NLP_ANNO.ELMO_EMBEDDINGS]
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'oncology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'radiology': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'twitter': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'reddit': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#             'marketing': {
#                 NLP_ANNO.CLASSIFIER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.NER_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTIMENT_DL: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.SENTENCE_DETECTOR: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.POS: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#                 NLP_ANNO.CONTEXT_SPELL_CHECKER: {
#                     'small': {
#                         'model_parameters': {
#                             'lr': 0.03,
#                             'batch': 13,
#                         },
#                         'preprocessing': {
#                             'spellcheck': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'lemmatize': {
#                                 'use': True,
#                                 'configs': {},  # only defined when use is true
#                             },
#                             'word_embeddings': {
#                                 'use': True,
#                                 'configs': {  # only defined when use is true
#                                     'nlu_reference': 'en.bert'
#
#                                 }
#
#                             },
#
#                             'preprocess_order': ['spellcheck', 'lemmatize', 'word_embeddings']
#                         },
#                     },
#                     'medium': {{}},  # ...
#                     'large': {{}},  # ...
#                 },
#             },
#         },
#
# }
