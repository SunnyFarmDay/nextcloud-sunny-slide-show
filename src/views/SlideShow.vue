<template>
	<NcContent app-name="sunny-slide-show">
		<template v-if="loading">
			<div class="loader">
				<div class="loader__spinner"></div>
			</div>
		</template>
		<NcAppContent>
			<div class="test-files-pickers">
				<div class="slider-container">
					<h2>{{ t('ui_example', 'Slide Show') }}</h2>
					<NcButton @click="selectTestFile">
						{{ t('ui_example', 'Select test file') }}
					</NcButton>
					<NcButton @click="getImageFromDav">
						{{ t('ui_example', 'Get image from DAV') }}
					</NcButton>
					<div class="autoplay-control">
						<div class="slider-container">
							<label for="autoplay-slider">Autoplay Speed: {{ autoPlayInterval }} ms</label>
							<input id="autoplay-slider" type="range" min="1000" max="10000" step="100"
								v-model="autoPlayInterval" />
						</div>
						<p>Current Autoplay Interval: {{ autoPlayInterval }} ms</p>
					</div>
				</div>

				<div ref="fullscreenDiv" :class="isFullscreen ? 'media-container-fullscreen' : 'media-container'">
					<div v-if="loadingMedia" class="loader_local">
						<div class="loader__spinner"></div>
					</div>
					<div v-else>
						<RenderImage v-if="isImage" :selectedUrl="selectedUrl" />
						<video v-else-if="isVideo" :src="selectedUrl" controls autoplay @ended="handleVideoEnd" />
					</div>
					<div class="scroll-buttons">
						<button @click="handlePrevious" class="left-button">
							<i class="ri-arrow-left-double-line"></i>
						</button>
						<button @click="handleNext" class="right-button">
							<i class="ri-arrow-right-double-line"></i>
						</button>
					</div>
					<NcButton class="toggle-fullscreen" @click="toggleFullscreen">
						{{ isFullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}
					</NcButton>
					<NcButton class="toggle-auto-play" @click="toggleAutoPlay">
						{{ autoPlay ? 'Stop' : 'Play' }}
					</NcButton>
				</div>
				<p>{{ testResponse }}</p>

				<template v-if="selectedFileIds.length > 0">
					<h3>{{ t('ui_example', 'Selected from File Actions Menu:') }}</h3>
					<p><b>{{ t('ui_example', 'File List:') }}</b> {{ fileList }}</p>
				</template>
			</div>
		</NcAppContent>
	</NcContent>
</template>

<script>
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'
import { RiArrowLeftSLine, RiArrowRightSLine } from 'react-icons/ri'
import { getFilePickerBuilder } from '@nextcloud/dialogs'
import { formatBytes, requestFileInfo, searchByFileId } from '../files.js'

import '@nextcloud/dialogs/style.css'
import Navigation from '../components/Navigation.vue'
import NcContent from '@nextcloud/vue/dist/Components/NcContent.js'
import NcAppContent from '@nextcloud/vue/dist/Components/NcAppContent.js'
import { NcAppNavigation } from '@nextcloud/vue'
import RenderImage from '../components/RenderImage.vue'

export default {
	name: 'SlideShow',
	components: {
		Navigation,
		RenderImage,
		NcContent,
		NcButton,
		NcAppContent,
	},
	data() {
		return {
			loading: true,
			selectedFile: '',
			selectedFileInfo: [],
			selectedFileIds: [],
			selectedFilesInfo: {},
			selectedUrl: '',
			fileList: '',
			testResponse: '',
			currentMediaIndex: 0,
			loadedMedia: {},
			preloadAmount: 10,
			lastPollLoading: null,
			isFullscreen: false,
			autoPlay: false,
			autoPlayInterval: 3000,
			autoPlayTimeout: null,
			loadingMedia: false,
		}
	},
	mounted() {
		document.addEventListener('fullscreenchange', this.handleFullscreenChange);
		document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange); // Safari
		document.addEventListener('mozfullscreenchange', this.handleFullscreenChange); // Firefox
		document.addEventListener('MSFullscreenChange', this.handleFullscreenChange); // IE/Edge
	},
	beforeDestroy() {
		document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
		document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
		document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange);
		document.removeEventListener('MSFullscreenChange', this.handleFullscreenChange);
	},
	computed: {
		formattedSize() {
			return formatBytes(this.selectedFileInfo?.size || 0) || ''
		},
		isImage() {
			return this.selectedFileInfo?.mime?.startsWith('image')
		},
		isVideo() {
			return this.selectedFileInfo?.mime?.startsWith('video')
		},
	},
	beforeMount() {
		// Load files info from fileIds query parameter if exists
		if (this.$route.query.fileIds) {
			this.selectedFileIds = this.$route.query.fileIds.split(',').map(Number)
			this.selectedFilesInfo = new Array(this.selectedFileIds.length) // Initialize the array

			const filePromises = this.selectedFileIds.map(fileId => {
				return searchByFileId(fileId).then(fileInfo => {
					const fileId = fileInfo.props.fileid
					// find the index of the file in the list
					const index = this.selectedFileIds.indexOf(fileId)
					this.selectedFilesInfo[index] = fileInfo
				})
			})

			Promise.all(filePromises).then(() => {
				this.fileList = this.selectedFilesInfo.map(fileInfo => fileInfo.filename).join('\n')
				this.setViewMediaIndex(0)
				this.loading = false
			})
		}
	},
	methods: {
		toggleAutoPlay() {
			this.autoPlay = !this.autoPlay
			if (this.autoPlay) {
				this.setViewMediaIndex(this.currentMediaIndex)
			} else {
				clearTimeout(this.autoPlayTimeout)
			}
		},
		handleVideoEnd() {
			console.log('Video ended')
			if (this.autoPlay) {
				this.setViewMediaIndex(Math.min(this.selectedFilesInfo.length - 1, this.currentMediaIndex + 1))
			}
		},
		handleFullscreenChange() {
			this.isFullscreen = !!document.fullscreenElement;
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
				this.$store.dispatch('loadImageFromDav', this.selectedFilesInfo[index].filename).then(url => {
					this.loadedMedia[index] = url
				}).catch(error => {
					console.error('Error fetching media:', error)
				})
			}
		},
		setUpAutoPlay() {
			if (this.autoPlay) {
				var isVideo = this.selectedFilesInfo[this.currentMediaIndex].mime.startsWith('video')
				if (this.autoPlayTimeout || isVideo) {
					clearTimeout(this.autoPlayTimeout)
				}
				if (isVideo) {
					return
				}
				this.autoPlayTimeout = setTimeout(() => {
					this.setViewMediaIndex(Math.min(this.selectedFilesInfo.length - 1, this.currentMediaIndex + 1))
				}, this.autoPlayInterval)
			}
		},
		setViewMediaIndex(index) {
			this.currentMediaIndex = index
			this.selectedFile = this.selectedFilesInfo[index].filename
			this.selectedFileInfo = this.selectedFilesInfo[index]

			// load the current media
			if (!this.loadedMedia[index]) {
				this.$store.dispatch('loadImageFromDav', this.selectedFilesInfo[index].filename).then(url => {
					this.loadedMedia[index] = url
					this.selectedUrl = url
					this.setUpAutoPlay()

				}).catch(error => {
					console.error('Error fetching media:', error)
				})
			} else {
				if (this.loadedMedia[index] === true) {
					this.loadingMedia = true
					console.log('Media not loaded yet, retrying in 100ms')
					if (this.lastPollLoading) {
						clearTimeout(this.lastPollLoading)
					}
					this.lastPollLoading = setTimeout(() => {
						this.setViewMediaIndex(index)
					}, 100)
				} else {
					this.loadingMedia = false
					this.selectedUrl = this.loadedMedia[index]
					this.setUpAutoPlay()
				}
			}

			// preload x files before and after the current one
			for (let i = Math.max(0, index - this.preloadAmount); i <= Math.min(this.selectedFilesInfo.length - 1, index + this.preloadAmount); i++) {
				if (i !== index) {
					this.preloadMedia(i)
				}
			}
		},
		handlePrevious() {
			this.setViewMediaIndex(Math.max(0, this.currentMediaIndex - 1))
		},
		handleNext() {
			this.setViewMediaIndex(Math.min(this.selectedFilesInfo.length - 1, this.currentMediaIndex + 1))
		},
		getFilesPicker(title) {
			return getFilePickerBuilder(title)
				.setMultiSelect(false)
				.setType(1)
				.allowDirectories(true)
				.build()
		},
		getImageFromDav() {
			console.log(this.selectedFile, this.selectedFileInfo)
			this.$store.dispatch('getImageFromDav', this.selectedFile).then(response => {
				console.log('Image fetched:', response)
				const blob = new Blob([response], { type: this.selectedFileInfo.getcontenttype })
				this.selectedUrl = URL.createObjectURL(blob)
			}).catch(error => {
				console.error('Error fetching image:', error)
			})
		},
		selectTestFile() {
			this.getFilesPicker(t('ui_example', 'Select test file')).pick().then(filePath => {
				this.selectedFile = filePath
				requestFileInfo(filePath).then(fileInfo => {
					this.selectedFileInfo = fileInfo
					this.getImageFromDav()
				})
			})
		},
		sendToExApp() {
			this.$store.dispatch('sendNextcloudFileToExApp', this.selectedFileInfo)
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
	height: 80vh;
	/* Set a maximum width */
	margin: 20px auto;
	/* Center the container with margin */
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: black;
	/* Optional background */
	padding: 10px;
	/* Add some padding */
	border-radius: 8px;
	/* Optional: rounded corners */
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
	object-fit: cover;
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
	padding: 20px;
	border-radius: 10px;
	/* Rounded corners */
	max-width: 400px;
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
	margin: 20px 0;
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
}

.loader_local {
	position: relative;
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
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
</style>
