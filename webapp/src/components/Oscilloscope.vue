<template>
    <v-card title="Oscilloscope">
        <v-container>
            <v-row>
                <v-col>
                    <v-btn @click="this.$refs.commandSender.command = 'HORIZONTAL:SCALE '">Scale</v-btn>
                    <v-btn @click="this.$refs.commandSender.command = 'HORIZONTAL:MODE:SAMPLERATE '">Sample Rate</v-btn>
                    <CommandSender :target="target" ref="commandSender"/>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <v-btn @click="updateChart" color="blue-darken-1">Update chart</v-btn>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <GChart type="LineChart" :data="chartData" :options="chartOptions" />
                </v-col>
            </v-row>
        </v-container>
    </v-card>
</template>

<script>
// https://github.com/devstark-com/vue-google-charts
import { GChart } from 'vue-google-charts'
import CommandSender from './CommandSender.vue';

export default {
    name: "Oscilloscope",
    components: {
        CommandSender,
        GChart,
    },
    props: {
        chartData: {
            type: Array,
        }
    },
    data() {
        return {
            target: "Oscilloscope",
            chartOptions: {
                legend: "none",
                vAxis: {
                    viewWindow: {
                        min: 0
                    }
                }
            }
        }
    },
    methods: {
        async updateChart() {
            let data = await this.postCommand("getCurve");
            this.chartData = [];
            this.chartData.push([["X"], ["Y"]])
            for (let i in data["value"]) {
                this.chartData.push([i, data["value"][i]]);
            }
            console.log(data["value"]);
        }
    }
}
</script>