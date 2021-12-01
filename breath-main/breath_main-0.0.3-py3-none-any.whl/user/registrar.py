import streamlit as st
import hashlib as hl

from user.oauth import google_oauth_login

class Registrar:
	def __init__(self):
		
		# Título
		st.title("Cadastro Inicial")
		st.text("Faça seu cadastro ou realize login com o Google.")

		# Campos de preenchimento
		st.text_input("Nome", key="name_typed")
		st.text_input("Email", key="email_typed")
		st.text_input("Senha", type="password", key="senha_typed")
		#print(st.session_state.name, st.session_state.email, st.session_state.senha)
		#print(st.session_state.senha_typed[0], st.session_state.senha_typed[1], st.session_state.senha_typed)

		# Botões
		left_column, right_column = st.columns(2)
		left_column.button("Login com Google", key="button_google_login")
		right_column.button("Registrar", key="button_registrar")

		# Interação com botão de registrar
		if st.session_state.button_registrar == True:
			st.session_state.name = st.session_state.name_typed
			st.session_state.email = st.session_state.email_typed
			st.session_state.senha = self.crypto(st.session_state.senha_typed)
			st.session_state.google_login = False
			st.session_state.logado = True

		# Interação com botão de login com google
		if st.session_state.button_google_login:
			google_oauth_login()

	def crypto(self, password):
		return hl.sha512(str.encode(password)).hexdigest()

		

if __name__ == "__main__":
	Registrar()