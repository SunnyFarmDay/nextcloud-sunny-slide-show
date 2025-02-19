import VueRouter from 'vue-router' // eslint-disable-line
import { generateUrl } from '@nextcloud/router'
import Vue from 'vue'
import { APP_API_ROUTER_BASE, EX_APP_ID, EX_APP_MENU_ENTRY_NAME } from '../constants/AppAPI.js'
import 'remixicon/fonts/remixicon.css'

const SlideShow = () => import('../views/SlideShow.vue')

Vue.use(VueRouter)

function setPageHeading(heading) {
	const headingEl = document.getElementById('page-heading-level-1')
	if (headingEl) {
		headingEl.textContent = heading
	}
}

const baseTitle = document.title
const router = new VueRouter({
	mode: 'history',
	base: generateUrl(`${APP_API_ROUTER_BASE}/${EX_APP_ID}/${EX_APP_MENU_ENTRY_NAME}`, ''), // setting base to AppAPI embedded URL
	linkActiveClass: 'active',
	routes: [
		{
			path: '/slide_show',
			component: SlideShow,
			name: 'slide_show',
			meta: {
				title: async () => {
					return t('sunny-slide-show', 'ExApp slide show')
				},
			},
		},
	],
})

router.afterEach(async (to) => {
	const metaTitle = await to.meta.title?.(to)
	if (metaTitle) {
		document.title = `${t('ui_example', metaTitle)} - ${baseTitle}`
		setPageHeading(metaTitle)
	} else {
		document.title = baseTitle
	}
})

export default router
