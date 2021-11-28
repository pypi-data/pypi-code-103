import re

from tableX import table2json
#
if __name__ == '__main__':
    text = ["""
    <table class="details" style="margin-top: 8px;">
              <thead>
                  <tr class="top">
                    
                      <th rowspan="2">    <a href="?s=partNumber">
AOS 产品型号</a></th>
                      <th rowspan="2">    <a href="?s=description">
描述</a></th>
                      <th rowspan="2">      <a class="asc" href="?s=-statusId">
Status</a></th>
                      <th class="wrap" rowspan="3">    <a href="?s=recommendedReplacement">
Recommended<br>Replacement</a></th>
                      <th class="wrap" rowspan="4">    <a href="?s=picType">
Type</a></th>
                      <th class="wrap" rowspan="5">    <a href="?s=schottky">
Integrated Schottky</a></th>
                      <th rowspan="2">    <a href="?s=pgood">
PGOOD</a></th>
                      <th class="wrap" rowspan="2">    <a href="?s=soft_start">
Soft Start</a></th>
                      <th class="wrap" rowspan="2">    <a href="?s=package">
Package</a></th>
                      <th class="wrap">    <a href="?s=min_vin">
Min V (in)</a></th>
                      <th class="wrap">    <a href="?s=max_vin">
Max V (in)</a></th>
                      <th class="wrap">    <a href="?s=max_iout">
Max I (out)</a></th>
                      <th class="wrap">    <a href="?s=min_vout">
Min V (out)</a></th>
                      <th class="wrap">    <a href="?s=max_vout">
Max V (out)</a></th>
                      <th class="wrap last">    <a href="?s=op_freq">
Operating Freq</a></th>
                  </tr>
                  <tr>
                      <th>V</th>
                      <th>V</th>
                      <th>A</th>
                      <th>V</th>
                      <th>V</th>
                      <th class="last">KHz</th>
                  </tr>
              </thead>
              <tbody>


                <tr>
  <td class="left first oneline">
    <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3011PI" class="info" rel="menu-0">AOZ3011PI</a>
<div id="menu-0" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3011PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
  </td>
                    <td class="wrap">3A Sync Buck with External Soft-Start</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6663DI, AOZ6683CI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3013PI" class="info" rel="menu-1">AOZ3013PI</a>
<div id="menu-1" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3013PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOZ3013PI.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A Sync Buck with External Soft-Start</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6663DI, AOZ6683CI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3015AI" class="info" rel="menu-2">AOZ3015AI</a>
<div id="menu-2" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3015AI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A EZBuck Regulator with Light Load Mode</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6663DI, AOZ6683CI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">Internal - 5ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3015PI" class="info" rel="menu-3">AOZ3015PI</a>
<div id="menu-3" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3015PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A EZBuck Regulator with Light Load Mode</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6663DI, AOZ6683CI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">Internal - 5ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3017PI" class="info" rel="menu-4">AOZ3017PI</a>
<div id="menu-4" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3017PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">4A Sync Buck with External Soft-Start</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6604PI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>4</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3018PI" class="info" rel="menu-5">AOZ3018PI</a>
<div id="menu-5" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3018PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">5A Sync Buck with External Soft-Start</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6605PI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>5</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3024PI" class="info" rel="menu-6">AOZ3024PI</a>
<div id="menu-6" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3024PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A Buck Regulator</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">-</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>Yes</td>
                    <td class="wrap">Internal - 4.5ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3046PI" class="info" rel="menu-7">AOZ3046PI</a>
<div id="menu-7" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3046PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">4A EZBuck Regulator</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6604PI</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">Internal - 4ms</td>
                    <td class="wrap">SO-8</td>
                    <td>7.5</td>
                    <td>18</td>
                    <td>4</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ3101DI" class="info" rel="menu-8">AOZ3101DI</a>
<div id="menu-8" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ3101DI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/DFN3x3B_8L_EP1_P.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3x3B_8L_EP1_P.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">2A Regulator with Internal Soft-Start</td>
                    <td class="wrap">Not For New Designs</td>
                    <td class="wrap">AOZ6662DI, AOZ6682CI</td>
                    <td>Sync</td>
                    <td>No</td>
                    <td>No</td>
                    <td class="wrap">Internal - 1.5ms</td>
                    <td class="wrap">DFN3x3B-8L</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>2</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1017AI" class="info" rel="menu-9">AOZ1017AI</a>
<div id="menu-9" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1017AI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          <li><a target="_blank" href="/res/evalboards/AOZ1017AI.pdf">Eval Board Notes</a></li>
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOZ1017AI.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A EZBuck Regulator</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Non-Sync</td>
                    <td>No</td>
                    <td>-</td>
                    <td class="wrap">Internal - 2.2ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>16</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>16</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1019AI" class="info" rel="menu-10">AOZ1019AI</a>
<div id="menu-10" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1019AI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          <li><a target="_blank" href="/res/evalboards/AOZ1019AI.pdf">Eval Board Notes</a></li>
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOZ1019AI.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">2A EZBuck Regulator</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Non-Sync</td>
                    <td>No</td>
                    <td>-</td>
                    <td class="wrap">Internal - 4ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>16</td>
                    <td>2</td>
                    <td>0.8</td>
                    <td>15</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1020AI" class="info" rel="menu-11">AOZ1020AI</a>
<div id="menu-11" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1020AI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          <li><a target="_blank" href="/res/evalboards/AOZ1020AI.pdf">Eval Board Notes</a></li>
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">2A EZBuck Regulator</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>Yes</td>
                    <td class="wrap">Internal - 4ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>16</td>
                    <td>2</td>
                    <td>0.8</td>
                    <td>15</td>
                    <td>500</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1033AI" class="info" rel="menu-12">AOZ1033AI</a>
<div id="menu-12" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1033AI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A EZBuck Regulator with Light Load Mode</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">Internal - 2.5ms</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>17</td>
                    <td>600</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1052PI" class="info" rel="menu-13">AOZ1052PI</a>
<div id="menu-13" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1052PI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/SO8_EP1.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8_EP1.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">4A Sync Buck with External Soft-Start</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Sync</td>
                    <td>-</td>
                    <td>No</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>18</td>
                    <td>4</td>
                    <td>0.8</td>
                    <td>15.3</td>
                    <td>450</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1057AIL" class="info" rel="menu-14">AOZ1057AIL</a>
<div id="menu-14" class="overlay">
    <div class="content">
        <ul class="documents">
          
            
          
          <li><a target="_blank" href="/res/packaging_information/SO8.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/SO8.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">3A EZBuck Regulator</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Non-Sync</td>
                    <td>No</td>
                    <td>-</td>
                    <td class="wrap">External - Programmable</td>
                    <td class="wrap">SO-8</td>
                    <td>4.5</td>
                    <td>16</td>
                    <td>3</td>
                    <td>0.8</td>
                    <td>16</td>
                    <td>340</td>
                </tr>


                <tr>
    <td class="left first oneline">
      <a href="/zh/products/power-ics/ezbuck-dc-dc-buck-regulators/AOZ1083CI" class="info" rel="menu-15">AOZ1083CI</a>
<div id="menu-15" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOZ1083CI.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/TSOP6.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TSOP6.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
                    <td class="wrap">1.2A Buck LED Driver</td>
                    <td class="wrap">Obsolete</td>
                    <td class="wrap">-</td>
                    <td>Non-Sync</td>
                    <td>No</td>
                    <td>-</td>
                    <td class="wrap">Internal - 0.4ms</td>
                    <td class="wrap">TSOP-6</td>
                    <td>3</td>
                    <td>26</td>
                    <td>1.2</td>
                    <td>0.28</td>
                    <td>23</td>
                    <td>1,500</td>
                </tr>

            </tbody>
        </table>"""]
    json = table2json.table2json(text, [0, 1, 2], [3], 2,1)
    # json = table2json.table2jsonStr(text, [0, 1, 2], [3])
    print(json)

