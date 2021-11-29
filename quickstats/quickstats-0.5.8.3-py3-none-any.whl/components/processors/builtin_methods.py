BUILTIN_METHODS = \
{
    "Namespace_ROOT_VecOps": "using namespace ROOT::VecOps;", 
    "Namespace_ROOT_Math": "using namespace ROOT::Math;",
    "SizeOf" : "template<typename T>\n"
               "auto SizeOf(T vec)\n"
               "{return vec.size();}",
    "CosineThetaStar": "template<typename T1, typename T2>\n"
                       "auto CosineThetaStar(T1 P1, T2 P2){\n"
                       "auto P12 = P1 + P2;\n"
                       "double P1_plus  = (P1.E() + P1.Pz())/1.41421356;\n"
                       "double P2_plus  = (P2.E() + P2.Pz())/1.41421356;\n"
                       "double P1_minus = (P1.E() - P1.Pz())/1.41421356;\n"
                       "double P2_minus = (P2.E() - P2.Pz())/1.41421356;\n"
                       "double M12_squared = pow(P12.M(),2);\n"
                       "double PT12_squared = pow(P12.Pt(),2);\n"
                       "return 2*((P1_plus*P2_minus -P1_minus*P2_plus)/"
                       "sqrt(M12_squared*(M12_squared+PT12_squared)))*(P12.Pz()/abs(P12.Pz()));}\n"
}