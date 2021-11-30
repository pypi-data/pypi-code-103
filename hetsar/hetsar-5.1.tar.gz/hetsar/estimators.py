import numpy as np
from scipy.optimize import minimize
from functools import reduce
import pandas as pd
from .utils import fn_varml_sandwich_Npsi_NKbeta_Nsgmsq, format_output, fn_mg_est, fn_significance_stars, _format_pred

class RegressionResultsWrapper:
    """
    Wrapper class for the regression results of the HSAR model.
    """
    def __init__(self,modelstring,a_x,m_y,m_ys,W,y,ind,exog_labels,v_theta_ini,bnds,optim_output,variance,variance_sand,df_est,df_mg_est,N,T,K,robust):
        self.modelstring = modelstring
        self.a_x = a_x
        self.m_y = m_y
        self.m_ys = m_ys
        self.W = W
        self.exog_labels = exog_labels
        self.v_theta_ini = v_theta_ini
        self.bnds = bnds
        self.optim_output = optim_output
        self.variance = variance
        self.variance_sand = variance_sand
        self.df_est = df_est
        self.y = y
        self.ind = ind
        self.df_mg_est = df_mg_est
        self.N = N
        self.T = T
        self.K = K

        mgDict = {}
        for gr in self.df_mg_est.group.unique():
            mgDict[gr] = {}
            for param in [f'W{self.y}']+ self.exog_labels+['sgmsq']:
                paramDict = {}
                paramDict['est'] = self.df_mg_est.set_index('group').loc[gr][f'{param}_mg']
                paramDict['se'] = self.df_mg_est.set_index('group').loc[gr][f's_{param}_mg']
                paramDict['z'] = self.df_mg_est.set_index('group').loc[gr][f'{param}_mg']/self.df_mg_est.set_index('group').loc[gr][f's_{param}_mg']
                paramDict['lb'] = self.df_mg_est.set_index('group').loc[gr][f'{param}_mg'] - 1.96*self.df_mg_est.set_index('group').loc[gr][f's_{param}_mg']
                paramDict['ub'] = self.df_mg_est.set_index('group').loc[gr][f'{param}_mg'] + 1.96*self.df_mg_est.set_index('group').loc[gr][f's_{param}_mg']
                paramDict['stars'] = fn_significance_stars(self.df_mg_est.set_index('group').loc[gr][f'{param}_mg']/self.df_mg_est.set_index('group').loc[gr][f's_{param}_mg'])
                mgDict[gr][param] = paramDict
        self.mgDict = mgDict

        if robust==True:
            var_str = 'var_sandw_'
        else:
            var_str = 'var_'
        df_params = self.df_est
        for param in [f'W{self.y}']+self.exog_labels+['sgmsq']:
            df_params[f's_{param}'] = np.sqrt(df_params[f'{var_str}{param}'])

        estDict = {}
        for i in self.df_est[ind].unique():
            estDict[i] = {}
            for param in [f'W{self.y}']+ self.exog_labels+['sgmsq']:
                paramDict = {}
                paramDict['est'] = df_params.set_index(ind).loc[i][f'{param}']
                paramDict['se'] = df_params.set_index(ind).loc[i][f's_{param}']
                paramDict['z'] = df_params.set_index(ind).loc[i][f'{param}']/df_params.set_index(ind).loc[i][f's_{param}']
                paramDict['lb'] = df_params.set_index(ind).loc[i][f'{param}'] - 1.96*df_params.set_index(ind).loc[i][f's_{param}']
                paramDict['ub'] = df_params.set_index(ind).loc[i][f'{param}'] + 1.96*df_params.set_index(ind).loc[i][f's_{param}']
                paramDict['stars'] = fn_significance_stars(df_params.set_index(ind).loc[i][f'{param}']/df_params.set_index(ind).loc[i][f's_{param}'])
                estDict[i][param] = paramDict

        self.estDict = estDict


    def summary(self):
        """
        :return summary: (str) Prints Mean Group estimates.
        """
        output = f"""
        SAR model with heterogeneous coefficients \n
        Mean Group estimates, N={self.N}, T={self.T}, number of observations={self.N*self.T} \n
        Dependent variable: {self.y} \n
        """
        print(output)
        data = [['Group','Param','Est','Std. Err','z','95% CI']]
        for gr in self.df_mg_est.group.unique():
            for param in [f'W{self.y}']+ self.exog_labels+['sgmsq']:
                param_list = [f'{gr}',param,
                             f"""{self.mgDict[gr][param]['est']:.5f}{self.mgDict[gr][param]['stars']}""",
                             f"""{self.mgDict[gr][param]['se']:.5f}""",
                             f"""{self.mgDict[gr][param]['z']:.5f}""",
                             f"""{self.mgDict[gr][param]['lb']:.5f}-{self.mgDict[gr][param]['ub']:.5f}"""]
                data = data + [param_list]

        col_windths = [max([len(row[i]) for row in data]) for i in range(len(data[0]))]
        dash = '-' * (sum(col_windths)+ 2*len(col_windths))
        for row in data:
            print ("".join(row[i].ljust(col_windths[i]+2) for i in range(len(row))))
            row_str = "".join(row[i].ljust(col_windths[i]+2) for i in range(len(row)))
            output = f'{output}\n{row_str}'
            if row[0]=='Group':
                print(dash)
                output = f'{output}\n{dash}'

    def summary_all(self):
        """
        :return summary: (str) Prints indivindual estimates.
        """
        output = f"""
        SAR model with heterogeneous coefficients \n
        Unit specific parameter estimates, N={self.N}, T={self.T}, number of observations={self.N*self.T} \n
        Dependent variable: {self.y} \n
        """
        print(output)
        data = [[f'{self.ind}','Param','Est','Std. Err','z','95% CI']]
        for gr in self.df_est[ind].unique():
            for param in [f'W{self.y}']+ self.exog_labels+['sgmsq']:
                param_list = [f'{gr}',param,
                             f"""{self.estDict[gr][param]['est']:.5f}{self.estDict[gr][param]['stars']}""",
                             f"""{self.estDict[gr][param]['se']:.5f}""",
                             f"""{self.estDict[gr][param]['z']:.5f}""",
                             f"""{self.estDict[gr][param]['lb']:.5f}-{self.estDict[gr][param]['ub']:.5f}"""]
                data = data + [param_list]

        col_windths = [max([len(row[i]) for row in data]) for i in range(len(data[0]))]
        dash = '-' * (sum(col_windths)+ 2*len(col_windths))
        for row in data:
            print ("".join(row[i].ljust(col_windths[i]+2) for i in range(len(row))))
            row_str = "".join(row[i].ljust(col_windths[i]+2) for i in range(len(row)))
            output = f'{output}\n{row_str}'
            if row[0]==f'{self.ind}':
                print(dash)
                print(dash)
            if row[1]==self.exog_labels[-1]:
                print(dash)
                output = f'{output}\n{dash}'

    def fitted_values(self, naive = False):
        """
        Returns fitted value and estimated resinduals of the HSAR model.

        :return: (numpy.ndarray, numpy.ndarray) Tuple containing fitted values and estimated resinduals
        """
        v_psi_hat = self.optim_output.x[:self.N].reshape([self.N,1])
        m_beta_hat = self.optim_output.x[self.N:(self.K+1)*self.N].reshape([self.N,self.K],order = 'C')

        a_x2 = np.transpose(self.a_x,(0,2,1))
        m_beta2 = m_beta_hat[:,:,np.newaxis]
        m_beta_x = m_beta2*a_x2
        m_beta_x2 = np.transpose(m_beta_x,(0,2,1))
        m_beta_x_sum = np.sum(m_beta_x2,2)
        if naive==True:
            m_y_hat = v_psi_hat*self.m_ys+m_beta_x_sum
        else:
            m_Psi = v_psi_hat * np.identity(len(v_psi_hat))
            m_A = np.identity(self.N)-m_Psi@self.W

            m_y_hat = np.linalg.inv(m_A)@m_beta_x_sum
        m_eps_hat = self.m_y-m_y_hat

        dfyhat = _format_pred(m_y_hat,'yhat',self.T)
        ehat = _format_pred(m_eps_hat,'ehat',self.T)

        return dfyhat.merge(ehat, on = ['ind','time'])

def _generate_NT_array(df,ind,t,var):
    """
    Takes a pandas.DataFrame and outputs an NxT array of sorted values
    :param df: (pandas.DataFrame)
    :param ind: (str) Variable name of the indentifier
    :param t: (str) Variable name of the time variable
    :param var: (str) Name of the variable to be transformed.
    :return: (numpy.ndarray) NxT array with values of var sorted by ind and t
    """
    N = df[ind].nunique()
    T = df[t].nunique()
    return np.array(df.sort_values([ind,t])[var]).reshape([N,T])

class Hetsar(object):
    """
    Hetsar estimator class
    """

    def __init__(self):
        self.modelstring = 'hetsar'

    def objective_function(self,v_theta0,args):
        """
        Objective function of the Hetsar class.

        :param v_theta0: (numpy.ndarray) parameter of initial values for the optimization algorithm
        :param args: (tuple) contains the arrays (m_y,m_ys,a_x,W)
        :rtype: (numpy.ndarray) Value of the log-likelihood evaluated at the arguments.
        """
        v_theta = v_theta0.reshape(len(v_theta0),1)
        m_y,m_ys,a_x,W = args
        N,T,K = a_x.shape
        v_psi = v_theta[:N,0].reshape(N,1)
        v_beta = v_theta[N:(N+K*N),0].reshape(N*K,1)
        v_sgmsq = v_theta[(N+K*N):,0].reshape(N,1)
        m_beta = v_beta.reshape([N,K])

        v_sgm4h = v_sgmsq**2
        v_sgm6h = v_sgmsq**3

        a_x2 = np.transpose(a_x,(0,2,1))
        m_beta2 = m_beta[:,:,np.newaxis]
        m_beta_x = m_beta2*a_x2
        m_beta_x2 = np.transpose(m_beta_x,(0,2,1))
        m_beta_x_sum = np.sum(m_beta_x2,2)

        m_eps = m_y-v_psi*m_ys-m_beta_x_sum
        v_ssr = np.sum(m_eps**2,1).reshape(N,1)
        sssr = np.sum(v_ssr/v_sgmsq)
        m_Psi = v_psi * np.identity(len(v_psi))
        m_A = np.identity(N)-m_Psi@W
        det_mA= np.linalg.det(m_A)
        if det_mA<=0:
            print('Error: determinant(A)<=0!')
        constant = np.log(2*np.pi)*N/2
        first_part = -np.log(det_mA)
        second_part = np.sum(np.log(v_sgmsq))/2
        third_part = sssr/(2*T)
        return constant + first_part+second_part+third_part


    def gradient(self,v_theta0,args):

        """
        Gradient of the objective function of the Hetsar class.

        :param v_theta0: (numpy.ndarray) parameter of initial values for the optimization algorithm
        :param args: (tuple) contains the arrays (m_y,m_ys,a_x,W)
        :rtype: (numpy.ndarray) Value of the gradient evaluated at the arguments.
        """

        v_theta = v_theta0.reshape(len(v_theta0),1)
        m_y,m_ys,a_x,W = args
        N,T,K = a_x.shape
        v_psi = v_theta[:N,0].reshape(N,1)
        v_beta = v_theta[N:(N+K*N),0].reshape(N*K,1)
        v_sgmsq = v_theta[(N+K*N):,0].reshape(N,1)
        m_beta = v_beta.reshape([N,K])

        v_sgm4h = v_sgmsq**2
        v_sgm6h = v_sgmsq**3
        a_x2 = np.transpose(a_x,(0,2,1))
        m_beta2 = m_beta[:,:,np.newaxis]
        m_beta_x = m_beta2*a_x2
        m_beta_x2 = np.transpose(m_beta_x,(0,2,1))
        m_beta_x_sum = np.sum(m_beta_x2,2)

        m_eps = m_y-v_psi*m_ys-m_beta_x_sum
        v_ssr = np.sum(m_eps**2,1).reshape(N,1)
        m_Psi = v_psi * np.identity(len(v_psi))
        m_A = np.identity(N)-m_Psi@W
        m_Q = W@np.linalg.inv(m_A)
        v_dphi_dvpsi = np.diag(m_Q).reshape(N,1)-np.sum(m_ys*m_eps,1).reshape(N,1)/v_sgmsq/T
        m_eps2 = m_eps[:,:,np.newaxis]
        a_x_times_eps = m_eps2*a_x
        m_x_times_eps = np.sum(a_x_times_eps,1)
        m_X_times_eps_divinded_sgmsq = m_x_times_eps/v_sgmsq
        m_X_times_eps_divinded_sgmsq_tr = np.transpose(m_X_times_eps_divinded_sgmsq)
        v_dphi_dvbeta = -m_X_times_eps_divinded_sgmsq_tr.flatten('F')/T
        v_dphi_dvsgmsq = (0.5/v_sgmsq)-v_ssr/v_sgm4h/T/2
        grad = np.concatenate([v_dphi_dvpsi,v_dphi_dvbeta.reshape(N*K,1),v_dphi_dvsgmsq])
        return grad.reshape((K+2)*N,)

    def hessian(self,v_theta0,args):
        """
        Hessian of the objective function of the Hetsar class.

        :param v_theta0: (numpy.ndarray) parameter of initial values for the optimization algorithm
        :param args: (tuple) contains the arrays (m_y,m_ys,a_x,W)
        :rtype: (numpy.ndarray) Value of the Hessian evaluated at the arguments.
        """
        v_theta = v_theta0.reshape(len(v_theta0),1)
        m_y,m_ys,a_x,W = args
        N,T,K = a_x.shape
        v_psi = v_theta[:N,0].reshape(N,1)
        v_beta = v_theta[N:(N+K*N),0].reshape(N*K,1)
        v_sgmsq = v_theta[(N+K*N):,0].reshape(N,1)
        m_beta = v_beta.reshape([N,K])

        v_sgm4h = v_sgmsq**2
        v_sgm6h = v_sgmsq**3
        a_x2 = np.transpose(a_x,(0,2,1))
        m_beta2 = m_beta[:,:,np.newaxis]
        m_beta_x = m_beta2*a_x2
        m_beta_x2 = np.transpose(m_beta_x,(0,2,1))
        m_beta_x_sum = np.sum(m_beta_x2,2)

        m_eps = m_y-v_psi*m_ys-m_beta_x_sum
        v_ssr = np.sum(m_eps**2,1).reshape(N,1)
        m_Psi = v_psi * np.identity(len(v_psi))
        m_A = np.identity(N)-m_Psi@W
        m_Q = W@np.linalg.inv(m_A)
        m_H11a = m_Q*np.transpose(m_Q)
        m_H11b = np.sum(m_ys**2,1).reshape(N,1)*np.identity(N)/v_sgmsq/T
        m_H11 = m_H11a+m_H11b
        m_H13 = np.sum(m_ys*m_eps,1).reshape(N,1)*np.identity(N)/v_sgm4h/T
        m_H33 = (-0.5/v_sgm4h+v_ssr/v_sgm6h/T)*np.identity(N)
        m_H12 = np.zeros([N,N*K])
        m_H22 = np.zeros([N*K,N*K])
        m_H23 = np.zeros([N*K,N])

        for i in range(N):
            ind = (i * K + 1,(i+1) * K)
            v_ysi = m_ys[i,:].reshape(T,1)
            m_Xi = a_x[i,:,:] # TxK
            v_epsi = m_eps[i,:].reshape(T,1)
            sgmsqi = v_sgmsq[i,0]
            sgm4hi = v_sgm4h[i,0]
            m_H12[i,ind[0]-1:ind[1]] = np.transpose(v_ysi)@m_Xi/sgmsqi/T
            m_H22[ind[0]-1:ind[1],ind[0]-1:ind[1]] = np.transpose(m_Xi)@m_Xi/sgmsqi/T
            m_H23[ind[0]-1:ind[1],i] = np.transpose(np.transpose(m_Xi)@v_epsi/sgm4hi/T)

        row1 = np.concatenate((m_H11,m_H12,m_H13),axis = 1)
        row2 = np.concatenate((m_H12.T,m_H22,m_H23),axis = 1)
        row3 = np.concatenate((m_H13.T,m_H23.T,m_H33),axis = 1)

        return np.concatenate((row1,row2,row3),axis = 0)

    def fit(self,df,y,x,ind,t,W,spatial_lags = None,intercept = True,group = None,robust = True,
            method = 'L-BFGS-B', sigma_bnd = 0.01,theta_ini=None):

        """
        This function estimates the HSAR model.

        :param df: (pandas.DataFrame) Data frame that contains the data.
        :param y: (str) Name of dependent variable.
        :param x: (list[str]) List of exogenous variables.
        :param ind: (str) Name of ind variable.
        :param t: (str) Name of time variable.
        :param W: (numpy.ndarray) Row-normalized adjacency matrix.
        :param spatial_lags: (list[str]) List of variables for which spatial lags should be computed and used in the regression. Defaults to None.
        :param intercept: (bool) If True, a unit-specific fixed effect is added to the regression. Defaults to True.
        :param group: (str) Column that provindes a group label for every unique value of ind. Defaults to None.
        :param robust: (bool) If True, the sandwich variance estimator is used.
        :param method:
        :param sigma_bnd:
        :param theta_ini:
        :return: Instance of the RegressionResultsWrapper class
        """

        N = df[ind].nunique()
        T = df[t].nunique()

        if len(df)!=N*T:
            raise ValueError('Unbalanced Panel')

        indLabels = dict(zip([i+1 for i in range(N)],sorted(df[ind].unique())))
        K = len(x)

        exog_labels = x
        if intercept==True:
            K = K+1
            exog_labels = ['const']+x
        if type(spatial_lags)==list:
            K = K + len(spatial_lags)
            exog_labels = exog_labels + [f'W{i}' for i in spatial_lags]

        m_y = _generate_NT_array(df,ind,t,y)

        # spatial lag of dependent variable
        m_ys = W@m_y

        # covariates for the estimator
        a_x = np.ones((N,T,K))

        if intercept==True:
            i = 1
        else:
            i = 0

        for xvar in x:
            a_x[:,:,i] = _generate_NT_array(df,ind,t,xvar)
            i = i+1
        if type(spatial_lags)==list:
            for xsvar in spatial_lags:
                m_xs = _generate_NT_array(df,ind,t,xsvar)
                a_x[:,:,i] = W@m_xs
                i = i+1
        assert(i==K)



        # arguments for the objective function
        args = (m_y,m_ys,a_x,W)

        if theta_ini==None:
            # starting parameter for the optimization algorithm
            v_theta_ini = np.concatenate([np.zeros([(K+1)*N]),np.ones([N])])
        else:
            v_theta_ini = theta_ini
        # lower bound
        v_lb = -np.concatenate([0.995*np.ones(N),np.inf*np.ones(K*N),sigma_bnd*np.ones(N)])
        # upper bound
        v_ub = np.concatenate([0.995*np.ones(N),np.inf*np.ones((K+1)*N)])
        bnds = tuple([(v_lb[i],v_ub[i]) for i in range(len(v_lb))])


        optim_output = minimize(self.objective_function, v_theta_ini, args=(args,),jac=self.gradient,
                       bounds = bnds,method = method,
                      options = {'maxiter':1000})

        (variance,variance_sand) = fn_varml_sandwich_Npsi_NKbeta_Nsgmsq(optim_output.x.reshape([N*(K+2),1]),m_y,m_ys,a_x,W)
        df_est = format_output(optim_output,N,T,K,variance,variance_sand,y,exog_labels,ind)


        if group== None:
            df_est['group'] = 1
        else:
            groupLabels = dict(zip(df[ind],df[group]))
            df_est['group'] = df_est[ind].apply(lambda x: groupLabels[indLabels[x]])


        mg_vars = [f'W{y}']+exog_labels+['sgmsq']
        mg_est_list = []
        for var_hat in mg_vars:
            mg_est_list = mg_est_list + [fn_mg_est(df_est,var_hat,'group')]

        df_mg_est = reduce(lambda left,right: pd.merge(left,right,on='group'), mg_est_list)

        return RegressionResultsWrapper(self.modelstring,a_x,m_y,m_ys,W,y,ind,exog_labels,v_theta_ini,bnds,optim_output,variance,variance_sand,df_est,df_mg_est,N,T,K,robust)










