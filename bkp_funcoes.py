def pega_nome_atletas():
    # Selecionando os dados dos corredores
    s = 1
    n = 26
    num_pag = verifica_num_pag()
    nomes_atletas = []

    if num_pag == 1:
        num_pag = num_pag+1
        for i in range(1, num_pag):
            print(i)    
            # Entrando nos resultados de cada corredor
            for j in range(s,n):
                print(i,j)
                try: # Verificando em qual aba está - 1 a 5 - caso não esteja na aba certa, clica-se na aba correta
                    driver.find_element(
                        by=By.XPATH,
                        value=f'//*[@id="results"]/nav/ul/li[{i+1}]/a',
                        ).click()
                    sleep(1)
                    if i == 1 and j == 1:
                        nome = driver.find_element(
                                            by=By.XPATH,
                                            value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/strong/a',
                                        ).text
                        #print(nome)
                        nomes_atletas.append(nome)
                        sleep(1)
                        
                    else:
                        nome = driver.find_element(
                                            by=By.XPATH,
                                            value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/a',
                                        ).text
                        #print(nome)
                        nomes_atletas.append(nome)
                        sleep(1)
                
                except Exception: # Caso ja esteja na aba correta, vai direto pro atleta
                    try:
                        if i == 1 and j == 1:
                            nome = driver.find_element(
                                                by=By.XPATH,
                                                value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/strong/a',
                                            ).text
                            #print(nome)
                            nomes_atletas.append(nome)
                            sleep(1)
                        
                        else:
                            nome = driver.find_element(
                                                by=By.XPATH,
                                                value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/a',
                                            ).text
                            #print(nome)
                            nomes_atletas.append(nome)
                            sleep(1)
                            
                    except Exception:
                        print('except')
                        break
    else:
        num_pag = num_pag-1
        for i in range(1, num_pag):
            print(i)    
            # Entrando nos resultados de cada corredor
            for j in range(s,n):
                print(i,j)
                try: # Verificando em qual aba está - 1 a 5 - caso não esteja na aba certa, clica-se na aba correta
                    driver.find_element(
                        by=By.XPATH,
                        value=f'//*[@id="results"]/nav/ul/li[{i+1}]/a',
                        ).click()
                    sleep(1)
                    if i == 1 and j == 1:
                        nome = driver.find_element(
                                            by=By.XPATH,
                                            value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/strong/a',
                                        ).text
                        #print(nome)
                        nomes_atletas.append(nome)
                        sleep(1)
                        
                    else:
                        nome = driver.find_element(
                                            by=By.XPATH,
                                            value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/a',
                                        ).text
                        #print(nome)
                        nomes_atletas.append(nome)
                        sleep(1)
                
                except Exception: # Caso ja esteja na aba correta, vai direto pro atleta
                    try:
                        if i == 1 and j == 1:
                            nome = driver.find_element(
                                                by=By.XPATH,
                                                value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/strong/a',
                                            ).text
                            #print(nome)
                            nomes_atletas.append(nome)
                            sleep(1)
                        
                        else:
                            nome = driver.find_element(
                                                by=By.XPATH,
                                                value=f'//*[@id="results"]/table/tbody/tr[{j}]/td[2]/a',
                                            ).text
                            #print(nome)
                            nomes_atletas.append(nome)
                            sleep(1)
                            
                    except Exception:
                        print('except')
                        break

    return nomes_atletas



### Aqui quando passa pra aba 2 ele busca o primeiro nome em negrito, pq o j é 1 e como ele nao acha ele pula



