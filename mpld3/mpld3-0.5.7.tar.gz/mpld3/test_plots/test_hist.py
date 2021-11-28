"""Plot to test polygons"""
import matplotlib.pyplot as plt
import numpy as np
import mpld3

random_data =[1.6088185574147464,
 -0.6865771485141146,
 -1.6136369485782012,
 -0.3392658435669958,
 1.4387492600538156,
 -1.7432591997998272,
 -1.1082471324814325,
 1.6589479820353064,
 -0.13049658094505667,
 1.2576658123386033,
 1.7963480416316446,
 1.1430405041422613,
 -0.4472323843738978,
 -0.6550491457750972,
 0.9587514144130824,
 -0.3395959055304727,
 2.1602167699502393,
 -1.295552001830939,
 -0.8089544706632718,
 -1.059898488934211,
 -1.49840844285432,
 -0.28948812041181315,
 1.288458860066516,
 -0.045776284512724794,
 -0.17603684344978587,
 0.32877358888432034,
 0.541536214412118,
 -0.24433774008617837,
 0.601868139626899,
 -0.28906442847885255,
 -1.1151998316860108,
 1.8356164778710642,
 -0.7103164540816693,
 1.3015278551091776,
 1.3298491664708991,
 0.039883192975611916,
 -1.0335566237806555,
 -0.6252207577843318,
 1.3298538422237947,
 -0.4617915164308597,
 0.09126263830080214,
 -0.48477949570239454,
 0.26803781904185003,
 -0.20182850148656825,
 0.7972021848483254,
 -0.8282312719003075,
 1.3641371074485997,
 0.24341631560423083,
 1.3115542891128071,
 0.06872710320774854,
 -0.01672072283950251,
 1.4422119012100003,
 0.2528618829661779,
 0.9616468054908228,
 0.986887707014175,
 3.0258489983553383,
 -1.6816251031482299,
 0.2950440044644165,
 -1.8763902132612298,
 0.7624976458741685,
 -0.037227217772358524,
 -0.25902776727215787,
 -0.5417080779000882,
 0.04284672907498912,
 -0.13718254382313286,
 0.3569275300145882,
 -0.10662334822352819,
 -0.20642815589262306,
 0.5450968108182405,
 -0.062190347435352254,
 -0.5304976410890131,
 0.11496067466178328,
 -1.0368841824181443,
 0.2503567167261422,
 -0.6341715118680747,
 1.25978863474973,
 2.0435613495865774,
 0.7410644160060791,
 0.2528301815581853,
 -1.538978431967695,
 -0.2206925312874959,
 0.29577840638693786,
 -0.8990147300635852,
 1.6909167851741114,
 -0.10736814113290882,
 1.8031628709576693,
 -0.5003026573281728,
 1.1236234943942045,
 -0.47104101684459104,
 -0.1923028862063637,
 -1.8800925078391912,
 -0.42312802123630855,
 0.038490251876292195,
 -1.0867893036291791,
 0.0743810621308829,
 -0.47909429145664206,
 0.373368117914869,
 1.534135149819737,
 0.5245494022834717,
 -0.6984090785788215,
 1.4427674444634822,
 -2.4922813329332545,
 -1.055953770682888,
 1.878609211373456,
 -0.5908328730082637,
 -1.857048057759057,
 1.4786935759559536,
 -1.28181489277262,
 0.5157675445982315,
 1.7195808917236108,
 -0.38440912454122145,
 0.8797574085810836,
 1.676239682331843,
 -0.45240799723213676,
 0.2802772191700505,
 0.3309554099198398,
 0.38338570346598083,
 -0.5034539695574349,
 0.37627553203847464,
 0.8519091363726424,
 0.5383015788727779,
 1.1096325663839426,
 -0.12052436986058586,
 1.3140245276665212,
 -1.6530681149038304,
 -0.25888841120633477,
 -0.16350037559227912,
 1.8474504533549003,
 2.1263366425570833,
 -2.4710734105428376,
 0.8718448474019873,
 0.033821899566860276,
 0.8085927980513511,
 1.2601667298400134,
 -0.0996093564508275,
 -0.11628042414484877,
 -0.30729165471241415,
 -1.0341851401416844,
 -0.1504103660115286,
 2.350913034096008,
 1.3196851342214893,
 -1.1347512591503675,
 -0.8734170695785559,
 -0.7056234969058184,
 -0.9103649939672405,
 -0.2002480157061158,
 -0.10831954230789262,
 -0.007850307426785403,
 1.6674772351633886,
 -0.9856132076907798,
 -1.0434180080976176,
 -0.7030186659655316,
 1.2277115608023585,
 0.898005768601088,
 1.6274643029829878,
 -0.08320385964386205,
 -1.0356424576358394,
 -1.9123345323284744,
 -0.4955321187542757,
 0.4408707747503287,
 -0.5249733215919139,
 -0.10939488654798794,
 0.13553860026767425,
 -0.044305821603251534,
 -0.7159385332949207,
 0.1337325665608888,
 0.4342004517486429,
 0.9866633375956508,
 -0.4653819475223896,
 0.5295495127235367,
 0.3247402423321501,
 -0.172493356502056,
 -0.2537971923947709,
 -1.1923561470207291,
 -1.377995450737569,
 0.3296828119945463,
 1.140535300240797,
 -1.819560409414942,
 -0.6162187522864669,
 -0.18242365258955792,
 1.239049703542898,
 0.8643784466658591,
 -0.08538549494480388,
 0.5881499817461358,
 -0.057619619123778186,
 -1.2707376565079977,
 -1.3977605070083239,
 0.09574346340872995,
 0.23884692218285297,
 0.4029036841565875,
 -0.9400128968346682,
 0.42326857325407236,
 0.5648516210728396,
 -1.3651144362578458,
 0.898288264619132,
 0.4468229076264855,
 0.30232587578398423,
 0.19062463725075862,
 -1.5821141982099332,
 0.3138327015600902,
 0.9040160345128291,
 -0.7917206940604362,
 1.1607614234184414,
 0.5766896888158412,
 -1.043476800149341,
 -0.8052738529239508,
 -0.7951554215524248,
 0.2232526689122744,
 1.0188389616353848,
 0.46285935979550724,
 0.7530817165084904,
 0.5807926089444349,
 0.951763854573985,
 0.7779599385764743,
 0.9504812904388322,
 -0.7516979999357363,
 -0.464067808534713,
 -0.16380932224811862,
 -0.6864196976240141,
 0.2455737023517738,
 -0.7348409615713362,
 0.05758310026884851,
 0.553063059550217,
 0.048544227898844196,
 -1.0605120659188905,
 -1.8920278387522278,
 -0.658061996299685,
 1.9990327483568218,
 1.6828958494813993,
 -0.21219138503074944,
 2.028293015011859,
 0.25073190254352673,
 -1.0099002205136993,
 -0.989634542442095,
 -1.8160059730296367,
 1.0035962608820848,
 0.28918067305350814,
 0.8361827598492787,
 0.4089949457053751,
 0.7185549408083635,
 2.0949185611609504,
 0.3971691690456786,
 0.03746589256624114,
 -1.0529324976132892,
 0.27839584072377,
 0.33365799579104055,
 0.6964644795032722,
 0.2714256509423176,
 1.8044818571556243,
 -0.014691244797071097,
 -1.7387991143638268,
 0.9914453084472065,
 0.1180319411371459,
 1.0937264804224316,
 0.9364065911889146,
 0.2519024816944673,
 0.4021939664482127,
 -0.5028089868006651,
 0.0388962526649951,
 1.2030710009668146,
 0.3840680927370874,
 1.313243414710453,
 -1.3349241399871241,
 -0.8300588871468806,
 -2.03421982770625,
 0.32842532365118315,
 -1.89901585610299,
 0.32970239917356436,
 0.8533773496260463,
 1.5693173384939607,
 -0.16435860939222388,
 2.017424616530559,
 -0.8717492192875496,
 -0.9205396786640737,
 -0.27997075405423666,
 0.8765383654317493,
 -1.4259702572640618,
 -1.8306588867848146,
 -0.5533842251456949,
 -0.21735511572955551,
 0.6382620822372181,
 0.2697140871204187,
 -0.31404218568267667,
 0.9316811764590066,
 -2.0667451860587622,
 1.697252913678298,
 1.1140315605316327,
 -0.009728699147934545,
 0.44189013768413343,
 -2.091495320531901,
 -1.2308916385480955,
 1.03026426888392,
 0.6627516925501729,
 0.817194063857429,
 -0.09226755901979303,
 -0.7362235501925207,
 0.04861987725869331,
 -1.0870115812073784,
 -0.2775709188139612,
 -0.29904174027582114,
 -0.24527232361588672,
 0.04773573775114175,
 -1.0677960401047661,
 0.8530438179721761,
 0.2897513718951045,
 1.6199955149540348,
 1.5104979796348013,
 -0.41309856833836495,
 -0.5872239669415509,
 -0.7130500893351722,
 -0.3365322853411775,
 1.489694182097857,
 0.7557971239310557,
 0.03497335646263285,
 0.16339919779924367,
 -1.3428139079259165,
 0.023618745777960616,
 0.33455741995750904,
 -0.2773459662635286,
 -1.2584353309363554,
 -0.35231067826871987,
 -0.46865158640324983,
 1.3217355404117228,
 0.8399869535160688,
 -1.2162406398696064,
 -0.6350983093634716,
 -0.4321460762899319,
 -0.08527475307077167,
 -0.45399095073088236,
 -0.8177666488623411,
 0.5418295821038207,
 -0.6897257208335155,
 1.9658831505381047,
 -0.5284782606870327,
 -0.10594382890096236,
 0.24217314486549776,
 -0.5460335643043203,
 -1.3520718886259466,
 -0.15218616373826915,
 -0.1805423354466487,
 0.8415580222953368,
 -0.879646055763199,
 -2.714005962761264,
 -0.9585563813890874,
 0.2388829833649452,
 -0.0018540203771739466,
 0.644323760922803,
 -1.1416656024255565,
 0.36059299815837736,
 -0.3405770278729513,
 -0.3060403596539795,
 -0.17120569365180208,
 -0.8850411936131686,
 0.4314129582862788,
 0.5069769759851513,
 0.19882895186884772,
 0.540960911738796,
 0.7150512811896927,
 0.21539364433513875,
 -0.14880865724659603,
 -0.970486940943654,
 1.1256175047352606,
 -0.12226332002538869,
 -1.205309174534235,
 -0.3261500143680117,
 -1.0554032200494499,
 -0.2573819201081508,
 -0.390669301965708,
 0.21584409681938665,
 0.6619000008876321,
 0.6672312131593522,
 2.614110705304245,
 2.3277918581365675,
 -0.13865785865596422,
 1.6795442426292522,
 -0.5908374267513135,
 -1.909847525232184,
 1.3472993801655453,
 -0.2745189218380143,
 -2.3547825709264467,
 -0.7955575743254125,
 0.7923489976326644,
 0.29674299018855055,
 0.1035247640421333,
 -0.9888059458106297,
 -1.8395994751705467,
 0.12825918570249015,
 -0.19293516184610582,
 -1.3489737673445084,
 1.2327432621197973,
 0.2221064625924095,
 0.7610779332844465,
 -1.0239691289648312,
 -0.1565823811347759,
 1.4533257293286792,
 -0.11013059558922982,
 -0.5155256072913103,
 -0.3205426002771927,
 0.3539596160876571,
 -0.9638065147736249,
 0.09279011027491435,
 -0.7071397022232381,
 1.5997327256021119,
 -1.584187374648889,
 -1.1156709280409551,
 0.4340149441755118,
 -0.7083424606262801,
 1.030159256692143,
 -0.03902523555766703,
 0.31686738030088063,
 -1.468287742606628,
 -0.4249646873881102,
 -2.132444540031783,
 1.3759071574719794,
 0.5604989649036469,
 -0.6391100435482325,
 -0.37883211235704667,
 0.27634895124008235,
 0.44186696190782637,
 -1.1996295740986185,
 -0.6313435996243602,
 0.15195351822228517,
 -1.0084179828289148,
 -0.28009382621337053,
 -1.2916745021370748,
 0.8031447665256342,
 1.5448416345166864,
 0.5650167050374918,
 -0.22692657044538106,
 0.4657098245292046,
 -0.731737283783585,
 0.29015243544801783,
 -0.2568729575658686,
 0.6462038763805821,
 0.03227524011079943,
 -0.11612118017364606,
 -0.6868112224881517,
 -0.2647807973589498,
 0.9670076443564106,
 1.4042294708834777,
 0.46222355841059154,
 -0.16896499680869345,
 0.5194292707657132,
 0.049028237544197155,
 0.23541854435222753,
 1.5963045842316512,
 -0.8835656730136358,
 -1.5303883709287394,
 2.14927118430476,
 0.651015648751183,
 -0.38864585624570913,
 0.737489494433733,
 0.1453528158913322,
 -1.598180855169015,
 0.5275094033382759,
 1.0127561937365395,
 -0.3933309736771058,
 -1.4863368389917533,
 -0.9483466608061892,
 -0.9887848826467983,
 -0.4844687388626192,
 0.6588653188263609,
 -1.9217465388124388,
 -1.8233868910754438,
 -0.5060394534743602,
 0.08339289479665324,
 1.6073503691251432,
 -1.512588432746404,
 -0.8384147514383815,
 -1.4945981086734483,
 1.001356338889699,
 -1.4193317466315716,
 -0.9826214973907532,
 -1.0318404168530542,
 -0.7855313870405117,
 0.019212819799928733,
 -0.3921471487430196,
 1.1804152033180966,
 -0.4999154374050257,
 -0.4554909566262925,
 0.1749698807335615,
 2.0540590495754274,
 1.2606061405374105,
 -1.7699196258937016,
 -0.6398880181586967,
 0.24074296988586688,
 1.6366265129160817,
 -0.11216944021389891,
 0.05076596701734716,
 -1.1415712976136028,
 -1.1648288165948886,
 0.45647427435363913,
 0.09807293341608687,
 -0.3118362702922066,
 0.10678521064476658,
 -0.038455686391581,
 -0.22007985721261505,
 -0.5635347991217103,
 0.2941046121794234,
 0.31455015119383994]
 
def create_plot():
    fig, ax = plt.subplots()
    ax.grid(color='gray')

    x = np.array(random_data )
    ax.hist(x, 30, fc='blue', alpha=0.5)

    ax.xaxis.set_major_locator(plt.NullLocator())

    return fig


def test_hist():
    fig = create_plot()
    html = mpld3.fig_to_html(fig)
    plt.close(fig)


if __name__ == "__main__":
    mpld3.show(create_plot())
