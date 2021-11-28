"""Plot to test mouse events"""
import matplotlib.pyplot as plt
import numpy as np
import mpld3, mpld3.plugins as plugins

random_x = [0.037984906849671374, 0.5880357008425118, 0.47736125281329767, 0.010304252492200239, 0.35796828706754447, 0.23109561146897417, 0.8631302372372742, 0.13444834717909937, 0.5056397861230668, 0.024528122585731227, 0.5372864367524129, 0.058924358084960105, 0.2631680487666277, 0.6814702489039445, 0.11034531955119298, 0.4299675665498215, 0.0631667742233506, 0.10316683922592784, 0.19692341232102673, 0.3353885162702046, 0.9152346663864552, 0.11198196158519313, 0.8799975132010748, 0.7960293867412321, 0.9295540537314296, 0.3958725715755408, 0.035255608999481325, 0.0054287463568508665, 0.7517682039494487, 0.5385301522985431, 0.30208986270541394, 0.18467091269007285, 0.6218806664279364, 0.6877500188861776, 0.546811722807477, 0.3140703221286578, 0.989234786215092, 0.41888939305739137, 0.33314667920077945, 0.345491646148014, 0.6755566139855378, 0.955322435733609, 0.8673785689480379, 0.31111198199765544, 0.025862944203813854, 0.8359219522933756, 0.47622910878639735, 0.41210620978548884, 0.9941003162789824, 0.17550975368294885]

random_y = [0.45402157945566135, 0.16864929140625728, 0.5111076100380816, 0.41026380763175285, 0.3971396415356726, 0.5812543312682149, 0.32639546372485917, 0.9794503784387796, 0.5393582722581963, 0.49968700001151, 0.13357111737556648, 0.9563556753027254, 0.3734508445972159, 0.3644342446362956, 0.32761929072245144, 0.12402062932059743, 0.872807150749212, 0.844186788071371, 0.37936922460029165, 0.18200905951561552, 0.779773690605089, 0.5963142521743686, 0.5522500805846032, 0.051824827070525936, 0.06473610523722362, 0.04522228562224817, 0.8933476377595784, 0.4748328124416784, 0.1520450481465807, 0.8200682148351869, 0.4581154746719148, 0.8991510174008752, 0.33249486911216286, 0.8320338099832485, 0.8549033533974582, 0.16978769781277792, 0.2315533412315509, 0.037676231224115564, 0.3719505107401978, 0.37076483058680243, 0.774208501240394, 0.5930470039583583, 0.15492566806379704, 0.43094178354006774, 0.6257337718514595, 0.5325297011058135, 0.5360600203459467, 0.43296583733953886, 0.35999596815150825, 0.43044674586992837] 


class ClickInfo(plugins.PluginBase):
    """Plugin for getting info on click"""

    JAVASCRIPT = """
    mpld3.register_plugin("clickinfo", ClickInfo);
    ClickInfo.prototype = Object.create(mpld3.Plugin.prototype);
    ClickInfo.prototype.constructor = ClickInfo;
    ClickInfo.prototype.requiredProps = ["id"];
    function ClickInfo(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    ClickInfo.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id);
        obj.elements().on("click",
                          function(d, i){alert("clicked on points[" + i + "]");});
    }
    """
    def __init__(self, points):
        self.dict_ = {"type": "clickinfo",
                      "id": mpld3.utils.get_id(points)}

def create_plot():
    fig, ax = plt.subplots()
    points = ax.scatter(random_x, random_y, 
                        s=500, alpha=0.3)

    plugins.clear(fig)
    ax.set_title('Click info', size=14)
    plugins.connect(fig, plugins.Reset(), plugins.Zoom(), ClickInfo(points))
    return fig


def test_mouse_events():
    fig = create_plot()
    html = mpld3.fig_to_html(fig)
    plt.close(fig)


if __name__ == "__main__":
    mpld3.show(create_plot())
