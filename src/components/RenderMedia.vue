<template>
	<div class="zoom-container"
		:style="{ transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`, touchAction: 'none' }"
		@touchstart="onTouchStart"
		@touchmove="onTouchMove"
		@touchend="onTouchEnd">
		<img
			v-if="mediaType.startsWith('image')"
			:src="selectedUrl"
			alt="Selected image"
			:class="animationEnabled && restartAnmimation ? 'animate' : ''"
			:style="animationEnabled ? animation : {}"
			@touchstart.prevent
			@touchmove.prevent>
		<video
			v-else-if="mediaType.startsWith('video')"
			:src="selectedUrl"
			controls
			autoplay
			v-bind="videoAttributes"
			@ended="handleVideoEnded" />
	</div>
</template>

<script>
export default {
	props: {
		selectedUrl: {
			type: String,
			required: true,
		},
		mediaType: {
			type: String,
			required: true,
		},
		videoAttributes: {
			type: Object,
			default: () => ({}),
		},
		animation: {
			type: Object,
			required: true,
		},
		animationEnabled: {
			type: Boolean,
			default: false,
		},
		videoEndedHandler: {
			type: Function,
			default: () => {},
		},
	},
	data() {
		return {
			scale: 1,
			initialDistance: 0,
			isZooming: false,
			isScrolling: false,
			startX: 0,
			startY: 0,
			translateX: 0,
			translateY: 0,
			restartAnmimation: false,
			scrollX: 0,
		}
	},
	watch: {
		selectedUrl() {
			// Reset zoom and translation when the image changes
			this.scale = 1
			this.translateX = 0
			this.translateY = 0
			this.restartAnmimation = false
			this.$nextTick(() => {
				setTimeout(() => {
					this.restartAnmimation = true
				}, 100)
			})
		},
	},
	methods: {
		onTouchStart(event) {
			if (event.touches.length === 2 && this.mediaType.startsWith('image')) {
				this.isScrolling = false
				this.isZooming = true
				this.initialDistance = this.getDistance(event.touches)
				this.startX = event.touches[0].clientX
				this.startY = event.touches[0].clientY
			} else if (event.touches.length === 1 && this.mediaType.startsWith('image')) {
				// allow default touch behavior
				this.isZooming = false
				this.isScrolling = true
				this.scrollX = event.touches[0].clientX

			}
		},
		onTouchMove(event) {
			if (this.isZooming && event.touches.length === 2) {
				// do event prevent default to avoid scrolling
				event.preventDefault()
				const currentDistance = this.getDistance(event.touches)
				const scaleChange = currentDistance / this.initialDistance
				this.scale = Math.max(1, Math.min(this.scale * scaleChange, 3)) // Limit scale between 1 and 3
				this.initialDistance = currentDistance // Update initial distance for the next move

				// Calculate translation
				const dx = event.touches[0].clientX - this.startX
				const dy = event.touches[0].clientY - this.startY
				this.translateX += dx
				this.translateY += dy

				// Update start positions
				this.startX = event.touches[0].clientX
				this.startY = event.touches[0].clientY
			} else {
				if (this.isScrolling) {
					event.preventDefault()
					const dx = event.touches[0].clientX - this.scrollX
					this.translateX += dx
					this.scrollX = event.touches[0].clientX
				}
			}
		},
		onTouchEnd(event) {
			if (event.touches.length < 2) {
				if (this.isScrolling) {
					this.isScrolling = false
					// handle if scroll to the left or right if needed using percentage of the screen width)
					if (this.translateX > 50) {
						this.translateX = 0
						this.$emit('right-swipe')
					} else if (this.translateX < -50) {
						this.translateX = 0
						this.$emit('left-swipe')
					}
				}
				this.isZooming = false
				// Reset translation when touch ends
				this.translateX = 0
				this.translateY = 0
			}
		},
		getDistance(touches) {
			const dx = touches[0].clientX - touches[1].clientX
			const dy = touches[0].clientY - touches[1].clientY
			return Math.sqrt(dx * dx + dy * dy)
		},
		handleVideoEnded() {
			this.videoEndedHandler()
		},
	},
}
</script>

<style scoped>
.zoom-container {
	display: flex;
	justify-content: center;
	align-items: center;
	overflow: hidden;
	width: 100%;
	height: 100%;
	background-color: #000;
	transition: transform 0.1s ease; /* Smooth zoom transition */
}

.zoom-container img,
.zoom-container video {
	max-width: 100%;
	max-height: 100%;
	object-fit: contain;
}

.animate {
	animation: translateMovement var(--animation-duration) ease-out forwards,
	           scaleMovement var(--animation-duration) ease-out forwards;
}

@keyframes translateMovement {
    0% {
        transform: translate(var(--start-x), var(--start-y));
    }
    100% {
        transform: translate(var(--end-x), var(--end-y));
    }
}

@keyframes scaleMovement {
    0% {
        transform: scale(var(--start-scale));
    }
    100% {
        transform: scale(var(--end-scale));
    }
}
</style>
