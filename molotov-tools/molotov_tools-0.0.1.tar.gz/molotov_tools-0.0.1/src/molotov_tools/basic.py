import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def CatmullRomSpline(P0, P1, P2, P3, nPoints=100):
    """
    P0, P1, P2, and P3 should be (x,y) point pairs that define the
    Catmull-Rom spline.
    nPoints is the number of points to include in this curve segment.
    """
    # Convert the points to numpy so that we can do array multiplication
    P0, P1, P2, P3 = map(np.array, [P0, P1, P2, P3])

    # Calculate t0 to t4
    alpha = 0.5
    def tj(ti, Pi, Pj):
        xi, yi = Pi
        xj, yj = Pj
        return ( ( (xj-xi)**2 + (yj-yi)**2 )**0.5 )**alpha + ti

    t0 = 0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    # Only calculate points between P1 and P2
    t = np.linspace(t1,t2,nPoints)

    # Reshape so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    t = t.reshape(len(t),1)

    A1 = (t1-t)/(t1-t0)*P0 + (t-t0)/(t1-t0)*P1
    A2 = (t2-t)/(t2-t1)*P1 + (t-t1)/(t2-t1)*P2
    A3 = (t3-t)/(t3-t2)*P2 + (t-t2)/(t3-t2)*P3

    B1 = (t2-t)/(t2-t0)*A1 + (t-t0)/(t2-t0)*A2
    B2 = (t3-t)/(t3-t1)*A2 + (t-t1)/(t3-t1)*A3

    C  = (t2-t)/(t2-t1)*B1 + (t-t1)/(t2-t1)*B2
    return C

def disp_excel(P):
    """
    Calculate Catmull Rom for a chain of points and return the combined curve.
    """

    '''
    ROTINA PARA PLOTAR DISPERSÃO IGUAL O EXCEL

    Entrada é uma matriz M, onde os pontos estão ordenados em pares por linha M = [ [x0,y0] , [x1,y1] ]
    
    A saída são duas tuplas (imutáveis) com os novos valores de x e y do tipo:
    
    pts_x , pts_y = disp_excel(M)
    
    Minimo de 4 pontos são necessários
    '''


    #necessidade de adicionar um ponto extra no inicio e no fim de modo que a interpolação pegue todos os pontos
    #verificar se x é crescente ou decrescente
    def add_pi(P):


        x0i, x1i = P[0, 0], P[1, 0]
        y0i, y1i = P[0, 1], P[1, 1]
        xi = x0i + (x0i - x1i) * .001
        if x0i - x1i == 0:

            # pegar y com base na posicao
            if y1i < y0i:

                yi = y0i + 0.001 * y0i
            else:
                yi = y0i - 0.001 * y0i
        else:
            f_inicio = interp1d(P[:3, 0], P[:3, 1], fill_value="extrapolate")
            yi = f_inicio(xi)
        M = np.concatenate((np.array([[xi, yi]]), P), axis=0)
        return M

    def add_pf (P):

        x0f, x1f = P[-2, 0], P[-1, 0]
        y0f, y1f = P[-2, 1], P[-1, 1]
        xf = x1f - (x0f - x1f) * .001
        if x0f - x1f == 0:

            #pegar y com base na posicao
            if y1f<y0f:

                yf=y1f - 0.001*y1f
            else:
                yf = y1f + 0.001 * y1f
        else:
            f_fim = interp1d(P[-3:, 0], P[-3:, 1], fill_value="extrapolate")
            yf = f_fim(xf)
        M = np.concatenate((P,np.array([[xf, yf]])), axis=0)
        return M

    P = add_pi(P)
    P = add_pf(P)

    sz = len(P)

    # The curve C will contain an array of (x,y) points.
    C = []
    for i in range(sz-3):
        c = CatmullRomSpline(P[i], P[i+1], P[i+2], P[i+3])
        C.extend(c)
    return zip(*C)


def get_dados(dataframe, n_col_per_data=2, pos_col_x=0, pos_col_y=1, pular_linha=1):

    '''
    FUNÇÃO DE LEITURA DOS DADOS EM CSV (tem como deixar mais genérico)

    O csv que recebi do site de gerar dados forece pares de dados x,y, então há a necessidade de agrupar x e y para cada 2 pares de dados do csv, a primeira linha possui o nome das sequencias de dados, a segunda linha possui o nome do eixo e a partir da terceira linha os dados são fornecidos

    retorna um dicionario que contem o nome do conjunto de pontos, outro dicionario para os pontos x e y do modo que:

    dados = get_dados(dataframe)

    dados["Alpha 0"]["x"] = Lista com os pontos 'x' de Alpha 0

    dados["Alpha 0"]["y"] = Lista com os pontos 'y' de Alpha 0

    dados["Alpha 2"]["x"] = Lista com os pontos 'x' de Alpha 2

    dados["Alpha 2"]["y"] = Lista com os pontos 'y' de Alpha 2

    Parameters
    ----------
    dataframe
    n_col_per_data
    pos_col_x
    pos_col_y
    pular_linha
    Returns
    -------

    '''

    saida = {}
    nome_colunas = dataframe.columns[::n_col_per_data]
    for i in range(len(nome_colunas)):
        x_nao_tratado = dataframe.iloc[pular_linha:, n_col_per_data * i + pos_col_x].to_numpy()
        y_nao_tratado = dataframe.iloc[pular_linha:, n_col_per_data * i + pos_col_y].to_numpy()
        x = [float(i) for i in x_nao_tratado if not (pd.isnull(i))]
        y = [float(i) for i in y_nao_tratado if not (pd.isnull(i))]
        saida[f"{nome_colunas[i]}"] = {"x": np.array(x), "y": np.array(y)}

    return saida


def loop_plots(axis, dicionario, inverte_y=False, inverte_eixos=False, scatter=True, label=True, linestyle="-",
               exp_data=False):

    '''
    FUNCAO PARA PLOT SEQUENCIAL DOS DADOS EM UM DICIONARIO DO TIPO GET_DADOS

    recebe um eixo de subplot, um dicionário de dados e um parametro de inversão dos eixos
    Parameters

    ----------
    axis
    dicionario -> {f"N Crit = {n}":{"x":N["alpha"],"y":N["CL"]}}
    inverte_y
    inverte_eixos
    scatter
    label
    linestyle
    exp_data

    Returns
    -------

    '''

    for nome, valores in dicionario.items():

        if inverte_eixos:
            vx = valores["y"]
            vy = valores["x"]
        else:
            vx = valores["x"]
            vy = valores["y"]

        matriz_par_a_par = np.array([vx, vy]).T
        x_limpo, y_limpo = disp_excel(matriz_par_a_par)

        # inversao do eixo y
        if inverte_y:
            y_plot_limpo = np.array(y_limpo) * -1
            y_plot_dots = vy * -1
        else:
            y_plot_limpo = np.array(y_limpo)
            y_plot_dots = vy

        if exp_data:
            if scatter:
                axis.plot(x_limpo, y_plot_limpo, label=f"{label}", linestyle=linestyle)
                cor = axis.get_lines()[-1].get_color()
                axis.scatter(vx, y_plot_dots, color=cor)
            else:
                axis.plot(x_limpo, y_plot_limpo, label=f"{label}", linestyle=linestyle)
        else:
            if label:
                if scatter:
                    axis.plot(x_limpo, y_plot_limpo, linestyle=linestyle)
                    cor = axis.get_lines()[-1].get_color()
                    axis.scatter(vx, y_plot_dots, color=cor, label=f"{nome}")
                else:
                    axis.plot(x_limpo, y_plot_limpo, label=f"{nome}", linestyle=linestyle)
                    cor = axis.get_lines()[-1].get_color()
            else:
                if scatter:
                    axis.scatter(vx, y_plot_dots, color=cor)

                axis.plot(x_limpo, y_plot_limpo, linestyle=linestyle)



'''
cd_cl_df = pd.read_csv(caminho + "csv/cd x cl.csv")

cl_alpha_df = pd.read_csv(caminho + "csv/cl.csv")

clmax_df = pd.read_csv(caminho + "csv/clmax.csv")

cp_df = pd.read_csv(caminho + "csv/cp.csv")

wb_erro = xl.load_workbook(caminho + "excel/Erro relativo dos paineis NACA0012.xlsx",data_only=True)


#coleta dos dados csv
cp = get_dados(cp_df)
cd_cl = get_dados(cd_cl_df)
cl_alpha = get_dados(cl_alpha_df)
clmax = get_dados(clmax_df)

#ler dados do excel
dados_erro = wb_erro["Planilha1"]["B2:F14"]

dados_erro = range_to_data(dados_erro)
'''