def login(usernameArray, passwordArray, inputUsername, Inputpassword):
  if usernameArray.includes(inputUsername):
    uan = usernameArray.index(inputUsername)
    if passwordArray.includes(Inputpassword):
      pan = passwordArray.index(Inputpassword)
      if pan == uan: 
        return True
    else: return False
  else: return False