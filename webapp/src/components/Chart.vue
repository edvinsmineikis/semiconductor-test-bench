<template>
    <v-card title="Oscilloscope">
        <GChart type="LineChart" :data="chartData" :options="chartOptions" />
    </v-card>
</template>

<script>
// https://github.com/devstark-com/vue-google-charts
import { GChart } from 'vue-google-charts'

export default {
    name: "Chart",
    components: {
        GChart
    },
    props: {
        chartData: {
            type: Array,
        }
    },
    data() {
        return {
            chartOptions: {
                legend: "none",
                vAxis: {
                    viewWindow: {
                        min: 0
                    }
                }
            }
        }
    }
}
</script>