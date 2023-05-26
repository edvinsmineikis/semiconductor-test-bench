<template>
    <v-app-bar title="Semiconductor Test Bench" color="blue-darken-1">
    </v-app-bar>

    <v-navigation-drawer color="grey-lighten-2">
        <v-list>
            <v-list-item>
                <ControlMenu />
            </v-list-item>
        </v-list>
    </v-navigation-drawer>

    <v-content>
        <v-container>
            <v-row>
                <v-col>
                    <Parameters @chart-update="updateChart()"/>
                </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-row>
                <v-col>
                    <Chart :chartData="chartData"/>
                </v-col>
            </v-row>
        </v-container>
    </v-content>
</template>

<script>
import ControlMenu from "./ControlMenu.vue";
import Parameters from "./Parameters.vue";
import Chart from "./Chart.vue";


export default {
    components: {
        ControlMenu,
        Parameters,
        Chart
    },
    data() {
        return {
            chartData: []
        }
    },
    methods: {
        async postCommand(command) {
            let response = await fetch("http://localhost:5000/commands", {
                method: "POST",
                body: JSON.stringify({ "command": command })
            });
            let data = await (response).json();
            return data;
        },
        async updateChart() {
            let data = await this.postCommand("testCmd");
            this.chartData = [];
            this.chartData.push([["X"],["Y"]])
            for (let i in data["got"]) {
                this.chartData.push([i, data["got"][i]]);
            }
            console.log(this.chartData);
        }
    }
}
</script>