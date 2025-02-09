<template>
	<NcContent app-name="sunny-slide-show">
		<template v-if="loading">
			<div class="loader">
				<div class="loader__spinner" />
			</div>
		</template>
		<NcAppContent>
			<div class="test-files-pickers">
				<div class="slider-container">
					<div class="autoplay-control">
						<div class="slider-container">
							<label for="autoplay-slider">Autoplay Speed: {{ autoPlayInterval }} ms</label>
							<input id="autoplay-slider"
								v-model="autoPlayInterval"
								type="range"
								min="1000"
								max="10000"
								step="100">
						</div>
					</div>
				</div>

				<div ref="fullscreenDiv" :class="isFullscreen ? 'media-container-fullscreen' : 'media-container'">
					<template v-if="loadingMedia">
						<div class="loader_local">
							<div class="loader__spinner" />
							<p>{{ loadingMediaText }}</p>
						</div>
					</template>
					<template v-else>
						<transition name="fade" mode="out-in">
							<RenderMedia
								:animation-enabled="enableAnimation"
								:animation="animationStyles"
								:media-type="currentMedia.mime ?? ''"
								:selected-url="currentUrl"
								:video-ended-handler="handleVideoEnd"
								@left-swipe="handleNext"
								@right-swipe="handlePrevious" />
						</transition>
					</template>
					<div class="scroll-buttons">
						<button class="left-button" @click="handlePrevious">
							<i class="ri-arrow-left-double-line" />
						</button>
						<button class="right-button" @click="handleNext">
							<i class="ri-arrow-right-double-line" />
						</button>
					</div>
					<NcButton class="toggle-fullscreen" @click="toggleFullscreen">
						<i :class="isFullscreen ? 'ri-fullscreen-fill' : 'ri-fullscreen-fill'" />
					</NcButton>
					<NcButton class="toggle-auto-play" @click="toggleAutoPlay">
						<i :class="autoPlay ? 'ri-stop-fill' : 'ri-play-fill'" />
					</NcButton>
				</div>
			</div>
		</NcAppContent>
	</NcContent>
</template>

<script>
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'
import { searchByFileId } from '../files.js'

import '@nextcloud/dialogs/style.css'
import NcContent from '@nextcloud/vue/dist/Components/NcContent.js'
import NcAppContent from '@nextcloud/vue/dist/Components/NcAppContent.js'
import RenderMedia from '../components/RenderMedia.vue'

export default {
	name: 'SlideShow',
	components: {
		RenderMedia,
		NcContent,
		NcButton,
		NcAppContent,
	},
	data() {
		return {
			loading: true,
			currentMedia: {},
			selectedFileIds: [],
			fileInfos: {},
			currentUrl: '',
			currentMediaIndex: 0,
			loadedMedia: {},
			preloadAmountForward: 10,
			preloadAmountBackward: 5,
			lastPollLoading: null,
			isFullscreen: false,
			autoPlay: false,
			autoPlayInterval: 3000,
			autoPlayTimeout: null,
			loadingMedia: false,
			loadingMediaText: '',
			animationStyles: {
				'--start-x': '0',
				'--start-y': '0',
				'--end-x': '0',
				'--end-y': '0',
				'--start-scale': 1,
				'--end-scale': 1,
				'--animation-duration': '0',
			},
			isMobile: false,
			enableAnimation: false,
		}
	},
	computed: {
	},
	beforeMount() {
		// Load files info from fileIds query parameter if exists
		if (this.$route.query.fileIds) {
			this.selectedFileIds = this.$route.query.fileIds.split(',').map(Number)
			this.selectedFileIds.forEach(fileId => {
				this.fileInfos[fileId] = null
			})
		}

		// check viewport to determine if it's a mobile device
		this.isMobile = window.innerWidth <= 768
	},
	mounted() {
		document.addEventListener('fullscreenchange', this.handleFullscreenChange)
		document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange) // Safari
		document.addEventListener('mozfullscreenchange', this.handleFullscreenChange) // Firefox
		document.addEventListener('MSFullscreenChange', this.handleFullscreenChange) // IE/Edge
		this.loading = false
		this.setViewMediaIndex(0)
	},
	beforeDestroy() {
		document.removeEventListener('fullscreenchange', this.handleFullscreenChange)
		document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange)
		document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange)
		document.removeEventListener('MSFullscreenChange', this.handleFullscreenChange)
	},
	methods: {
		async getFileInfoIntoList(fileId) {
			const fileInfo = await searchByFileId(fileId)
			this.fileInfos[fileId] = fileInfo
			return fileInfo
		},
		randomizeAnimationStyles() {
			if (!this.isMobile) {
				this.animationStyles = {
					'--start-x': '0px',
					'--start-y': '0px',
					'--end-x': `${Math.random() * 300}px - 150px`,
					'--end-y': `${Math.random() * 300}px - 150px`,
					'--start-scale': '1',
					'--end-scale': Math.random() * 0.5 + 0.90,
					'--animation-duration': this.autoPlayInterval / 1000 + 's',
				}
			} else {
				this.animationStyles = {
					'--start-x': '0px',
					'--start-y': '0px',
					'--end-x': `${Math.random() * 100}px - 50px`,
					'--end-y': `${Math.random() * 100}px - 50px`,
					'--start-scale': '1',
					'--end-scale': Math.random() * 0.2 + 0.98,
					'--animation-duration': this.autoPlayInterval / 1000 + 's',
				}
			}
		},
		toggleAutoPlay() {
			this.autoPlay = !this.autoPlay
			if (this.autoPlay) {
				this.enableAnimation = true
				this.setViewMediaIndex(this.currentMediaIndex)
			} else {
				this.enableAnimation = false
				clearTimeout(this.autoPlayTimeout)
				this.animationStyles = {
					'--start-x': '0',
					'--start-y': '0',
					'--end-x': '0',
					'--end-y': '0',
					'--start-scale': 1,
					'--end-scale': 1,
					'--animation-duration': '0',
				}
			}
		},
		handleVideoEnd() {
			if (this.autoPlay) {
				this.setViewMediaIndex(Math.min(this.selectedFileIds.length - 1, this.currentMediaIndex + 1))
			}
		},
		handleFullscreenChange() {
			this.isFullscreen = !!document.fullscreenElement
		},
		toggleFullscreen() {
			const div = this.$refs.fullscreenDiv

			if (!this.isFullscreen) {
				if (div.requestFullscreen) {
					div.requestFullscreen()
				} else if (div.mozRequestFullScreen) { // Firefox
					div.mozRequestFullScreen()
				} else if (div.webkitRequestFullscreen) { // Chrome, Safari and Opera
					div.webkitRequestFullscreen()
				} else if (div.msRequestFullscreen) { // IE/Edge
					div.msRequestFullscreen()
				}
			} else {
				if (document.exitFullscreen) {
					document.exitFullscreen()
				} else if (document.mozCancelFullScreen) { // Firefox
					document.mozCancelFullScreen()
				} else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
					document.webkitExitFullscreen()
				} else if (document.msExitFullscreen) { // IE/Edge
					document.msExitFullscreen()
				}
			}
			this.isFullscreen = !this.isFullscreen
		},
		preloadMedia(index) {
			if (!this.loadedMedia[index]) {
				this.loadedMedia[index] = true

				const fileId = this.selectedFileIds[index]

				this.getFileInfoIntoList(fileId).then(() => {
					this.$store.dispatch('loadImageFromDav', this.fileInfos[fileId].filename).then(url => {
						if (this.loadedMedia[index] === 'abort') {
							URL.revokeObjectURL(url)
							this.loadedMedia[index] = null

						} else {
							this.loadedMedia[index] = url
						}

					}).catch(error => {
						console.error('Error fetching media:', error)
					})
				})
			}
		},
		setUpAutoPlay() {
			if (this.autoPlay) {
				const fileId = this.selectedFileIds[this.currentMediaIndex]
				const isVideo = this.fileInfos[fileId].mime.startsWith('video')
				if (this.autoPlayTimeout || isVideo) {
					clearTimeout(this.autoPlayTimeout)
				}
				if (isVideo) {
					return
				}
				this.autoPlayTimeout = setTimeout(() => {
					this.setViewMediaIndex(Math.min(this.selectedFileIds.length - 1, this.currentMediaIndex + 1))
				}, this.autoPlayInterval)
			}
		},
		loadedMediaToCurrentDisplay() {
			this.loadingMedia = true
			this.loadingMediaText = ''
			this.currentUrl = this.loadedMedia[this.currentMediaIndex]
			this.randomizeAnimationStyles()
			this.setUpAutoPlay()
			this.loadingMedia = false
		},
		setViewMediaIndex(index) {
			if (index < 0 || index >= this.selectedFileIds.length) {
				return
			}
			this.loadingMedia = true
			this.currentUrl = ''
			this.currentMediaIndex = index
			this.currentMedia = {
				fileId: this.selectedFileIds[index],
			}
			const fileId = this.selectedFileIds[index]

			// load the current media
			if (!this.loadedMedia[index]) {
				if (this.fileInfos[fileId] instanceof Object) {
					this.loadingMediaText = `Loading ${this.fileInfos[fileId].filename}...`
					Object.assign(this.currentMedia, this.fileInfos[fileId])
					this.$store.dispatch('loadImageFromDav', this.fileInfos[fileId].filename).then(url => {
						this.loadedMedia[index] = url
						this.loadedMediaToCurrentDisplay()
					}).catch(error => {
						console.error('Error fetching media:', error)
					})
				} else {
					this.loadingMediaText = 'Loading media...'
					this.getFileInfoIntoList(fileId).then(() => {
						Object.assign(this.currentMedia, this.fileInfos[fileId])
						this.$store.dispatch('loadImageFromDav', this.fileInfos[fileId].filename).then(url => {
							this.loadedMedia[index] = url
							this.loadedMediaToCurrentDisplay()
						}).catch(error => {
							console.error('Error fetching media:', error)
						})
					})
				}
			} else {
				if (this.loadedMedia[index] === true) {
					Object.assign(this.currentMedia, this.fileInfos[fileId])
					if (this.currentMedia.filename) {
						this.loadingMediaText = `Loading ${this.currentMedia.filename}...`
					} else {
						this.loadingMediaText = 'Loading media...'
					}
					if (this.lastPollLoading) {
						clearTimeout(this.lastPollLoading)
					}
					this.lastPollLoading = setTimeout(() => {
						this.setViewMediaIndex(index)
					}, 100)
				} else {
					Object.assign(this.currentMedia, this.fileInfos[fileId])
					this.loadedMediaToCurrentDisplay()
				}
			}

			// preload x files before and after the current one and revoke/abort the rest
			for (let i = Math.max(0, index - this.preloadAmountBackward - 2); i <= Math.min(this.selectedFileIds.length - 1, index + this.preloadAmountForward + 2); i++) {
				if (i < index - this.preloadAmountBackward || i > index + this.preloadAmountForward) {
					if (this.loadedMedia[i] === true) {
						this.loadedMedia[i] = 'abort'
					}
					if (this.loadedMedia[i] && this.loadedMedia[i].startsWith('blob:')) {
						URL.revokeObjectURL(this.loadedMedia[i])
						this.loadedMedia[i] = null
					}
				} else if (i !== index) {
					this.preloadMedia(i)
				}
			}

		},
		handlePrevious() {
			this.setViewMediaIndex(Math.max(0, this.currentMediaIndex - 1))
		},
		handleNext() {
			this.setViewMediaIndex(Math.min(this.selectedFileIds.length - 1, this.currentMediaIndex + 1))
		},
	},
}
</script>

<style lang="scss" scoped>
.test-files-pickers {
	width: 100%;
	max-width: 600px;
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 30px auto;
	padding: 20px;

	p,
	button {
		color: white;
		margin: 10px 0;
	}
}

.media-container-fullscreen {
	position: fixed;
	/* Cover the viewport */
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;

	height: 100vh;
	/* Fill the viewport */
	width: 100vw;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: black;
	/* Optional background */
}

.media-container {
	position: relative;
	/* Change to relative for normal layout */
	width: 100%;
	height: 60vh;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: black;
	z-index: 10000;
}

.left-button,
.right-button {
	background: rgba(0, 0, 0, 0.5);
	/* Button background */
	border: none;
	/* Remove border */
	color: white;
	/* Text color */
	padding: 5px 5px;
	/* Padding */
	border-radius: 100%;
	/* Rounded corners */
	cursor: pointer;
	/* Pointer on hover */
}

.icon {
	display: flex;
	align-items: center;
	/* Center icon vertically */
}

img,
video {
	max-width: 100%;
	/* Fit within the container */
	max-height: 100%;
	object-fit: contain;
	/* Maintain aspect ratio */
}

.scroll-buttons {
	color: white;
	position: absolute;
	/* Position buttons relative to the container */
	bottom: 60px;
	right: 10px;
	/* Center vertically */
	transform: translateY(-50%);
	/* Adjust for centering */
	display: flex;
	flex-direction: column;
	align-items: end;
	gap: 10px;
	width: 100%;
}

.toggle-fullscreen {
	position: absolute;
	/* Position the toggle button */
	bottom: 10px;
	/* Adjust as needed */
	right: 10px;
}

.toggle-auto-play {
	position: absolute;
	/* Position the toggle button */
	bottom: 10px;
	/* Adjust as needed */
	left: 50px;
}

.autoplay-control {
	background-color: #1e1e1e;
	/* Dark background */
	color: #ffffff;
	/* Light text color */
	padding: 20px 20px;
	border-radius: 10px;
	/* Rounded corners */
	max-width: 800px;
	/* Max width for the container */
	margin: auto;
	/* Center the container */
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
	/* Shadow for depth */
}

h2 {
	text-align: center;
	/* Center the heading */
}

.slider-container {
	flex-direction: row;
}

label {
	display: block;
	/* Block display for label */
	margin-bottom: 10px;
	/* Space below the label */
	font-weight: bold;
	/* Bold label text */
}

input[type="range"] {
	width: 100%;
	/* Make the slider full width */
	-webkit-appearance: none;
	/* Remove default styling */
	background: #444;
	/* Background for the slider track */
	border-radius: 5px;
	/* Rounded track */
	height: 8px;
	/* Height of the track */
	outline: none;
	/* Remove outline */
}

input[type="range"]::-webkit-slider-thumb {
	-webkit-appearance: none;
	/* Remove default thumb styling */
	appearance: none;
	/* Remove default thumb styling */
	width: 20px;
	/* Thumb width */
	height: 20px;
	/* Thumb height */
	background: #ffffff;
	/* Thumb color */
	border-radius: 50%;
	/* Rounded thumb */
	cursor: pointer;
	/* Pointer cursor on hover */
}

input[type="range"]::-moz-range-thumb {
	width: 20px;
	/* Thumb width */
	height: 20px;
	/* Thumb height */
	background: #ffffff;
	/* Thumb color */
	border-radius: 50%;
	/* Rounded thumb */
	cursor: pointer;
	/* Pointer cursor on hover */
}

.loader {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 10010;
	flex-direction: column;
}

.loader_local {
	position: relative;
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
}

.loader__spinner {
	border: 8px solid rgba(255, 255, 255, 0.3);
	border-top: 8px solid #ffffff;
	border-radius: 50%;
	width: 50px;
	height: 50px;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
	}
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}

</style>
