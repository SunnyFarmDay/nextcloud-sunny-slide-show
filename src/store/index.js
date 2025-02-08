import Vue from 'vue'
import Vuex, { Store } from 'vuex'

import functions from './sunny-slide-show.js'

Vue.use(Vuex)

export default new Store({
	modules: {
		functions,
	},

	strict: process.env.NODE_ENV !== 'production',
})
