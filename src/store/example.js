import axios from '@nextcloud/axios'
import { generateUrl, generateRemoteUrl } from '@nextcloud/router'
import { showError, showSuccess } from '@nextcloud/dialogs'
import { APP_API_PROXY_URL_PREFIX, EX_APP_ID } from '../constants/AppAPI.js'
import { translate as t } from '@nextcloud/l10n'

import { getCurrentUser } from '@nextcloud/auth'
import { getClient } from '@nextcloud/files/dav'
import { davGetClient } from '@nextcloud/files'

const state = {
	initial_state_value: {},
}

const mutations = {
	setInitialStateValue(state, data) {
		state.initial_state_value = data
	},
}

const getters = {
	getInitialStateValue: (state) => state.initial_state_value,
}

const actions = {
	verifyInitialStateValue(context, value) {
		axios.post(generateUrl(`${APP_API_PROXY_URL_PREFIX}/${EX_APP_ID}/api/verify_initial_value`), {
			initial_value: value,
		})
			.then((res) => {
				if ('initial_value' in res.data) {
					context.commit('setInitialStateValue', res.data.initial_value)
				} else {
					context.commit('setInitialStateValue', { error: 'No initial value returned' })
				}
				showSuccess(t('ui_example', 'Initial value is correct'))
			})
			.catch(() => {
				context.commit('setInitialStateValue', { error: 'Initial value is incorrect' })
				showError(t('ui_example', 'Initial value is incorrect'))
			})
	},

	sendNextcloudFileToExApp(context, fileInfo) {
		axios.post(generateUrl(`${APP_API_PROXY_URL_PREFIX}/${EX_APP_ID}/api/nextcloud_file`), {
			file_info: fileInfo,
		})
			.then(() => {
				showSuccess(t('ui_example', 'File sent'))
			})
			.catch(() => {
				showError(t('ui_example', 'Failed to send file'))
			})
	},

	getImageFromExApp(context, fileInfo) {
		return axios.post(generateUrl(`${APP_API_PROXY_URL_PREFIX}/${EX_APP_ID}/api/get_image`), {
			file_info: fileInfo,
			user_id: getCurrentUser().uid,
			responseType: 'blob',
		})
	},
	getImageFromDav(context, path) {
		const davClient = davGetClient(generateRemoteUrl(`dav/files/${getCurrentUser().uid}`))
		return davClient.getFileContents(path)
	},
	async loadImageFromDav(context, filename) {
		const davClient = getClient()
		// remove the first two leading components of the path
		const path = filename.split('/').slice(3).join('/')
		const response = await davClient.getFileContents(`${path}`, { details: true })
		return URL.createObjectURL(new Blob([response.data], { type: response.headers['content-type'] }))
	},
}

export default { state, mutations, getters, actions }
