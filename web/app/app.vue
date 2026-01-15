<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
</script>

<style>
@import "tailwindcss";

/* Official YÖK Color Palette */
:root {
  --sidebar-bg: #e8e8e8;
  --sidebar-text: #ae5961;
  --accent-red: #bc5f68;
  --accent-green: #5eab8c;
  --accent-gray: #7c7c7c;
  --text-primary: #30302f;
  --page-bg: #f7f7f7;
  --border-color: #d0d0d0;
}

/* Reset body/html to prevent white space and scrollbar shift */
html {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  overflow-y: scroll; /* Always show scrollbar to prevent content shift */
}

body {
  margin: 0;
  padding: 0;
  width: 100%;
  overflow-x: hidden;
}

/* No rounded corners - official/formal look */
* {
  border-radius: 0 !important;
}

/* Form control */
.form-control {
  display: block;
  width: 100%;
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.5;
  color: #30302f;
  background: #fff;
  border: 1px solid #ccc;
  transition: border-color 0.15s;
}

.form-control:focus {
  border-color: #ae5961;
  outline: none;
}

/* Panel styles */
.x-panel {
  background: #fff;
  border: 1px solid #d0d0d0;
  margin-bottom: 15px;
}

.x-panel .x-title {
  border-bottom: 1px solid #d0d0d0;
  padding: 12px 15px;
  background: #f9f9f9;
}

.x-panel .x-title h2 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #30302f;
}

.x-panel .x-content {
  padding: 15px;
}

/* Button styles */
.btn-red {
  background: #bc5f68;
  border: 1px solid #bc5f68;
  color: #fff;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}

.btn-red:hover {
  background: #a85058;
}

.btn-green {
  background: #5eab8c;
  border: 1px solid #5eab8c;
  color: #fff;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}

.btn-green:hover {
  background: #4d9a7a;
}

.btn-gray {
  background: #7c7c7c;
  border: 1px solid #7c7c7c;
  color: #fff;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}

.btn-gray:hover {
  background: #666;
}

/* Table styles */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  background: #f5f5f5;
  border: 1px solid #d0d0d0;
  padding: 8px 10px;
  text-align: left;
  font-weight: 500;
  color: #30302f;
}

.data-table td {
  border: 1px solid #d0d0d0;
  padding: 8px 10px;
  color: #30302f;
}

.data-table tr:nth-child(even) {
  background: #fafafa;
}

.data-table tr:hover {
  background: #f0f0f0;
}

/* Alert boxes */
.alert-info {
  background: #e8f4fd;
  border: 1px solid #b8daff;
  padding: 12px 15px;
  color: #004085;
}

.alert-warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
  padding: 12px 15px;
  color: #856404;
}
</style>
