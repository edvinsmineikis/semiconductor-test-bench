<template>
    <v-card title="Control Board">
        <v-container>
            <v-row>
                <v-col>
                    <v-btn @click="this.$refs.commandSender.command = 'getTemp'">Temperature</v-btn>
                    <v-btn @click="this.$refs.commandSender.command = 'getTempTarget'">Temperature Target</v-btn>
                    <CommandSender :target="target" ref="commandSender"/>
                </v-col>
            </v-row>
        </v-container>
    </v-card>
</template>

<script>
import CommandSender from './CommandSender.vue';
export default {
    name: "ControlBoard",
    components: {
        CommandSender
    },
    data() {
        return {
            target: "ControlBoard"
        }
    }
}
</script>