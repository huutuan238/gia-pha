<template>
  <div
    id="FamilyChart"
    class="f3"
    style="
      width: 100%;
      height: 900px;
      margin: auto;
      background-color: rgb(33, 33, 33);
      color: #fff;
    "
  ></div>
</template>

<script>
import * as f3 from "family-chart";
import "family-chart/styles/family-chart.css";

import { getFamilyTree, updatePerson } from "../api/familyApi";

export default {
  name: "FamilyChart",

  data() {
    return {
      f3Chart: null,
      f3EditTree: null,
    };
  },

  mounted() {
    this.loadFamilyTree();
  },

  methods: {
    async loadFamilyTree() {
      try {
        const response = await getFamilyTree();

        this.create(response.data);
      } catch (error) {
        console.error("Load family tree error:", error);
      }
    },

    create(data) {
      this.f3Chart = f3
        .createChart("#FamilyChart", data)
        .setTransitionTime(1000)
        .setCardXSpacing(250)
        .setCardYSpacing(150);

      const f3Card = this.f3Chart
        .setCardHtml()
        .setCardDisplay([["first name", "last name"], ["birthday"]]);

      this.f3EditTree = this.f3Chart
        .editTree()
        .setFields(["first name", "last name", "birthday"])
        .setEditFirst(true)
        .setCardClickOpen(f3Card)

        .setOnChange(async (data, tree) => {
          console.log("Changed:", data);

          const changedPerson = data.data;

          // try {

          //   await updatePerson(
          //     data.id,
          //     data
          //   );

          //   console.log(
          //     "Saved"
          //   );

          // } catch(error) {

          //   console.error(
          //     "Save error:",
          //     error
          //   );

          // }
        });

      this.f3Chart.updateTree({
        initial: true,
      });

      this.f3EditTree.open(this.f3Chart.getMainDatum());

      this.f3Chart.updateTree({
        initial: true,
      });
    },
  },
};
</script>
