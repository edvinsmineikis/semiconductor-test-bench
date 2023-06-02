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
                    <PowerSupply/>
                </v-col>
                <v-col>
                    <ControlBoard/>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <Oscilloscope/>
                </v-col>
            </v-row>
        </v-container>
    </v-content>
</template>

<script>
import ControlMenu from "./ControlMenu.vue";
import PowerSupply from "./PowerSupply.vue";
import ControlBoard from "./ControlBoard.vue";
import Oscilloscope from "./Oscilloscope.vue";



export default {
    components: {
        ControlMenu,
        PowerSupply,
        ControlBoard,
        Oscilloscope
    },
    data() {
        return {
            chartData: []
        }
    }
}
</script>

<style>
.v-btn {
    text-transform: unset !important;
}
</style>