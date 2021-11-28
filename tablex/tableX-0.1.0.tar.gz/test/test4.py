from tableX import table2json

if __name__ == '__main__':
    text = [
        ''' 
    <table class="details">
        <thead>
            <tr class="top">
                
                <th rowspan="3">    <a href="?s=partNumber">
Part Number</a></th>
                <th rowspan="3">      <a class="asc" href="?s=-statusId">
Status</a></th>
                <th rowspan="3">    <a href="?s=package">
Package</a></th>
                <th rowspan="3">    <a href="?s=productType">
Configuration</a></th>
                <th class="wrap" rowspan="2">    <a href="?s=vce_max">
V<span class="subS">CE</span> (max)</a></th>
                <th class="wrap" colspan="2">I<span class="subS">C</span> (max)</th>
                <th class="wrap" rowspan="2">    <a href="?s=vce">
V<span class="subS">CE(sat)</span><br>(typ)</a></th>
                <th class="wrap" rowspan="2">    <a href="?s=e_on">
E<span class="subS">ON</span></a></th>
                <th class="wrap" rowspan="2">    <a href="?s=e_off">
E<span class="subS">OFF</span></a></th>
                  <th class="wrap" rowspan="2">    <a href="?s=qg">
Q<span class="subS">g</span></a></th>
                  <th class="wrap" rowspan="2">    <a href="?s=vf">
V<span class="subS">F</span></a></th>
                  <th class="wrap" rowspan="2">    <a href="?s=qrr">
Q<span class="subS">rr</span></a></th>
                  <th class="wrap last" rowspan="2">    <a href="?s=irm">
I<span class="subS">rm</span></a></th>
            </tr>
            <tr>
                <th>    <a href="?s=ic_max_25">
25°C</a></th>
                <th>    <a href="?s=ic_max_100">
100°C</a></th>
            </tr>
            <tr>
                <th>V</th>
                
                <th>A</th>
                <th>A</th>
                
                <th>V</th>
                <th>mJ</th>
                <th>mJ</th>
                <th>nC</th>
                  <th>V</th>
                  <th>µC</th>
                  <th>A</th>
      </tr>
        </thead>
        <tbody>
            <tr>
  <td class="left first oneline">
    <a href="/zh/products/igbts/igbt_ap_diode/AOTF15B65M3" class="info" rel="menu-0">AOTF15B65M3</a>
<div id="menu-0" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF15B65M3.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF15B65M3.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF15B65M3.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
  </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>30</td>
              <td>15</td>
              <td>1.95</td>
              <td>0.28</td>
              <td>0.19</td>
              <td>25.4</td>
                <td>1.9</td>
                <td>0.4</td>
                <td>3.8</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF15B65MQ1" class="info" rel="menu-1">AOTF15B65MQ1</a>
<div id="menu-1" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF15B65MQ1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF15B65MQ1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF15B65MQ1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>30</td>
              <td>15</td>
              <td>1.7</td>
              <td>0.29</td>
              <td>0.2</td>
              <td>32</td>
                <td>1.65</td>
                <td>0.24</td>
                <td>3.9</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF20B65LN2" class="info" rel="menu-2">AOTF20B65LN2</a>
<div id="menu-2" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF20B65LN2.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF20B65LN2.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF20B65LN2.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>40</td>
              <td>20</td>
              <td>1.54</td>
              <td>0.45</td>
              <td>0.26</td>
              <td>52</td>
                <td>0.6</td>
                <td>0.6</td>
                <td>5.4</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF20B65M1" class="info" rel="menu-3">AOTF20B65M1</a>
<div id="menu-3" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF20B65M1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF20B65M1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF20B65M1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>40</td>
              <td>20</td>
              <td>1.7</td>
              <td>0.47</td>
              <td>0.27</td>
              <td>46</td>
                <td>1.66</td>
                <td>0.8</td>
                <td>5.2</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF20B65M2" class="info" rel="menu-4">AOTF20B65M2</a>
<div id="menu-4" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF20B65M2.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF20B65M2.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF20B65M2.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>40</td>
              <td>20</td>
              <td>1.7</td>
              <td>0.58</td>
              <td>0.28</td>
              <td>46</td>
                <td>1.56</td>
                <td>0.8</td>
                <td>5.6</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF5B60D" class="info" rel="menu-5">AOTF5B60D</a>
<div id="menu-5" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF5B60D.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF5B60D.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>600</td>
              <td>10</td>
              <td>5</td>
              <td>1.55</td>
              <td>0.14</td>
              <td>0.04</td>
              <td>9.4</td>
                <td>1.46</td>
                <td>0.23</td>
                <td>4.4</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF5B65M1" class="info" rel="menu-6">AOTF5B65M1</a>
<div id="menu-6" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF5B65M1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOTF5B65M1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF5B65M1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>10</td>
              <td>5</td>
              <td>1.57</td>
              <td>0.08</td>
              <td>0.07</td>
              <td>14</td>
                <td>1.8</td>
                <td>0.24</td>
                <td>2.78</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOTF5B65M2" class="info" rel="menu-7">AOTF5B65M2</a>
<div id="menu-7" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOTF5B65M2.pdf">Datasheet</a></li>
          
          <li><a target="_blank" href="/res/packaging_information/TO220F.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO220F.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOTF5B65M2.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Full Production</td>
              <td>TO220F</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>10</td>
              <td>5</td>
              <td>1.57</td>
              <td>0.08</td>
              <td>0.07</td>
              <td>14</td>
                <td>1.48</td>
                <td>0.27</td>
                <td>3.5</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOB5B60D" class="info" rel="menu-8">AOB5B60D</a>
<div id="menu-8" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOB5B60D.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOB5B60D.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO263.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO263.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOB5B60D.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO263</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>600</td>
              <td>10</td>
              <td>5</td>
              <td>1.55</td>
              <td>0.14</td>
              <td>0.04</td>
              <td>9.4</td>
                <td>1.46</td>
                <td>0.23</td>
                <td>4.4</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOD5B65M1H" class="info" rel="menu-9">AOD5B65M1H</a>
<div id="menu-9" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOD5B65M1H.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOD5B65M1H.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO252.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO252.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOD5B65M1H.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO252</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>650</td>
              <td>10</td>
              <td>5</td>
              <td>1.57</td>
              <td>0.08</td>
              <td>0.07</td>
              <td>14</td>
                <td>1.8</td>
                <td>0.24</td>
                <td>2.78</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOD6B60M1" class="info" rel="menu-10">AOD6B60M1</a>
<div id="menu-10" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOD6B60M1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOD6B60M1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO252.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO252.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOD6B60M1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO252</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>600</td>
              <td>12</td>
              <td>6</td>
              <td>1.7</td>
              <td>0.12</td>
              <td>0.09</td>
              <td>14</td>
                <td>1.45</td>
                <td>0.15</td>
                <td>3.5</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOK10B60D" class="info" rel="menu-11">AOK10B60D</a>
<div id="menu-11" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOK10B60D.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOK10B60D.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO247.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO247.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOK10B60D.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO247</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>600</td>
              <td>20</td>
              <td>10</td>
              <td>1.53</td>
              <td>0.32</td>
              <td>0.12</td>
              <td>17.4</td>
                <td>1.52</td>
                <td>0.25</td>
                <td>5</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOK15B60D" class="info" rel="menu-12">AOK15B60D</a>
<div id="menu-12" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOK15B60D.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOK15B60D.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO247.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO247.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOK15B60D.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO247</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>600</td>
              <td>30</td>
              <td>15</td>
              <td>1.6</td>
              <td>0.51</td>
              <td>0.11</td>
              <td>25.4</td>
                <td>1.43</td>
                <td>0.48</td>
                <td>5.8</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOK20B120D1" class="info" rel="menu-13">AOK20B120D1</a>
<div id="menu-13" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOK20B120D1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOK20B120D1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO247.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO247.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOK20B120D1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO247</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>1,200</td>
              <td>40</td>
              <td>20</td>
              <td>1.54</td>
              <td>-</td>
              <td>0.94</td>
              <td>67.5</td>
                <td>1.33</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOK20B120E1" class="info" rel="menu-14">AOK20B120E1</a>
<div id="menu-14" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOK20B120E1.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOK20B120E1.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO247.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO247.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOK20B120E1.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO247</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>1,200</td>
              <td>40</td>
              <td>20</td>
              <td>1.68</td>
              <td>-</td>
              <td>0.83</td>
              <td>60.5</td>
                <td>1.6</td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/igbts/igbt_ap_diode/AOK20B120E2" class="info" rel="menu-15">AOK20B120E2</a>
<div id="menu-15" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOK20B120E2.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOK20B120E2.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO247.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO247.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOK20B120E2.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>
              <td class="wrap">Not For New Designs</td>
              <td>TO247</td>
              <td>IGBT with Anti-Parallel Diode</td>
              <td>1,200</td>
              <td>40</td>
              <td>20</td>
              <td>1.75</td>
              <td>-</td>
              <td>0.82</td>
              <td>53.5</td>
                <td>1.6</td>
                <td>-</td>
                <td>-</td>
            </tr>
        </tbody>
    </table>
    ''']

    json = table2json.table2json(text, [0], [], 2,1)
    print(json)
