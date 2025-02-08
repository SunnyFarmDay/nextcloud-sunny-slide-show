<template>
	<router-view />
  </template>
  
  <script>
  export default {
	name: 'App',
	data() {
	  return {
		currentVersion: '1.0.2', // Update this with your current version
	  };
	},
	created() {
	  this.checkForUpdates();
	},
	methods: {
	  checkForUpdates() {
		const storedVersion = localStorage.getItem('appVersion');
  
		// Compare stored version with the current version
		if (storedVersion !== this.currentVersion) {
		  // Version has changed, clear cache and refresh
		  this.clearCache();
		  localStorage.setItem('appVersion', this.currentVersion);
		}
	  },
	  clearCache() {
		// Clear specific cache data or all data
		localStorage.clear(); // Clear local storage
		sessionStorage.clear(); // Clear session storage
		// Optionally, you can also reload the page
		window.location.reload(true); // Force reload from server
	  },
	},
  };
  </script>
  
  <style>
  /* Add your styles here if needed */
  </style>