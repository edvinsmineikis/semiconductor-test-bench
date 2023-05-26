<template>
    <v-card title="Parameters">
        <v-container>
            <v-row>
                <v-col align="center">
                    <v-progress-circular color="red-darken-1" :model-value="30" :size="56" :width="8"></v-progress-circular>
                    <h3>Progress</h3>
                </v-col>
            </v-row>
            <v-row>
                <v-btn @click="$emit('chart-update')" color="blue-darken-1">Update chart</v-btn>
            </v-row>
        </v-container>
    </v-card>
</template>

<script>
export default {
    name: "Parameters",
}
</script>