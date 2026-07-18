
<template>
  <div id="FamilyChart" class="f3" style="width:100%;height:900px;margin:auto;background-color:rgb(33,33,33);color:#fff;"></div>
</template>

<script>
import * as d3 from 'd3';  // npm install d3 or yarn add d3
import * as f3 from 'family-chart';  // npm install family-chart@0.9.0 or yarn add family-chart@0.9.0
import 'family-chart/styles/family-chart.css';
     
export default {
  name: "FamilyChart",
  mounted() {
    fetch('http://localhost:5001')
      .then(res => res.json())
      .then(data => create(data))
      .catch(err => console.error(err))
    
    function create(data) {
      const f3Chart = f3.createChart('#FamilyChart', data)
        .setTransitionTime(1000)
        .setCardXSpacing(250)
        .setCardYSpacing(150)
    
      const f3Card = f3Chart.setCardHtml()
        .setCardDisplay([["first name","last name"],["birthday"]])
    
      const f3EditTree = f3Chart.editTree()
        .setFields(["first name","last name","birthday", "gender"])
        .setEditFirst(true)  // true = open form on click, false = open info in click
        .setCardClickOpen(f3Card)
        .setOnChange((data, tree) => {

          const main = f3EditTree.exportData()

console.log(main)

// gọi API Flask ở đây

})
        // .setNoEdit()  // if you want to just see info form
    
      f3Chart.updateTree({initial: true})
      f3EditTree.open(f3Chart.getMainDatum())
      f3Chart.updateTree({initial: true})
    }
  }
};
</script>
