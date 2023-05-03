<template>
    <v-container>
        <v-row>
            <v-col>
                <v-btn color="green-darken-1">Start Test</v-btn>
            </v-col>
            <v-col>
                <v-btn color="grey-darken-1">Stop Test</v-btn>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-switch label="Drain-Source" color="red-darken-1"></v-switch>
                <v-switch label="High Voltage to Gate" color="red-darken-1"></v-switch>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>


export default {
    name: "ControlMenu"
}
</script>