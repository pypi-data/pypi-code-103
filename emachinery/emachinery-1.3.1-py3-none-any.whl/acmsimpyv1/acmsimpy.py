# %%
try:
    from numba.experimental import jitclass
except:
    from numba import jitclass
from numba import njit#, types, vectorize, prange
from numba import int32, float64 # import the types
from pylab import np, plt
plt.style.use('ggplot')


############################################# CLASS DEFINITION 
@jitclass(
    spec=[
        # CONSOLE
            # ('reset', int32),
            ('sensorless_position', int32),
            ('sensorless_speed', int32),
            ('CMD_SPEED_SINE_HZ', float64),
            ('CMD_SPEED_SINE_RPM', float64),
        # CONTROL
            ('use_disturbance_feedforward_rejection', int32),
            ('KP', float64),
        # MOTOR
            # name plate data
            ('init_npp',   int32),
            ('init_IN',  float64),
            # electrical parameters
            ('init_R',   float64),
            ('init_Ld',  float64),
            ('init_Lq',  float64),
            ('init_KE',  float64),
            ('init_Rreq',float64),
            # mechanical parameters
            ('init_Js',  float64),
    ])
class The_Human:
    def __init__(self):
        # self.reset = False
        self.sensorless_position = False
        self.sensorless_speed    = False
        self.CMD_SPEED_SINE_HZ   = 10
        self.CMD_SPEED_SINE_RPM  = 0
        # ADRC
        self.use_disturbance_feedforward_rejection = 0
        self.KP = 100
        # name plate data
        self.init_npp = 4
        self.init_IN = 3 # Arms (line-to-line)
        # electrical parameters
        self.init_R = 1.1
        self.init_Ld = 5e-3
        self.init_Lq = 6e-3 # 5e-3 #BUG
        self.init_KE = 0.095
        self.init_Rreq = -1.0 # this should be set to infinity but setting to a negative value is easier for coding
        # mechanical parameters
        self.init_Js = 0.0006168  # kg.m^2

@jitclass(
    spec=[
        # name plate data
        ('npp',   int32),
        ('npp_inv', float64),
        ('IN',  float64),
        # electrical parameters
        ('R',   float64),
        ('Ld',  float64),
        ('Lq',  float64),
        ('KE',  float64),
        ('Rreq',float64),
        # mechanical parameters
        ('Js',  float64),
        ('Js_inv', float64),
        # states
        ('NS',    int32),
        ('x',   float64[:]),
        ('Tem', float64),
        # inputs
        ('uab',   float64[:]),
        ('udq',   float64[:]),
        ('TLoad', float64),
        # output
        ('cosT', float64),
        ('sinT', float64),
        ('iab',  float64[:]),
        ('idq',  float64[:]),
        ('omega_elec', float64),
        ('theta_d', float64),
        ('theta_mech', float64),
        ('KActive', float64),
    ])
class The_AC_Machines:
    def __init__(self, HUMAN):
        # name plate data
        self.npp = HUMAN.init_npp
        self.npp_inv = 1.0/self.npp
        self.IN  = HUMAN.init_IN
        # electrical parameters
        self.R   = HUMAN.init_R
        self.Ld  = HUMAN.init_Ld
        self.Lq  = HUMAN.init_Lq
        self.KE  = HUMAN.init_KE
        self.Rreq  = HUMAN.init_Rreq
        # mechanical parameters
        self.Js  = HUMAN.init_Js # kg.m^2
        self.Js_inv = 1.0/self.Js
        # states
        self.NS = 6
        self.x = np.zeros(self.NS, dtype=np.float64)
        self.x[5] = self.KE
        self.Tem = 0.0
        # inputs
        self.uab = np.zeros(2, dtype=np.float64)
        self.udq = np.zeros(2, dtype=np.float64)
        self.TLoad = 0
        # output
        self.cosT = 0.0
        self.sinT = 0.0
        self.iab = np.zeros(2, dtype=np.float64)
        self.idq = np.zeros(2, dtype=np.float64)
        self.omega_elec = 0.0
        self.theta_d = 0.0
        self.theta_mech = 0.0
        self.KActive = self.KE

@jitclass(
    spec=[
        # constants
        ('CL_TS', float64),
        ('VL_TS', float64),
        # feedback / input
        ('theta_d', float64),
        ('omega_elec', float64),
        ('iab', float64[:]),
        # states
        ('timebase', float64),
        ('cosT', float64),
        ('sinT', float64),
        ('idq', float64[:]),
        ('KActive', float64),
        ('Tem', float64),
        # commands
        ('cmd_idq', float64[:]),
        ('cmd_udq', float64[:]),
        ('cmd_uab', float64[:]),
        ('cmd_rpm', float64),
        # MOTOR
            # name plate data
            ('npp',   int32),
            ('IN',  float64),
            # electrical parameters
            ('R',   float64),
            ('Ld',  float64),
            ('Lq',  float64),
            ('KE',  float64),
            ('Rreq',float64),
            # mechanical parameters
            ('Js',  float64),
    ])
class The_Motor_Controller:
    def __init__(self, CL_TS, VL_TS, HUMAN):
        # constants
        self.CL_TS = CL_TS
        self.VL_TS = VL_TS
        # feedback / input
        self.theta_d = 0.0
        self.omega_elec = 0.0
        self.iab = np.zeros(2, dtype=np.float64)
        # states
        self.timebase = 0.0
        self.cosT = 0.0
        self.sinT = 0.0
        self.idq = np.zeros(2, dtype=np.float64)
        self.KActive = 0.0
        self.Tem = 0.0
        # commands 
        self.cmd_idq = np.zeros(2, dtype=np.float64)
        self.cmd_udq = np.zeros(2, dtype=np.float64)
        self.cmd_uab = np.zeros(2, dtype=np.float64)
        self.cmd_rpm = 0.0
        # MOTOR
        self.npp = HUMAN.init_npp
        self.IN  = HUMAN.init_IN
        self.R   = HUMAN.init_R
        self.Ld  = HUMAN.init_Ld
        self.Lq  = HUMAN.init_Lq
        self.KE  = HUMAN.init_KE
        self.Rreq = HUMAN.init_Rreq
        self.Js  = HUMAN.init_Js

@jitclass(
    spec=[
        ('Kp', float64),
        ('Ki', float64),
        ('Err', float64),
        ('Ref', float64),
        ('Fbk', float64),
        ('Out', float64),
        ('OutLimit', float64),
        ('ErrPrev', float64),
        ('OutPrev', float64),
    ])
class The_PI_Regulator:
    def __init__(self, KP_CODE, KI_CODE, OUTPUT_LIMIT):
        self.Kp = KP_CODE
        self.Ki = KI_CODE
        self.Err      = 0.0
        self.Ref      = 0.0
        self.Fbk      = 0.0
        self.Out      = 0.0
        self.OutLimit = OUTPUT_LIMIT
        self.ErrPrev  = 0.0
        self.OutPrev  = 0.0

############################################# OBSERVER SECTION

@jitclass(
    spec=[
        # feedback / inputs
        ('uab', float64[:]),
        ('uab_prev', float64[:]),
        ('uab_curr', float64[:]),
        ('iab', float64[:]),
        ('iab_prev', float64[:]),
        ('iab_curr', float64[:]),
        # states
        ('NS', int32),
        ('NS_SPEED', int32),
        ('NS_FLUX', int32),
        ('xspeed', float64[:]),
        ('xflux', float64[:]),
        ('cosT', float64),
        ('sinT', float64),
        # outputs
        ('theta_d', float64),
        ('omega_elec', float64),
        ('total_disrubance_feedforward', float64),
        ('output_error', float64),
        ('amplitude_mismatch', float64[:]),
        ('stator_flux', float64[:]),
        ('u_offset', float64[:]),
        ('active_flux', float64[:]),
        ('active_flux_ampl', float64),
        ('active_flux_ampl_lpf', float64),
        ('ActiveFlux_KP', float64),
        ('ActiveFlux_KI', float64),
        # gains
        ('ell1', float64),
        ('ell2', float64),
        ('ell3', float64),
        ('ell4', float64),
        ('one_over_six', float64),
        # MOTOR
            # # name plate data
            # ('npp',   int32),
            # ('IN',  float64),
            # # electrical parameters
            # ('R',   float64),
            # ('Ld',  float64),
            # ('Lq',  float64),
            # ('KE',  float64),
            # ('Rreq',float64),
            # # mechanical parameters
            # ('Js',  float64),
    ])
class The_Observer:
    def __init__(self, HUMAN):
        # feedback / input
        self.uab      = np.zeros(2, dtype=np.float64)
        self.uab_prev = np.zeros(2, dtype=np.float64)
        self.uab_curr = np.zeros(2, dtype=np.float64)
        self.iab      = np.zeros(2, dtype=np.float64)
        self.iab_prev = np.zeros(2, dtype=np.float64)
        self.iab_curr = np.zeros(2, dtype=np.float64)
        # state
        self.NS       = 4 # = max(NS_SPEED, NS_FLUX)
        self.NS_SPEED = 4
        self.NS_FLUX  = 4
        self.xspeed = np.zeros(self.NS_SPEED, dtype=np.float64)
        self.xflux = np.zeros(self.NS_FLUX, dtype=np.float64)
        self.cosT = 1.0
        self.sinT = 0.0
        # outputs
        self.theta_d    = 0.0
        self.omega_elec = 0.0
        self.total_disrubance_feedforward = 0.0
        self.output_error = 0.0
        self.amplitude_mismatch = np.zeros(2, dtype=np.float64)
        self.stator_flux = np.zeros(2, dtype=np.float64)
        self.u_offset = np.zeros(2, dtype=np.float64)
        self.active_flux = np.zeros(2, dtype=np.float64)
        self.active_flux[0] = HUMAN.init_KE
        self.active_flux_ampl = HUMAN.init_KE
        self.active_flux_ampl_lpf = HUMAN.init_KE
        self.ActiveFlux_KP = 200
        self.ActiveFlux_KI = 0.0

        # gains
        omega_ob = 100 # [rad/s]
        if False: # 2nd-order speed observer (assuming speed feedback)
            self.ell2 = 2 * omega_ob
            self.ell3 =     omega_ob**2 * HUMAN.init_Js/HUMAN.init_npp
        elif True: # 3rd-order position observer
            self.ell1 = 3 * omega_ob
            self.ell2 = 3 * omega_ob**2
            self.ell3 =     omega_ob**3 * HUMAN.init_Js/HUMAN.init_npp
            self.ell4 = 0.0
        else: # 4th-order position observer
            self.ell1 = 4 * omega_ob
            self.ell2 = 6 * omega_ob**2
            self.ell3 = 4 * omega_ob**3 * HUMAN.init_Js/HUMAN.init_npp
            self.ell4 =     omega_ob**4

        self.one_over_six = 1.0 / 6.0

        # MOTOR
        # self.npp = HUMAN.init_npp
        # self.IN  = HUMAN.init_IN
        # self.R   = HUMAN.init_R
        # self.Ld  = HUMAN.init_Ld
        # self.Lq  = HUMAN.init_Lq
        # self.KE  = HUMAN.init_KE
        # self.Rreq = HUMAN.init_Rreq
        # self.Js  = HUMAN.init_Js

@njit(nogil=True)
def DYNAMICS_2ndOdESO_LOF(x, OB, CTRL):
    fx = np.zeros(OB.NS_SPEED)

    # [rad/s]
    output_error = CTRL.omega_elec - x[1]

    # 机械子系统 (omega_r_elec, theta_d, theta_r_mech)
    fx[0] = x[1]
    fx[1] = OB.ell2*output_error + (CTRL.Tem + x[2]) * CTRL.npp/CTRL.Js # elec. angular rotor speed
    fx[2] = OB.ell3*output_error + 0.0
    fx[3] = 0.0
    return fx

@njit(nogil=True)
def DYNAMICS_4thOdESO_LOF(x, OB, CTRL):
    fx = np.zeros(OB.NS_SPEED)

    # [rad]
    output_error = np.sin(CTRL.theta_d - x[0])

    # 机械子系统 (omega_r_elec, theta_d, theta_r_mech)
    fx[0] = OB.ell1*output_error + x[1]
    fx[1] = OB.ell2*output_error + (CTRL.Tem + x[2]) * CTRL.npp/CTRL.Js # elec. angular rotor speed
    fx[2] = OB.ell3*output_error + x[3]
    fx[3] = OB.ell4*output_error + 0.0
    return fx

@njit(nogil=True)
def DYNAMICS_AFE_25_VMCMFusion(x, OB, CTRL):
    fx = np.zeros(OB.NS_FLUX)

    OB.active_flux[0] = x[0] - CTRL.Lq * CTRL.iab[0]
    OB.active_flux[1] = x[1] - CTRL.Lq * CTRL.iab[1]
    OB.active_flux_ampl = np.sqrt(OB.active_flux[0]*OB.active_flux[0] + OB.active_flux[1]*OB.active_flux[1])

    if OB.active_flux_ampl!=0:
        active_flux_ampl_inv = 1.0/OB.active_flux_ampl
        OB.cosT = OB.active_flux[0] * active_flux_ampl_inv
        OB.sinT = OB.active_flux[1] * active_flux_ampl_inv
    else:
        OB.cosT = 1.0
        OB.sinT = 0.0
    
    iD_at_current_step = CTRL.iab[0] * OB.cosT + CTRL.iab[1] * OB.sinT
    # iQ_at_current_step = CTRL.iab[0] *-OB.sinT + CTRL.iab[1] * OB.cosT
    CTRL.KActive = (CTRL.Ld - CTRL.Lq) * iD_at_current_step + CTRL.KE # 有功磁链计算

    OB.amplitude_mismatch[0] = CTRL.KActive*OB.cosT - OB.active_flux[0]
    OB.amplitude_mismatch[1] = CTRL.KActive*OB.sinT - OB.active_flux[1]

    fx[0] = CTRL.cmd_uab[0] - CTRL.R*CTRL.iab[0] \
            + OB.ActiveFlux_KP * OB.amplitude_mismatch[0] \
            + x[2]
    fx[1] = CTRL.cmd_uab[1] - CTRL.R*CTRL.iab[1] \
            + OB.ActiveFlux_KP * OB.amplitude_mismatch[1] \
            + x[3]

    fx[2] = OB.ActiveFlux_KI * OB.amplitude_mismatch[0]
    fx[3] = OB.ActiveFlux_KI * OB.amplitude_mismatch[1]
    return fx

@njit(nogil=True)
def RK4_OBSERVER_CJH_STYLE(THE_DYNAMICS, x, OB, hs, CTRL):
    NS = OB.NS # THIS SHOULD BE A CONSTANT THROUGHOUT THE CODES!!!
    k1, k2, k3, k4 = np.zeros(NS), np.zeros(NS), np.zeros(NS), np.zeros(NS) # incrementals at 4 stages
    xk, fx = np.zeros(NS), np.zeros(NS) # state x for stage 2/3/4, state derivative

    OB.uab[0] = OB.uab_prev[0]
    OB.uab[1] = OB.uab_prev[1]
    OB.iab[0] = OB.iab_prev[0]
    OB.iab[1] = OB.iab_prev[1]
    fx = THE_DYNAMICS(x, OB, CTRL)
    for i in range(0, NS):
        k1[i] = fx[i] * hs
        xk[i] = x[i] + k1[i]*0.5
                                                                         
    OB.iab[0] = 0.5*(OB.iab_prev[0]+OB.iab_curr[0])
    OB.iab[1] = 0.5*(OB.iab_prev[1]+OB.iab_curr[1])
    OB.uab[0] = 0.5*(OB.uab_prev[0]+OB.uab_curr[0])
    OB.uab[1] = 0.5*(OB.uab_prev[1]+OB.uab_curr[1])
    fx = THE_DYNAMICS(xk, OB, CTRL)
    for i in range(0, NS):
        k2[i] = fx[i] * hs
        xk[i] = x[i] + k2[i]*0.5
                                                                         
    fx = THE_DYNAMICS(xk, OB, CTRL)
    for i in range(0, NS):
        k3[i] = fx[i] * hs
        xk[i] = x[i] + k3[i]
                                                                         
    OB.iab[0] = OB.iab_curr[0]
    OB.iab[1] = OB.iab_curr[1]
    OB.uab[0] = OB.uab_curr[0]
    OB.uab[1] = OB.uab_curr[1]
    fx = THE_DYNAMICS(xk, OB, CTRL)
    for i in range(0, NS):
        k4[i] = fx[i] * hs
        x[i] = x[i] + (k1[i] + 2*(k2[i] + k3[i]) + k4[i]) * OB.one_over_six

############################################# MACHINE SIMULATION SECTION

@njit(nogil=True)
def DYNAMICS_MACHINE(t, x, ACM, CLARKE_TRANS_TORQUE_GAIN=1.5):
    fx = np.zeros(ACM.NS)

    # 电磁子系统 (id, iq, KActive as x[0], x[1], x[5])
    if ACM.Rreq > 0:
    # IM: Rreq is positive
        fx[5] = ACM.Rreq*x[0] - (ACM.Ld - ACM.Lq)/ACM.Rreq * x[5]
        ACM.KActive = x[5]
        fx[0] = (ACM.udq[0] - ACM.R*x[0] + x[2]*ACM.Lq*x[1] + fx[5]) / ACM.Lq
    else:
    # PMSM: Rreq is infinitely large
        # ACM.KActive = (ACM.Ld - ACM.Lq) * x[0] + ACM.KE # version 1
        ACM.KActive = x[5]                              # version 2 
        fx[0] = (ACM.udq[0] - ACM.R*x[0] + x[2]*ACM.Lq*x[1]) / ACM.Ld
        fx[5] = (ACM.Ld - ACM.Lq) * fx[0] + 0.0

    fx[1] = (ACM.udq[1] - ACM.R*x[1] - x[2]*ACM.Lq*x[0] - x[2]*ACM.KActive) / ACM.Lq

    # 机械子系统 (omega_r_elec, theta_d, theta_r_mech as x[2], x[3], x[4])
    ACM.Tem = CLARKE_TRANS_TORQUE_GAIN * ACM.npp * ACM.KActive *x[1] # 电磁转矩计算
    fx[2] = (ACM.Tem - ACM.TLoad) * ACM.npp/ACM.Js # elec. angular rotor speed
    fx[3] = x[2]          # elec. angular rotor position (bounded)
    fx[4] = x[2]/ACM.npp  # mech. angular rotor position (accumulated)
    return fx

@njit(nogil=True)
def RK4_MACHINE(t, ACM, hs): # 四阶龙格库塔法
    NS = ACM.NS
    k1, k2, k3, k4 = np.zeros(NS), np.zeros(NS), np.zeros(NS), np.zeros(NS) # incrementals at 4 stages
    xk, fx = np.zeros(NS), np.zeros(NS) # state x for stage 2/3/4, state derivative

    if False:
        """ this is about twice slower than loop through the element one by one """ 
        fx = DYNAMICS_MACHINE(t, ACM.x, ACM) # @t
        k1 = fx * hs
        xk = ACM.x + k1*0.5

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs/2
        k2 = fx * hs
        xk = ACM.x + k2*0.5

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs/2
        k3 = fx * hs
        xk = ACM.x + k3

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs
        k4 = fx * hs
        ACM.x = ACM.x + (k1 + 2*(k2 + k3) + k4)/6.0
    else:
        fx = DYNAMICS_MACHINE(t, ACM.x, ACM) # @t
        for i in range(NS):
            k1[i] = fx[i] * hs
            xk[i] = ACM.x[i] + k1[i]*0.5

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs/2
        for i in range(NS):
            k2[i] = fx[i] * hs
            xk[i] = ACM.x[i] + k2[i]*0.5

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs/2
        for i in range(NS):
            k3[i] = fx[i] * hs
            xk[i] = ACM.x[i] + k3[i]

        fx = DYNAMICS_MACHINE(t, xk, ACM)  # @t+hs
        for i in range(NS):
            k4[i] = fx[i] * hs
            ACM.x[i] = ACM.x[i] + (k1[i] + 2*(k2[i] + k3[i]) + k4[i])/6.0
            # ACM.x_dot[i] = (k1[i] + 2*(k2[i] + k3[i]) + k4[i])/6.0 / hs # derivatives

############################################# BASIC FOC SECTION

@njit(nogil=True)
def incremental_pi(reg):
    reg.Err = reg.Ref - reg.Fbk
    reg.Out = reg.OutPrev + \
        reg.Kp * (reg.Err - reg.ErrPrev) + \
        reg.Ki * reg.Err
    if reg.Out >    reg.OutLimit:
        reg.Out =   reg.OutLimit
    elif reg.Out < -reg.OutLimit:
        reg.Out =  -reg.OutLimit
    reg.ErrPrev = reg.Err
    reg.OutPrev = reg.Out

@njit(nogil=True)
def FOC(CTRL, reg_id, reg_iq, reg_speed, OB, HUMAN):
    reg_speed.Ref = CTRL.cmd_rpm / 60 * 2*np.pi * CTRL.npp
    reg_speed.Fbk = CTRL.omega_elec
    incremental_pi(reg_speed)

    reg_id.Ref = CTRL.cmd_idq[0]
    reg_id.Fbk = CTRL.idq[0]
    incremental_pi(reg_id)
    CTRL.cmd_udq[0] = reg_id.Out

    if HUMAN.use_disturbance_feedforward_rejection == 0:
        CTRL.cmd_idq[1] = reg_speed.Out
    else:
        CTRL.cmd_idq[1] = HUMAN.KP*(reg_speed.Ref-reg_speed.Fbk) + OB.total_disrubance_feedforward

    reg_iq.Ref = CTRL.cmd_idq[1]
    reg_iq.Fbk = CTRL.idq[1]
    incremental_pi(reg_iq)
    CTRL.cmd_udq[1] = reg_iq.Out

    return CTRL.cmd_udq

############################################# DSP SECTION

""" DSP """
@njit(nogil=True)
def DSP(ACM, CTRL, reg_id, reg_iq, reg_speed, OB, HUMAN):
    CTRL.timebase += CTRL.CL_TS

    """ Current Measurment """
    CTRL.iab[0] = ACM.iab[0] # + offset, scale error , noise
    CTRL.iab[1] = ACM.iab[1] # + offset, scale error , noise

    """ Position Measurement """
    if not HUMAN.sensorless_position:
        CTRL.theta_d = ACM.theta_d + 0.10*0 #BUG???

    """ Position and Speed Estimator """
    RK4_OBSERVER_CJH_STYLE(DYNAMICS_AFE_25_VMCMFusion, OB.xflux, OB, CTRL.CL_TS, CTRL)
    # Unpack x
    OB.stator_flux[0] = OB.xflux[0]
    OB.stator_flux[1] = OB.xflux[1]
    OB.u_offset[0] = OB.xflux[2]
    OB.u_offset[1] = OB.xflux[3]
    # Active flux
    OB.active_flux[0] = OB.xflux[0] - CTRL.Lq * CTRL.iab[0]
    OB.active_flux[1] = OB.xflux[1] - CTRL.Lq * CTRL.iab[1]
    OB.theta_d = np.arctan2(OB.active_flux[1], OB.active_flux[0])
    OB.active_flux_ampl = np.sqrt(OB.active_flux[0]*OB.active_flux[0] + OB.active_flux[1]*OB.active_flux[1])
    OB.active_flux_ampl_lpf = OB.active_flux_ampl #_lpf(OB.active_flux_ampl, OB.active_flux_ampl_lpf, 5)
    if OB.active_flux_ampl!=0:
        active_flux_ampl_inv = 1.0/OB.active_flux_ampl
        OB.cosT = OB.active_flux[0] * active_flux_ampl_inv
        OB.sinT = OB.active_flux[1] * active_flux_ampl_inv
    else:
        OB.cosT = 1.0
        OB.sinT = 0.0
    OB.amplitude_mismatch[0] = CTRL.KActive*OB.cosT - OB.active_flux[0]
    OB.amplitude_mismatch[1] = CTRL.KActive*OB.sinT - OB.active_flux[1]

    if HUMAN.sensorless_position:
        CTRL.theta_d = OB.theta_d

    """ Park Transformation Essentials
    """
    # do this once per control interrupt
    CTRL.cosT = np.cos(CTRL.theta_d)
    CTRL.sinT = np.sin(CTRL.theta_d)
    # Park transformation
    CTRL.idq[0] = CTRL.iab[0] * CTRL.cosT + CTRL.iab[1] * CTRL.sinT
    CTRL.idq[1] = CTRL.iab[0] *-CTRL.sinT + CTRL.iab[1] * CTRL.cosT

    """ Speed Observer """
    CTRL.KActive = (CTRL.Ld - CTRL.Lq) * CTRL.idq[0] + CTRL.KE # 有功磁链计算
    CTRL.Tem = 1.5 * CTRL.npp * CTRL.idq[1]*CTRL.KActive       # 电磁转矩计算
    if True:
        OB.iab_curr[0] = CTRL.iab[0]
        OB.iab_curr[1] = CTRL.iab[1]
        OB.uab_prev[0] = CTRL.cmd_uab[0] # Updating "OB.uab_prev[0]" here, which will be useful if voltage is measured, and is useless if assume command voltage is actual voltage.
        OB.uab_prev[1] = CTRL.cmd_uab[1] # Updating "OB.uab_prev[1]" here, which will be useful if voltage is measured, and is useless if assume command voltage is actual voltage.
        OB.uab_curr[0] = CTRL.cmd_uab[0]
        OB.uab_curr[1] = CTRL.cmd_uab[1]
        if False:
            RK4_OBSERVER_CJH_STYLE(DYNAMICS_2ndOdESO_LOF, OB.xspeed, OB, CTRL.CL_TS, CTRL)
        else:
            OB.output_error = np.sin(CTRL.theta_d - OB.xspeed[0]) # OE version 1
            RK4_OBSERVER_CJH_STYLE(DYNAMICS_4thOdESO_LOF, OB.xspeed, OB, CTRL.CL_TS, CTRL)
            # OB.output_error = np.sin(CTRL.theta_d - OB.xspeed[0]) # OE version 2
        while OB.xspeed[0]> np.pi: OB.xspeed[0] -= 2*np.pi
        while OB.xspeed[0]<-np.pi: OB.xspeed[0] += 2*np.pi
        OB.iab_prev[0] = OB.iab_curr[0]
        OB.iab_prev[1] = OB.iab_curr[1]
        # OB.uab_prev[0] = OB.uab_curr[0] # This is needed only if voltage is measured, e.g., by eCAP.
        # OB.uab_prev[1] = OB.uab_curr[1] # This is needed only if voltage is measured, e.g., by eCAP.

        """ Observer Outputs """
        OB.theta_d    = OB.xspeed[0]
        OB.omega_elec = OB.xspeed[1]
        if HUMAN.use_disturbance_feedforward_rejection == 0:
            OB.total_disrubance_feedforward = 0.0
        if HUMAN.use_disturbance_feedforward_rejection == 1:
            OB.total_disrubance_feedforward = OB.xspeed[2]
        elif HUMAN.use_disturbance_feedforward_rejection == 2:
            OB.total_disrubance_feedforward = OB.xspeed[2] + OB.ell2*OB.output_error

    """ Speed Measurement """
    if HUMAN.sensorless_speed:
        CTRL.omega_elec = OB.omega_elec
    else:
        CTRL.omega_elec = ACM.omega_elec

    """ (Optional) Do Park transformation again using the position estimate from the speed observer """

    """ Speed Controller """
    CTRL.cmd_udq = FOC(CTRL, reg_id, reg_iq, reg_speed, OB, HUMAN)
    # Inverse Park transformation
    CTRL.cmd_uab[0] = CTRL.cmd_udq[0] * CTRL.cosT + CTRL.cmd_udq[1] *-CTRL.sinT
    CTRL.cmd_uab[1] = CTRL.cmd_udq[0] * CTRL.sinT + CTRL.cmd_udq[1] * CTRL.cosT

    """ Inverter """
    ACM.uab[0] = CTRL.cmd_uab[0] # + current denpendent distorted voltage
    ACM.uab[1] = CTRL.cmd_uab[1] # + current denpendent distorted voltage

############################################# Wrapper level 1
""" MAIN for Real-time simulation """
@njit(nogil=True)
def ACMSimPyIncremental(
        t0, TIME,
        ACM=None,
        CTRL=None,
        reg_id=None,
        reg_iq=None,
        reg_speed=None,
        OB=None,
        HUMAN=None,
    ):
    MACHINE_TS = CTRL.CL_TS
    down_sampling_ceiling = int(CTRL.CL_TS / MACHINE_TS) #print('\tdown sample:', down_sampling_ceiling)

    # watch variabels
    machine_times  = np.arange(t0, t0+TIME, MACHINE_TS)
    control_times  = np.arange(t0, t0+TIME, CTRL.CL_TS)
    watch_data = np.zeros( (30, len(control_times)) )

    # Main loop
    # print('\tt0 =', t0)
    jj = 0; watch_index = 0
    for ii in range(len(machine_times)):

        t = machine_times[ii]

        """ Machine Simulation @ MACHINE_TS """
        # Park transformation
        ACM.udq[0] = ACM.uab[0] *  ACM.cosT + ACM.uab[1] * ACM.sinT
        ACM.udq[1] = ACM.uab[0] * -ACM.sinT + ACM.uab[1] * ACM.cosT
        # Numerical Integration (ode4) with 5 states
        RK4_MACHINE(t, ACM, hs=MACHINE_TS)

        """ Machine Simulation Output @ MACHINE_TS """
        # Generate output variables for easy access
        if ACM.x[3]> np.pi: ACM.x[3] -= 2*np.pi
        if ACM.x[3]<-np.pi: ACM.x[3] += 2*np.pi
        if ACM.x[4]> np.pi: ACM.x[4] -= 2*np.pi
        if ACM.x[4]<-np.pi: ACM.x[4] += 2*np.pi
        ACM.idq[0]      = ACM.x[0]
        ACM.idq[1]      = ACM.x[1]
        ACM.omega_elec  = ACM.x[2]
        ACM.theta_d     = ACM.x[3]
        ACM.theta_mech  = ACM.x[4]
        ACM.KActive     = ACM.x[5]
        # Inverse Park transformation
        ACM.cosT = np.cos(ACM.theta_d)
        ACM.sinT = np.sin(ACM.theta_d)
        ACM.iab[0] = ACM.x[0] * ACM.cosT + ACM.x[1] *-ACM.sinT
        ACM.iab[1] = ACM.x[0] * ACM.sinT + ACM.x[1] * ACM.cosT

        jj += 1
        if jj >= down_sampling_ceiling:
            jj = 0

            """ DSP @ CL_TS """
            DSP(ACM=ACM,
                CTRL=CTRL,
                reg_id=reg_id,
                reg_iq=reg_iq,
                reg_speed=reg_speed,
                OB=OB,
                HUMAN=HUMAN)

            """ Console @ CL_TS """
            if t < 1.0:
                CTRL.cmd_rpm = 50
            elif t < 1.5:
                ACM.TLoad = 2
            elif t < 2.0:
                CTRL.cmd_rpm = 200
            elif t < 3.0:
                CTRL.cmd_rpm = -200
            elif t < 4.0:
                CTRL.cmd_rpm = 0
            elif t < 4.5:
                CTRL.cmd_rpm = 2000
            elif t < 5:
                CTRL.cmd_idq[0] = 2
            elif t < 5.5:
                ACM.TLoad = 0.0
            elif t < 6: 
                HUMAN.CMD_SPEED_SINE_RPM = 500
            # else: # don't implement else to receive commands from IPython console

            if HUMAN.CMD_SPEED_SINE_RPM!=0:
                CTRL.cmd_rpm = HUMAN.CMD_SPEED_SINE_RPM * np.sin(2*np.pi*HUMAN.CMD_SPEED_SINE_HZ*t)

            """ Watch @ CL_TS """
            watch_data[ 0][watch_index] = ACM.x[0] # id
            watch_data[ 1][watch_index] = ACM.x[1] # iq
            watch_data[ 2][watch_index] = ACM.x[2] # omega_elec
            watch_data[ 3][watch_index] = ACM.x[3] # thete_d
            watch_data[ 4][watch_index] = ACM.x[4] # theta_mech
            watch_data[ 5][watch_index] = ACM.x[5] # KActive
            watch_data[ 6][watch_index] = CTRL.iab[0]
            watch_data[ 7][watch_index] = CTRL.iab[1]
            watch_data[ 8][watch_index] = CTRL.idq[0]
            watch_data[ 9][watch_index] = CTRL.idq[1]
            watch_data[10][watch_index] = CTRL.theta_d
            watch_data[11][watch_index] = CTRL.omega_elec / (2*np.pi*ACM.npp) * 60
            watch_data[12][watch_index] = CTRL.cmd_rpm
            watch_data[13][watch_index] = CTRL.cmd_idq[0]
            watch_data[14][watch_index] = CTRL.cmd_idq[1]
            watch_data[15][watch_index] = OB.xspeed[0] # theta_d
            watch_data[16][watch_index] = OB.xspeed[1] / (2*np.pi*ACM.npp) * 60 # omega_elec
            watch_data[17][watch_index] = OB.xspeed[2] # TL
            watch_data[18][watch_index] = OB.xspeed[3] # pT
            watch_data[19][watch_index] = CTRL.KActive
            watch_data[20][watch_index] = CTRL.KE
            watch_data[21][watch_index] = OB.xflux[0] # stator flux[0]
            watch_data[22][watch_index] = OB.xflux[1] # stator flux[1]
            watch_data[23][watch_index] = OB.xflux[2] # I term
            watch_data[24][watch_index] = OB.xflux[3] # I term
            watch_data[25][watch_index] = OB.active_flux[0] # active flux[0]
            watch_data[26][watch_index] = OB.active_flux[1] # active flux[1]
            watch_data[27][watch_index] = OB.theta_d # d-axis position
            watch_index += 1

    return control_times, watch_data
Watch_Mapping = [
    '[A]=ACM.x[0]', # id
    '[A]=ACM.x[1]', # iq
    '[rad/s]=ACM.x[2]', # omega_elec
    '[rad]=ACM.x[3]', # thete_d
    '[rad]=ACM.x[4]', # theta_mech
    '[Wb]=ACM.x[5]', # KActive
    '[A]=CTRL.iab[0]',
    '[A]=CTRL.iab[1]',
    '[A]=CTRL.idq[0]',
    '[A]=CTRL.idq[1]',
    '[rpm]=CTRL.theta_d',
    '[rpm]=CTRL.omega_elec',
    '[rpm]=CTRL.cmd_rpm',
    '[A]=CTRL.cmd_idq[0]',
    '[A]=CTRL.cmd_idq[1]',
    '[rad]=OB.xspeed[0]',  # theta_d
    '[rpm]=OB.xspeed[1]',  # omega_elec
    '[Nm]=OB.xspeed[2]',   # -TL
    '[Nm/s]=OB.xspeed[3]', # DL
    '[Wb]=CTRL.KActive',
    '[Wb]=CTRL.KE',
    '[Wb]=OB.xflux[0]', # stator flux[0]
    '[Wb]=OB.xflux[1]', # stator flux[1]
    '[V]=OB.xflux[2]', # I term
    '[V]=OB.xflux[3]', # I term
    '[Wb]=OB.active_flux[0]', # active flux[0]
    '[Wb]=OB.active_flux[1]', # active flux[1]
    '[rad]=OB.theta_d', # d-axis position
]

############################################# Wrapper level 2
def ACMSimPyWrapper(numba__scope_dict, *arg, **kwarg):

    # Do Numerical Integrations (that do not care about numba__scope_dict at all and return watch_data whatsoever)
    control_times, watch_data = ACMSimPyIncremental(*arg, **kwarg)

    # Post-processing
    numba__waveforms_dict = dict()
    for key, values in numba__scope_dict.items():
        # key = '$\alpha\beta$ current [A]'
        # values = ('CTRL.iab', 'CTRL.idq[1]'),
        waveforms = []
        for val in values:
            # val = 'CTRL.iab'
            for index, mapping in enumerate(Watch_Mapping):
                if val in mapping:
                    # CTRL.iab in '[A]=CTRL.iab[0]'
                    # CTRL.iab in '[A]=CTRL.iab[1]'
                    waveforms.append(watch_data[index])

                    # print('\t', key, val, 'in', mapping)
                    if len(val) == 1:
                        raise Exception('Invalid numba__scope_dict, make sure it is a dict of tuples of strings.')

        numba__waveforms_dict[key] = waveforms
    return control_times, numba__waveforms_dict



# %% Test incremental simulation
if __name__ == '__main__':

    # Simulation Basics
    CL_TS      = 1e-4
    TIME_SLICE = 1.0

    # Human
    HUMAN = The_Human()

    from collections import OrderedDict as OD
    numba__scope_dict = OD([
        (r'Speed [rpm]',                  ( 'CTRL.cmd_rpm', 'CTRL.omega_elec', 'OB.xspeed[1]'     ,) ),
        (r'Position [rad]',               ( 'ACM.x[3]', 'CTRL.theta_d', 'OB.xspeed[0]'            ,) ),
        (r'Position mech [rad]',          ( 'ACM.x[4]'                                       ,) ),
        (r'$q$-axis current [A]',         ( 'ACM.x[1]', 'CTRL.idq[1]', 'CTRL.cmd_idq[1]'     ,) ),
        (r'$d$-axis current [A]',         ( 'ACM.x[0]', 'CTRL.idq[0]', 'CTRL.cmd_idq[0]'     ,) ),
        (r'$\alpha\beta$ current [A]',    ( 'CTRL.iab'                        ,) ),
        (r'K_{\rm Active} [A]',           ( 'ACM.x[5]', 'CTRL.KActive'             ,) ),
        (r'Load torque [Nm]',             ( 'OB.xspeed[2]'                         ,) ),
    ])

    # init
    ACM       = The_AC_Machines(HUMAN)
    CTRL      = The_Motor_Controller(CL_TS, 5*CL_TS, HUMAN)
    reg_id    = The_PI_Regulator(6.39955, 6.39955*237.845*CTRL.CL_TS, 600)
    reg_iq    = The_PI_Regulator(6.39955, 6.39955*237.845*CTRL.CL_TS, 600)
    reg_speed = The_PI_Regulator(0.0380362, 0.0380362*30.5565*CTRL.VL_TS, 1*1.414*ACM.IN)
    OB        = The_Observer(HUMAN)

    # Global arrays
    global_ACM_speed, global__OB_speed = None, None
    global___KActive = None
    global____ACM_id, global___CTRL_id = None, None
    global________x5 = None
    global_CTRL_theta_d, global_OB_theta_d = None, None
    global_TL = None

    for ii in range(0, 10):
        """perform animation step"""
        control_times, numba__waveforms_dict = \
            ACMSimPyWrapper(numba__scope_dict,
                        t0=ii*TIME_SLICE, TIME=TIME_SLICE, 
                        ACM=ACM,
                        CTRL=CTRL,
                        reg_id=reg_id,
                        reg_iq=reg_iq,
                        reg_speed=reg_speed,
                        OB=OB,
                        HUMAN=HUMAN)
        cmd_rpm, ACM_speed, OB_speed = numba__waveforms_dict[r'Speed [rpm]']
        x5, KActive                  = numba__waveforms_dict[r'K_{\rm Active} [A]']
        ACM_id, CTRL_id, cmd_id      = numba__waveforms_dict[r'$d$-axis current [A]']
        _, CTRL_theta_d, OB_theta_d  = numba__waveforms_dict[r'Position [rad]']
        TL,                          = numba__waveforms_dict[r'Load torque [Nm]']

        def save_to_global(_global, _local):
            return _local if _global is None else np.append(_global, _local)    
        global_ACM_speed = save_to_global(global_ACM_speed, ACM_speed)
        global__OB_speed = save_to_global(global__OB_speed,  OB_speed)
        global________x5 = save_to_global(global________x5,        x5)
        global___KActive = save_to_global(global___KActive,   KActive)
        global____ACM_id = save_to_global(global____ACM_id,    ACM_id)
        global___CTRL_id = save_to_global(global___CTRL_id,   CTRL_id)
        global_CTRL_theta_d = save_to_global(global_CTRL_theta_d, CTRL_theta_d)
        global_OB_theta_d = save_to_global(global_OB_theta_d, OB_theta_d)
        global_TL        = save_to_global(global_TL, TL)

        print(ACM.KActive, 'Wb')

        # for k,v in numba__waveforms_dict.items():
        #     print(k, np.shape(v))

        # print(len(global_speed), end='|')
        # print(max(global_speed), end='|')
        # print(len(speed), end='|')
        # print(max(speed))
        # print()
        # break

    plt.figure(figsize=(15,4))
    plt.plot(global_ACM_speed); plt.plot(global__OB_speed)

    plt.figure(figsize=(15,4)); plt.ylim([-1e-1, 1e-1])
    plt.plot( (global_ACM_speed - global__OB_speed) ) # [2000:5000]

    plt.figure(figsize=(15,4))
    plt.plot( global________x5 ); plt.plot( global___KActive )

    plt.figure(figsize=(15,4))
    plt.plot( global____ACM_id ); plt.plot( global___CTRL_id )

    plt.figure(figsize=(15,4))
    plt.plot( global_CTRL_theta_d ); plt.plot( global_OB_theta_d )

    plt.figure(figsize=(15,4))
    plt.plot( np.sin(global_CTRL_theta_d - global_OB_theta_d) )

    plt.figure(figsize=(15,4))
    plt.plot( global_TL )

    print(OB.ell1, OB.ell2, OB.ell3, OB.ell4)



# %%
