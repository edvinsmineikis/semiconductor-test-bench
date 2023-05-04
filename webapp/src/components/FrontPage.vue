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
                    <Parameters />
                </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-row>
                <v-col>
                    <Chart />
                </v-col>
            </v-row>
        </v-container>
    </v-content>
</template>

<script>
import ControlMenu from './ControlMenu.vue';
import Parameters from './Parameters.vue';
import Chart from './Chart.vue';


export default {
    components: {
        ControlMenu,
        Parameters,
        Chart
    },
    data() {
        return {
            drawer: true
        }
    }
}
</script>