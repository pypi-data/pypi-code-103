""" Modulo Para alguin especial """

class Saludo():
    def __init__(self, nombre):
        self.hello = nombre
        
    def welcome(self):
        print("Hola {}, Bienvenida a esta historia\nLa mejor historia de todas".format(self.hello))


class TQM():

    def __init__(self):
        pass

    def quieres_ser_mi_novia(self):
        print("¿ Quieres ser mi novia ?")
        respuesta = input("SI | NO : ")

        while respuesta.upper() != "SI" and respuesta.upper() != "NO":
            print("Esa no es una respuesta valida, Vuelve a intentarlo.")
            print("¿ Quieres ser mi novia ?")
            respuesta = input("SI | NO : ")

        if respuesta.upper() == "SI":
            print("--------------------\nWelcome to my live\n--------------------\nEres la mejor = )")
        else:
            print("\n-------------------------------------------------\nNo te voy a presionar, quiero que sea libre\n\nAMAR ES LIBERAR")
