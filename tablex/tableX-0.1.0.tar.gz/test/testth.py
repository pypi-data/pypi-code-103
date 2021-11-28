import re

from tableX import table2json
#
if __name__ == '__main__':
    text = ["""
    <table class="table">
                    <thead>
                      <tr>
        <th>产品型号</th>
        <th>输入电压(V)</th>
        <th>输出电压(V)</th>
        <th>工作频率(Hz)</th>
        <th>效率(%)</th>
        <th>限流值(mA)</th>
        <th>封装</th>
        <th>规格书</th>
      </tr>
                    </thead>
                    <tbody>
                <div id="tag9be49e7c9bbe91f6673a4caabb748f94">
<tr>
        <th><a href="/html/OurService/OrgOptChange/760.html" class="title">LP3101</a></th>
        <td>2.5-4.8</td>
        <td>±5.1-5.9</td>
        <td>300K</td>
        <td>-</td>
        <td>±40mA</td>       
         <td>TDFN-12</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000109_LP3101A-00.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/573.html" class="title">LP3102</a></th>
        <td>2.5-4.8</td>
        <td>±5.5-5.9</td>
        <td>300K</td>
        <td>-</td>
        <td>±120</td>       
         <td>TDFN-10</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_34.1/201807/L_rc20180717000009_L20180717000007_LP3102-02.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/863.html" class="title">LP6286</a></th>
        <td>2.5-5.5</td>
        <td>6-18</td>
        <td>600/1200K</td>
        <td>92</td>
        <td>3000</td>       
         <td>TQFN-24 4x4</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000116_LP6286-00-V00-NOV-2016.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/572.html" class="title">LP3100</a></th>
        <td>2.8-4.8</td>
        <td>±5.5-5.9</td>
        <td>300K</td>
        <td>-</td>
        <td>±40mA</td>       
         <td>TDFN-12</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000108_LP3100-00.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/1020.html" class="title">LP6289</a></th>
        <td>8.0-14</td>
        <td>13.5-19.8</td>
        <td>750K</td>
        <td>90</td>
        <td>5000</td>       
         <td>TQFN 5X5-40</td>
        <td> <div class="table-responsive rounded p-1"><a href="" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/864.html" class="title">LP6288</a></th>
        <td>8-14</td>
        <td>13.5-19.8</td>
        <td>750K</td>
        <td>90</td>
        <td>~4250(Adj)</td>       
         <td>TQFN 6X6-40</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000117_LP6288-00-V01-JAN-2018.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/764.html" class="title">LP6285</a></th>
        <td>2.5-5.5</td>
        <td>6.0-18</td>
        <td>600K/ 1.2M</td>
        <td>92</td>
        <td>2500</td>       
         <td>TQFN 3X3-16</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000115_LP6285-00-V01-MAR-2017.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/763.html" class="title">LP6284</a></th>
        <td>2.5-5.5</td>
        <td>Vin-16</td>
        <td>640K/ 1.2M</td>
        <td>92</td>
        <td>2000</td>       
         <td>TQFN 4X4-24</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000114_LP6284-00-V00-AUG-2016.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/762.html" class="title">LP6283</a></th>
        <td>8-14</td>
        <td>Vin-18</td>
        <td>500/750K</td>
        <td>90</td>
        <td>4000</td>       
         <td>TQFN 7X7-48</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000113_LP6283-00-V00-JUL-2016.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/862.html" class="title">LP6282</a></th>
        <td>2.7-5.5</td>
        <td>Vin-13</td>
        <td>1500</td>
        <td>90</td>
        <td>2000</td>       
         <td>TQFN 3X3-20</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201806/L_rc20180623000014_L20180623000112_LP6282-00-V01-SET-2017.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
<tr>
        <th><a href="/html/OurService/OrgOptChange/761.html" class="title">LP6280</a></th>
        <td>2.1-5.5</td>
        <td>±4-6</td>
        <td>1M</td>
        <td>94</td>
        <td>±120</td>       
         <td>WLCSP</td>
        <td> <div class="table-responsive rounded p-1"><a href="http://es.kcttek.com:811/ESAPP1_22.1/201906/L_rc20180623000014_L20180623000111_LP6280-00-V01-DEC-2016.pdf" id="m1" target="_blank"><img src="/images/add.jpg"></a></div>
</td>
      </tr>
    </div>

                    </tbody>
                  </table>
"""]
    json = table2json.table2json(text, [0], [], 2,0)

    # json = table2json.table2jsonStr(text, [0, 1, 2], [3])
    print(json)

