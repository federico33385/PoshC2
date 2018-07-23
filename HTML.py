#!/usr/bin/env python

import sqlite3, re, subprocess, time
import pandas as pd
from Config import *

def graphviz():
  GV = """
digraph "PoshC2" {

  subgraph proxy {
      node [color=white, fontcolor=red, fontsize=15, shapefile="/opt/PoshC2_Python/Files/firewall.png"];
      "POSHSERVER";
  }

  subgraph implant {
      node [color=white, fontcolor=white, fontsize=15, shapefile="/opt/PoshC2_Python/Files/implant.png"];
      IMPLANTHOSTS
  }

  subgraph daisy {
      node [color=white, fontcolor=white, fontsize=15, shapefile="/opt/PoshC2_Python/Files/implant.png"];
      DAISYHOSTS
  }

}
  """
  ServerTAG = "\\n\\n\\n\\n\\n\\n\\n\\n\\n\\nPoshC2 Server\\n%s" % HostnameIP
  GV = GV.replace("POSHSERVER",ServerTAG)

  implants = get_implants_all_db()
  hosts = ""
  daisyhosts = ""

  for i in implants:
    if "Daisy" not in i[15]:
      if i[3] not in hosts:
        hostname = i[11].replace("\\","\\\\")
        hosts += "\"%s\" -> \"%s \\n %s\\n\\n\\n\\n \"; \n" % (ServerTAG,hostname,i[3])

  for i in implants:
    if "Daisy" in i[15]:
      hostname = i[11].replace("\\","\\\\")
      if "\"%s\\n\\n\\n\\n \" -> \"%s \\n %s\\n\\n\\n\\n \"; \n" % (i[9].replace('\x00','').replace("\\","\\\\").replace('@',' \\n '),hostname,i[3]) not in daisyhosts:
        daisyhosts += "\"%s\\n\\n\\n\\n \" -> \"%s \\n %s\\n\\n\\n\\n \"; \n" % (i[9].replace('\x00','').replace("\\","\\\\").replace('@',' \\n '),hostname,i[3])

  GV = GV.replace("DAISYHOSTS",daisyhosts)
  GV = GV.replace("IMPLANTHOSTS",hosts)
  output_file = open("%sPoshC2_Python.dot" % ReportsDirectory, 'w')
  output_file.write("%s" % GV.encode('utf-8'))
  output_file.close()
  subprocess.check_output("dot -T png -o %sPoshC2_Python.png %sPoshC2_Python.dot" % (ReportsDirectory,ReportsDirectory), shell=True)
  print ""
  print "GraphViz Generated PoshC2_Python.png"
  time.sleep(1)


def get_implants_all_db():
  conn = sqlite3.connect(DB)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute("SELECT * FROM Implants")
  result = c.fetchall()
  if result:
    return result
  else:
    return None

def get_htmlimplant( randomuri ):
  conn = sqlite3.connect(DB)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute("SELECT * FROM Implants WHERE RandomURI=?",(randomuri,))
  result = c.fetchone()
  if result:
    return result
  else:
    return None

def generate_table(table):
  HTMLPre = """<script>
function SearchCommand() {
  // Declare variables 
  var input, filter, table, tr, td, i;
  input = document.getElementById("CommandInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("PoshTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[3];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}
function SearchOutput() {
  // Declare variables 
  var input, filter, table, tr, td, i;
  input = document.getElementById("OutputInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("PoshTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[4];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}
function SearchTask() {
  // Declare variables 
  var input, filter, table, tr, td, i;
  input = document.getElementById("SearchTask");
  filter = input.value.toUpperCase();
  table = document.getElementById("PoshTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}


// Do some tweaking to markup to make things easier
function tweakMarkup(){
  
  // Add classes to columns
  var classes = ['id', 'taskid', 'randomuri', 'command', 'output', 'prompt']
  tbl = document.getElementById("PoshTable");
  ths = tbl.getElementsByTagName("th");
  for( i=0; i<ths.length; i++ ){
    th = ths[i];
    th.className = classes[i]
  }
  trs = tbl.getElementsByTagName("tr");
  for( i=0; i<trs.length; i++ ){
    tr = trs[i]
    tds = tr.getElementsByTagName('td');
    if( i % 2 == 0 ){
      tr.className = 'even';
    }else{
      tr.className = 'odd';
    }
    for( j=0; j<tds.length; j++ ){
      td = tds[j];
      td.className = classes[j]
      if( td.className.match(/output|command/) ){
        td.className += ' hidden';
        td.innerHTML = '<div>' + td.innerHTML + '</div>';
        td.onclick = toggleHide
      }
    }
  }

}

function toggleHide( evnt ){
  td = evnt.target;
  if( td.nodeName == 'DIV' ){
    td = td.parentElement;
  }
  cls = td.className;
  if( cls.match(/hidden/) ){
    cls = cls.replace('hidden','shown');
  }else{
    cls = cls.replace('shown','hidden');
  }
  td.className = cls;
}

</script>

<style>

#CommandInput, #OutputInput, #SearchTask {
    background-image: url('/css/searchicon.png'); /* Add a search icon to input */
    background-position: 10px 12px; /* Position the search icon */
    background-repeat: no-repeat; /* Do not repeat the icon image */
    width: 100%; /* Full-width */
    font-size: 16px; /* Increase font-size */
    padding: 12px 20px 12px 40px; /* Add some padding */
    border: 1px solid #ddd; /* Add a grey border */
    margin-bottom: 12px; /* Add some space below the input */
}

body {
font-family: Verdana, Geneva, Arial, Helvetica, sans-serif;
}

table {
  font-family: monospace;
  margin: 1em 0;
  white-space: pre;
  border-spacing: 0;
  width: 100%;
  table-layout: fixed;
}
  table tr {}
  table tr.even{
    background-color: #f2f2f2
  }
    table tr th,
    table tr td {
      text-align: left;
      padding: 0.5em;
      border: 1px solid #ccc;
      
    }
    table tr th {
        background-color: #4CAF50;
        color: white;
    }
    table tr td {
      vertical-align: top;
    }
    table tr td.command {
    }
    table tr td.hidden div, 
    table tr td.shown div {
      cursor: pointer;
      background: top right url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHkSURBVDjL3ZNvT1JhGMafb3G+TQqKECNFRIEDcvgXmB5IPNJmTdbC1SQ0S1xzZKXyT41TdpCOMyYtiXS9aW2uD8EbPsHV87RRmyLrdc92vbt/1/U8930/ZLYxASbpSwgz9SCin2+CHtJJwYoLgbITvvcOeN7a4S6NgTB45+cmCucvu8JMFOZCZQHpr0tYO12Ga9cKwpJz5xvIfH+GR2dxRGp+uSOs8Jxv39GKV+/gYS2OlXoSfNECMnMSRKw+hdS3BLI/Mlho3MPUR88lE+++ozlfjWG1kYJUCcNRsMCWM4NM02vf/hTgwsf+1uLpfTw4mcOtQ0G9aCDINiWmRiAdiAz+HTC6Nfi3QKx6uckjT3Pi0K1c1QPnzojahtsi3Zr2L/rfDGin5fE3o+pVxeYXRmVw3dA0Pddzfwz8Co82LFVERMuTbEyXJjGUMaqBgoBQ0Qfjmq5lWO3n9E/76IK8s4PCYHCytoDZgwhsWXPzosGNdYPszY1jTonBnxVgSuuhe6KhyfRDJGsJ3P0gQSqLDG7RBeE6PeF6Wie7X/MI5N2YLonoX+oFce1ZsXicQOJoHs68FdbNznBbAytaREthSHIE2lQPCF8cgT0/jLHtIQbD8sqEbrBuWYM+mqx93ANN8hp+AQOPtI0tirA3AAAAAElFTkSuQmCC);
      background-repeat: no-repeat;
      
      overflow: scroll;
      word-wrap: break-all;
      white-space:normal;
      min-height: 25px;
      width: 100%;
    }
    table tr td.shown div {
      background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHqSURBVDjL3ZHbThpRFIZ5i3kcLRYPqIgUGcDhNKBAqyKCobTR2NhiKmCstcWmBmtLPaCO4CQ6SBWVKInx0N70KbjhCf7O3ia0ZS686F0vVrL3Xvv7VvIvFQBVuOITQxfe6tj5IEPu9xW/ZxGcu2aJnAksxW9eYP42hmB5oBY48zAjJ240QoP7HH3j8xYhWgwiUgiAyxpFlTxZmL2ewvrPNBJX0wid+TF0zCsEHtEKGcbT4igWK0k8OwzBumGo0uZoeUCYuZzE0vUcVn6k8OSbUyFwyfDbSgKvShOIFsZgWTfU2K96pv5huOSm8KfvS/AXHAqBQ2CxcJFAsjwDe5YFgWkGdzCPoSMXHhed8BXs8B7YFALbVh/6Nx+RyWAzevR91qEu+Jf6XwRuecdkTSRp27YcVtaoCLE33Qn9sha6D+3oSrVB+07zO0RXzsx4chxmT18ifhqjSTcKej5qMbkfRVQM12EqILA8uRaRgnguhRE7mqJrahR0y5MjYgi+TTfsq1a0vVELVODYMVUJ/Lo0jZG8768d/1md71uhS2nBZxwYzwXRn2bxMNksqLgtoxgQ/RjOe2HK9FCrYaVLIehY1KB9oYVpnVfXnKscrMsmqBNNEm2a13ol05c7+L7SzD1gWpLNVXW8SST3X7gvtJUuvnAlAAAAAElFTkSuQmCC);
    }
    table tr td.output {
      width: 100px;
    }
    table tr td.hidden div {
      height: 1em;
      overflow: hidden;
      cursor: pointer;
    }
    table tr th.id {
      width: 3%;
      min-width: 3em;
    }
    table tr th.taskid {
      width: 12%;
    }
    table tr th.randomuri {
      width: 15%;
    }
    table tr th.prompt {
      width: 10%;
    }

p { 
margin-left: 20px; 
font-size: 12px; 
}
 
</style>

<pre>
__________            .__.     _________  ________  
\_______  \____  _____|  |__   \_   ___ \ \_____  \ 
|     ___/  _ \/  ___/  |  \  /    \  \/  /  ____/ 
|    |  (  <_> )___ \|   Y  \ \     \____/       \ 
|____|   \____/____  >___|  /  \______  /\_______  
                  \/     \/          \/         \/
=============== v4.0 www.PoshC2.co.uk =============
</pre>
"""

  if table == "CompletedTasks":
    HTMLPre += """<input type="text" id="SearchTask" onkeyup="SearchTask()" placeholder="Search for task..">
<input type="text" id="CommandInput" onkeyup="SearchCommand()" placeholder="Search for command..">
<input type="text" id="OutputInput" onkeyup="SearchOutput()" placeholder="Search for output..">
"""

  conn = sqlite3.connect(DB)
  pd.set_option('display.max_colwidth', -1)
  pd.options.mode.chained_assignment = None
  frame = pd.read_sql_query("SELECT * FROM %s" % table, conn)
  if table == "CompletedTasks":
    framelen = frame['RandomURI'].count()
    for x in range(0, framelen):
      try:
        frame['RandomURI'][x]
        a = get_htmlimplant(str(frame['RandomURI'][x]))
        frame['RandomURI'][x] = a[3], a[11]
      except Exception as e:
        print e
        a = "None"

  reportname = "%s%s.html" % (ReportsDirectory,table)
  output_file = open(reportname, 'w')
  HTMLPost = (frame.to_html(classes='table',index=False,escape=False)).replace("\\r\\n","</br>")
  HTMLPost = HTMLPost.replace("\\n","</br>")
  HTMLPost = re.sub(u'\x00', '', HTMLPost)  
  HTMLPost = HTMLPost.replace("      <td>","      <td class=\"TableColumn\">")
  HTMLPost = HTMLPost.replace("<tr style=\"text-align: right;\">","<tr>")
  HTMLPost = HTMLPost.replace("<table border=\"1\" class=\"dataframe table\">","<table id=\"PoshTable\" border=\"1\" class=\"PoshTableClass\">")
  HTMLPost = HTMLPost.replace("<th>CompletedTaskID</th>","<th class=\"CompletedTaskID\">ID</th>")
  HTMLPost = HTMLPost.replace("<th>ID</th>","<th class=\"ID\">ID</th>")
  HTMLPost = HTMLPost.replace("<th>TaskID</th>","<th class=\"TaskID\">TaskID</th>")
  HTMLPost = HTMLPost.replace("<th>RandomURI</th>","<th class=\"RandomURI\">RandomURI</th>")
  HTMLPost = HTMLPost.replace("<th>Command</th>","<th class=\"Command\">Command</th>")
  HTMLPost = HTMLPost.replace("<th>Output</th>","<th class=\"Output\">Output</th>")
  HTMLPost = HTMLPost.replace("<th>Prompt</th>","<th class=\"Prompt\">Prompt</th>")

  HTMLPost = HTMLPost + """
<script>
tweakMarkup();
</script>"""
  output_file.write("%s%s" % (HTMLPre.encode('utf-8'),HTMLPost.encode('utf-8')))
  output_file.close()
  print reportname
