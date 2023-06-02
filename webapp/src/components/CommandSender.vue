<template>
    <v-container>
        <v-row>
            <v-col>
                <v-text-field v-model="this.command" label="Command" clearable></v-text-field>
            </v-col>
            <v-col>
                <v-btn @click="sendCommand" color="blue-darken-1">Send</v-btn>
                <v-progress-circular v-if="this.loading" indeterminate color="red" :style="{margin:'0 10px'}"></v-progress-circular>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-card color="grey-lighten-3">
                    <code>
                            {{ this.respField }}
                        </code>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>

export default {
    name: "CommandSender",
    data() {
        return {
            respField: '{}',
            command: '',
            loading: false
        }
    },
    props: {
        target: String,
    },
    methods: {
        async sendCommand() {
            this.loading = true;
            try {
                
                let response = await fetch("http://localhost:5000/instruments", {
                    method: "POST",
                    headers: {
                        "content-type": "application/json"
                    },
                    body: JSON.stringify({
                        "target": this.target,
                        "command": this.command,
                    })
                });
                let data = await (response).json();
                this.respField = JSON.stringify(data);
            } catch (error) {
                this.respField = JSON.stringify({
                    "error": error.message
                });
            }
            this.loading = false;
        }
    }
}
</script>