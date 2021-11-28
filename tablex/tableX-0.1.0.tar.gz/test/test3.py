from tableX import table2json

if __name__ == '__main__':
    text = [
        ''' 
       <table class="details">
        <thead>
            <tr class="top">
                
                <th rowspan="3">Part Number</th>
                <th rowspan="3">Status</th>
                <th class="wrap" rowspan="3">Recommended<br>Replacement</th>
                <th rowspan="3">Package</th>
                <th rowspan="3">Configuration</th>
                <th rowspan="3">Polarity</th>
                <th class="wrap" rowspan="2">Vds</th>
                <th class="wrap" rowspan="2">Vgs</th>
                    <th class="wrap">Id</th>
                    <th class="wrap">Pd</th>
                <th class="wrap" colspan="4">Rds (on) mΩ max</th>
                <th class="wrap last" rowspan="3">Qg (nC)</th>
            </tr>
            <tr>
                     <th>25°C</th>
                     <th>25°C</th>
                <th>10V</th>
                <th>4.5V</th>
                <th>2.5V</th>
                <th class="last">1.8V</th>
            </tr>
            <tr>
                <th>V</th>
                <th>V</th>
                     <th>A</th>
                     <th>W</th>
                <th>mΩ</th>
                <th>mΩ</th>
                <th>mΩ</th>
                <th class="last">mΩ</th>
          </tr>
          <tr>
  <th>
    <a href="?s=partNumber">▲</a><a href="?s=-partNumber">▼</a>
  </th>
  <th>
      <span style="color: darkred">▲</span><a href="?s=-statusId">▼</a>
  </th>
  <th>
    <a href="?s=recommendedReplacement">▲</a><a href="?s=-recommendedReplacement">▼</a>
  </th>
  <th>
    <a href="?s=package">▲</a><a href="?s=-package">▼</a>
  </th>
  <th>
    <a href="?s=configuration">▲</a><a href="?s=-configuration">▼</a>
  </th>
  <th>
    <a href="?s=configurationType">▲</a><a href="?s=-configurationType">▼</a>
  </th>
  <th>
    <a href="?s=vds">▲</a><a href="?s=-vds">▼</a>
  </th>
  <th>
    <a href="?s=vgs">▲</a><a href="?s=-vgs">▼</a>
  </th>
  <th>
    <a href="?s=ids25">▲</a><a href="?s=-ids25">▼</a>
  </th>
  <th>
    <a href="?s=pd25">▲</a><a href="?s=-pd25">▼</a>
  </th>
  <th>
    <a href="?s=rds10">▲</a><a href="?s=-rds10">▼</a>
  </th>
  <th>
    <a href="?s=rds4_5">▲</a><a href="?s=-rds4_5">▼</a>
  </th>
  <th>
    <a href="?s=rds2_5">▲</a><a href="?s=-rds2_5">▼</a>
  </th>
  <th>
    <a href="?s=rds1_8">▲</a><a href="?s=-rds1_8">▼</a>
  </th>
  <th>
    <a href="?s=qg">▲</a><a href="?s=-qg">▼</a>
  </th>
          </tr>

        </thead>
        <tbody>
            <tr>
  <td class="left first oneline">
    <a href="/zh/products/lv-mosfets/common-drain/AOCA32108E" class="info" rel="menu-0">AOCA32108E</a>
<div id="menu-0" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOCA32108E.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOCA32108E.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/AlphaDFN3.01x1.52B_10.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/AlphaDFN3.01x1.52B_10.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOCA32108E.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
  </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>AlphaDFN3.01x1.52B-10L</td>
                <td>Common Drain</td>
                <td>N</td>
                <td>12</td>
                <td>8</td>
                     <td>25</td>
                     <td>3.1</td>
                <td>-</td>
                <td>3.8</td>
                <td>5.6</td>
                <td>-</td>
                <td>32</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/common-drain/AOCA32112E" class="info" rel="menu-1">AOCA32112E</a>
<div id="menu-1" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOCA32112E.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOCA32112E.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/AlphaDFN0.97x0.97C_4.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/AlphaDFN0.97x0.97C_4.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOCA32112E.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>AlphaDFN0.97x0.97C-4L</td>
                <td>Dual</td>
                <td>N</td>
                <td>20</td>
                <td>12</td>
                     <td>4.5</td>
                     <td>1.1</td>
                <td>-</td>
                <td>48</td>
                <td>72</td>
                <td>-</td>
                <td>11.5</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/single/AOD32324" class="info" rel="menu-2">AOD32324</a>
<div id="menu-2" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOD32324.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOD32324.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO252.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO252.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOD32324.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>TO252</td>
                <td>Single</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>70</td>
                     <td>69</td>
                <td>3.4</td>
                <td>4.5</td>
                <td>-</td>
                <td>-</td>
                <td>35</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/single/AOD32326" class="info" rel="menu-3">AOD32326</a>
<div id="menu-3" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AOD32326.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AOD32326.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/TO252.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/TO252.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AOD32326.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>TO252</td>
                <td>Single</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>46</td>
                     <td>45</td>
                <td>6.2</td>
                <td>8.5</td>
                <td>-</td>
                <td>-</td>
                <td>17</td>
            </tr>
            <tr>
    <td rowspan="2" class="left first oneline">
      <a href="/zh/products/lv-mosfets/asymmetric/AONH36334" class="info" rel="menu-4">AONH36334</a>
<div id="menu-4" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONH36334.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONH36334.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3x3A_8L_EP2_S.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3x3A_8L_EP2_S.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONH36334.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3x3A-8L</td>
                <td>Asymmetric</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>16</td>
                     <td>23</td>
                <td>10.2</td>
                <td>15.8</td>
                <td>-</td>
                <td>-</td>
                <td>3.9</td>
            </tr>
            <tr>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3x3A-8L</td>
                <td>Asymmetric</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>18</td>
                     <td>25</td>
                <td>7.7</td>
                <td>11.6</td>
                <td>-</td>
                <td>-</td>
                <td>6</td>
            </tr>
            <tr>
    <td rowspan="2" class="left first oneline">
      <a href="/zh/products/lv-mosfets/complementary/AONL32328" class="info" rel="menu-6">AONL32328</a>
<div id="menu-6" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONL32328.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONL32328.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN4x3A_12L_EP2_S.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN4x3A_12L_EP2_S.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONL32328.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN4x3A-12L</td>
                <td>Complementary</td>
                <td>P</td>
                <td>-30</td>
                <td>20</td>
                     <td>-7</td>
                     <td>2.6</td>
                <td>27</td>
                <td>45</td>
                <td>-</td>
                <td>-</td>
                <td>12</td>
            </tr>
            <tr>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN4x3A-12L</td>
                <td>Complementary</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>8</td>
                     <td>2.6</td>
                <td>21</td>
                <td>32</td>
                <td>-</td>
                <td>-</td>
                <td>7</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/dual/AONP36320" class="info" rel="menu-8">AONP36320</a>
<div id="menu-8" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONP36320.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONP36320.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3.3x3.3C_8L_EP2_S.pdf">Package</a></li>
          
          
          <li><a target="_blank" href="/res/reliability_reports/AONP36320.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3.3x3.3C-8L</td>
                <td>Dual</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>100</td>
                     <td>50</td>
                <td>3.2</td>
                <td>5.2</td>
                <td>-</td>
                <td>-</td>
                <td>10</td>
            </tr>
            <tr>
    <td rowspan="2" class="left first oneline">
      <a href="/zh/products/lv-mosfets/dual/AONP36332" class="info" rel="menu-9">AONP36332</a>
<div id="menu-9" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONP36332.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONP36332.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3.3x3.3B_8L_EP2_S.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3.3x3.3B_8L_EP2_S.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONP36332.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3.3x3.3B-8L</td>
                <td>Asymmetric</td>
                <td>N</td>
                <td>30</td>
                <td>12</td>
                     <td>50</td>
                     <td>33</td>
                <td>3.7</td>
                <td>4.7</td>
                <td>-</td>
                <td>-</td>
                <td>10</td>
            </tr>
            <tr>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3.3x3.3B-8L</td>
                <td>Asymmetric</td>
                <td>N</td>
                <td>30</td>
                <td>12</td>
                     <td>50</td>
                     <td>30</td>
                <td>4.7</td>
                <td>5.9</td>
                <td>-</td>
                <td>-</td>
                <td>7.5</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/single/AONR21311C" class="info" rel="menu-11">AONR21311C</a>
<div id="menu-11" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONR21311C.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONR21311C.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3x3A_8L_EP1_P.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3x3A_8L_EP1_P.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONR21311C.pdf">Reliability Report</a></li>
          
          <li><a class="file" target="_blank" href="/res/esd_report/AONR21311C.zip">ESD Report</a></li>
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3x3A-8L</td>
                <td>Single</td>
                <td>N</td>
                <td>-30</td>
                <td>20</td>
                     <td>-12</td>
                     <td>11</td>
                <td>40</td>
                <td>61</td>
                <td>-</td>
                <td>-</td>
                <td>6</td>
            </tr>
            <tr>
    <td rowspan="2" class="left first oneline">
      <a href="/zh/products/lv-mosfets/complementary/AONR26309A" class="info" rel="menu-12">AONR26309A</a>
<div id="menu-12" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONR26309A.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONR26309A.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3x3A-8L EP1_P.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3x3A-8L EP1_P.pdf">Tape &amp; Reel</a></li>
          
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3x3A-8L</td>
                <td>Complementary</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>14</td>
                     <td>7</td>
                <td>20</td>
                <td>26</td>
                <td>-</td>
                <td>-</td>
                <td>6.5</td>
            </tr>
            <tr>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3x3A-8L</td>
                <td>Complementary</td>
                <td>P</td>
                <td>-30</td>
                <td>20</td>
                     <td>-21</td>
                     <td>20.8</td>
                <td>32</td>
                <td>55</td>
                <td>-</td>
                <td>-</td>
                <td>11</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/single/AONR34332C" class="info" rel="menu-14">AONR34332C</a>
<div id="menu-14" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONR34332C.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONR34332C.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN3.3x3.3_8L_EP1_S.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN3.3x3.3_8L_EP1_S.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONR34332C.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN3.3x3.3-8L</td>
                <td>Single</td>
                <td>N</td>
                <td>30</td>
                <td>12</td>
                     <td>100</td>
                     <td>56</td>
                <td>1.6</td>
                <td>1.9</td>
                <td>2.9</td>
                <td>-</td>
                <td>36</td>
            </tr>
            <tr>
    <td class="left first oneline">
      <a href="/zh/products/lv-mosfets/single/AONS18314" class="info" rel="menu-15">AONS18314</a>
<div id="menu-15" class="overlay">
    <div class="content">
        <ul class="documents">
          
            <li><a target="_blank" href="/res/data_sheets/AONS18314.pdf">Datasheet</a></li>
          <li><a target="_blank" href="/res/markings/AONS18314.pdf">Marking</a></li>
          <li><a target="_blank" href="/res/packaging_information/DFN5x6_8L_EP1_P.pdf">Package</a></li>
          
          <li><a target="_blank" href="/res/tape_reel/DFN5x6_8L_EP1_P.pdf">Tape &amp; Reel</a></li>
          <li><a target="_blank" href="/res/reliability_reports/AONS18314.pdf">Reliability Report</a></li>
          
          
        </ul>
    </div>
    <div class="marker"><img height="10" width="10" src="/images/blank.gif"></div>
</div>
    </td>

                <td class="wrap">New</td>
                <td class="wrap">-</td>
                <td>DFN5x6-8L</td>
                <td>Single</td>
                <td>N</td>
                <td>30</td>
                <td>20</td>
                     <td>30</td>
                     <td>31</td>
                <td>7.9</td>
                <td>10.4</td>
                <td>-</td>
                <td>-</td>
                <td>9.5</td>
            </tr>
        </tbody>
    </table>
    ''']

    json = table2json.table2json(text, [0, 1, 2], [3])
    print(json)
