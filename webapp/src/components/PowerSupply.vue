<template>
    <v-card title="Power Supply">
        <v-container>
            <v-row>
                <v-col>
                    <v-btn @click="this.$refs.commandSender.command = 'SYST:LOCK ON'">Lock ON</v-btn>
                    <v-btn @click="this.$refs.commandSender.command = 'SYST:LOCK OFF'">Lock OFF</v-btn>
                    <CommandSender :target="target" ref="commandSender" />
                </v-col>
            </v-row>
        </v-container>
    </v-card>
</template>

<script>
import CommandSender from './CommandSender.vue';
export default {
    name: "PowerSupply",
    components: {
        CommandSender
    },
    data() {
        return {
            target: "PowerSupply"
        }
    },
    methods: {
        async postCommand(command, value = 0) {
            let response = await fetch("http://localhost:5000/commands", {
                method: "POST",
                body: JSON.stringify({
                    "command": command,
                    "value": value
                })
            });
            let data = await (response).json();
            return data;
        }
    }
}
</script>