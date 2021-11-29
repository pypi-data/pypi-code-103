import json
import re

LISP_COMMON_CONFIG = [ "/lisp/global_configs/common.json", "/opt/siem/global_configs/common.json" ]

__all__ = [ 'Configuration', 'ConfigurationFileError' ]

class ConfigurationFileError(Exception):
    """
    Eccezione sollevata nel caso che ci siano problemi con il file contenente la configurazione
    Il problema viene segnalato nel testo dell'eccezione
    """
    pass


class Configuration:
    """
    Classe per il caricamento di una configurazione da file JSON
    Nel caso non venga specificato su quale configurazione operare, viene considerata quella di default
    """
    __config_file_path = None                           # path della configurazione (per sviluppi futuri)
    __config_content = None                             # contenuto della configurazione
    __key_pattern = r'^([a-z0-9_]+\.)*[a-z0-9_]+$'      # formato delle chiavi (dot separated strings)
    __valid_values = (str, bool, list, type(None))      # valori dei campi ammessi

    def __init__(self, config_file_path=None):
        """
        Inizializza la classe di configurazione utilizzando il file "config_file_path" se specificato, altrimenti "/lisp/global_configs/common.json"
        :param config_file_path:            path del file contenente la configurazione
        :raises ConfigurationFileError:     quando il file non viene trovato o c'è un errore nel parsing
        """
        user_provided_config_file = True
        if config_file_path is None:
            # nel caso non venga specificato un path si usa quello della configurazione common linkspirit
            config_file_path = LISP_COMMON_CONFIG
            # indico che stiamo usando dei file di default
            user_provided_config_file = False

        if user_provided_config_file:
                try:
                    # provo ad aprire e parsare il file contenente la configurazione
                    with open(config_file_path, 'r') as config_file:
                        content = json.load(config_file)
                    opened_file_path = config_file_path
                except FileNotFoundError:
                    # il file potrebbe non esistere, propago l'eccezione al chiamante
                    raise ConfigurationFileError('Cannot find configuration file "{}". Please check if it exists.'.format(config_file_path))
                except json.JSONDecodeError:
                    # il file potrebbe non essere un json o essere corrotto, propago l'eccezione al chiamante
                    raise ConfigurationFileError('Cannot parse configuration file "{}". For this implementation configuration file must be json and must contains a dictionary.'.format(config_file_path))
        else:
            for path in config_file_path:
                try:
                    # provo ad aprire e parsare il file contenente la configurazione
                    with open(path, 'r') as config_file:
                        content = json.load(config_file)
                    opened_file_path = path
                    break
                except FileNotFoundError:
                   pass
                except json.JSONDecodeError:
                    pass

            else:
                # non siamo riusciti ad aprire nessun file di default
                raise ConfigurationFileError('Cannot find any configuration file of {} or the existing ones where invalid (format must be json and must contains a dictionary).'.format(config_file_path))

        # controllo se il contenuto file specificato e' un dizionario
        if not isinstance(content, dict):
            raise ConfigurationFileError('Configuration file "{}" does not contain a dictionary. For this implementation configuration file must be json and must contains a dictionary.'.format(opened_file_path))

        # il contenuto è un dizionario, allora inizializzo lo stato interno ed esco
        self.__config_file_path = opened_file_path
        self.__config_content = content

    def __is_a_valid_key(self, key):
        """
        Funzione che controlla se una data chiave è del formato corretto (dot separated strings)
        :param key:         chiave da controllare
        :return:            True se il formato è corretto, False altrimenti
        """
        return re.match(self.__key_pattern, key)

    def __is_a_valid_value(self, value):
        """
        Funzione che data un valore determina se questo è valido o meno
        :param value:       valore da controllare
        :return:            True se il valore è valido, False altrimenti
        """
        return isinstance(value, self.__valid_values)

    def exists(self, key):
        """
        Funzione che controlla se una chiave è presente nella struttura dati (valido anche per i path)
        Ritorna True se esiste, False altrimenti
        :param key:         chiave la cui esistenza va verificata
        :return:            True se la chiave esiste, False se la chiave non esiste o se non ha un formato valido
        """
        # controllo che la chiave abbia il formato corretto
        if not self.__is_a_valid_key(key):
            # raise ValueError('Searched key does not respect key standards (dots separated strings).')
            return False

        # ottengo le singole chiavi che lo compongono e ciclo per ottenere le sezioni innestate
        keys_list = str.split(key, '.')
        content = self.__config_content
        for key in keys_list:
            if isinstance(content, dict) and key in content:
                # se la chiave è nel contenuto corrente, imposto come contenuto il suo valore
                content = content.get(key)
            else:
                return False
        # se ho finito le chiavi vuol dire che la chiave iniziale esisteva
        return True

    def get(self, key, default=None):
        """
        Data una chiave (<path>.<entry>) valida, ritorna il valore puntato da quella chiave se esiste, altrimenti default
        La chiave cercata non può essere un path (non può restituire un dizionario)
        :param key:                         percorso del valore che si vuole ottenere
        :param default:                     valore da ritornare nel caso non venga trovata la chiave
        :return:                            valore richiesto se trovato o default, None se la chiave non è valida o è un path
        """
        if not self.__is_a_valid_key(key):
            # raise ValueError('Searched key does not respect key standards (dots separated strings).')
            return None

        # ottengo le singole chiavi che lo compongono e ciclo per ottenere le sezioni innestate
        keys_list = str.split(key, '.')
        content = self.__config_content
        for key in keys_list:
            if isinstance(content, dict) and key in content:
                # se la chiave è nel contenuto corrente, imposto come contenuto il suo valore
                content = content.get(key)
            else:
                # la chiave non è stata trovata oppure si è raggiunto un valore ma ci sono ancora chiavi
                return default

        # se il valore puntato dalla chiave non è tra quelli ammessi, ritorno None
        if not self.__is_a_valid_value(content):
            return None

        return content

    def to_dict(self):
        """
        Funzione che restituisce l'intera configurazione come dizionario
        :return:            dizionario contenente la configurazione
        """
        return dict(self.__config_content)

    def sections(self, key=None):
        """
        Funzione che ritorna una lista delle sezioni presenti nella configurazione o in una parte di essa
        :param key:             opzionale, indica di quale chiave si vogliono ottenere le sezioni
        :throw ValueError:      se la chiave non ha un formato valido
        :return:                lista di sezioni, None se la chiave non esiste o se la chiave punta ad un valore
        """
        # se la chiave è None allora torno le sezioni dell'intera configurazione
        if key is None:
            return list(self.__config_content.keys())

        if not self.__is_a_valid_key(key):
            raise ValueError('Searched key does not respect key standards (dots separated strings).')

        keys_list = str.split(key, '.')
        content = self.__config_content

        for key in keys_list:
            if isinstance(content, dict) and key in content:
                # se la chiave è nel contenuto corrente, imposto come contenuto il suo valore
                content = content.get(key)
            else:
                # la chiave non è stata trovata oppure si è raggiunto un valore ma ci sono ancora chiavi
                return None

        if not isinstance(content, dict):
            # non posso ottenere le sezioni di un valore che non sia dizionario
            return None
        else:
            return list(content.keys())

    @property
    def config_file_path(self):
        """
        Funzione che ritorna il path del file sul quale e' stata costruita la configurazione
        :return:			stringa contenente il path
        """
        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, _):
        """
        Setter della variabile config file path, solleva un'eccezione perche' non e' modificabile
        :throw AttributeError:			l'attributo e' accessibile solo in lettura
        """
        raise AttributeError('"config_file_path" is a readonly attribute')
