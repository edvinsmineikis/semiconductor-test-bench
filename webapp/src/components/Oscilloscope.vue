<template>
    <v-card title="Oscilloscope">
        <v-container>
            <v-row>
                <v-col>
                    <v-btn @click="this.$refs.commandSender.command = 'HORIZONTAL:SCALE '">Scale</v-btn>
                    <v-btn @click="this.$refs.commandSender.command = 'HORIZONTAL:MODE:SAMPLERATE '">Sample Rate</v-btn>
                    <v-btn @click="this.$refs.commandSender.command = 'DATA:SOURCE CH'">Set Channel</v-btn>
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
    data() {
        return {
            target: "Oscilloscope",
            chartData: [],
            chartOptions: {
                legend: "none",
                vAxis: {
                    title: 'Voltage, V',
                    viewWindow: {
                        min: 0
                    }
                }
            }
        }
    },
    methods: {
        async updateChart() {
            let url = "http://localhost:5000/measurements";
            let response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "content-type": "application/json"
                    },
                    body: JSON.stringify({
                        "command": "get_curve",
                    })
                });
            let data = await (response).json();
            this.chartData = [];
            this.chartData.push([["X"], ["Y"]])
            for (let i in data["message"]) {
                this.chartData.push([i, data["message"][i]]);
            }
            console.log(data);
        }
    }
}
</script>