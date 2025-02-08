<template>
	<div class="zoom-container"
		:style="{ transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`, touchAction: 'none' }"
		@touchstart="onTouchStart"
		@touchmove.prevent="onTouchMove"
		@touchend="onTouchEnd">
		<img
			v-if="mediaType.startsWith('image')"
			:src="selectedUrl"
			alt="Selected image"
			class="animate"
			:style="animationEnabled ? animation : {}">
		<video
			v-else-if="mediaType.startsWith('video')"
			:src="selectedUrl"
			controls
			autoplay
			v-bind="videoAttributes"
			@ended="handleVideoEnd" />
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
	},
	data() {
		return {
			scale: 1,
			initialDistance: 0,
			isZooming: false,
			startX: 0,
			startY: 0,
			translateX: 0,
			translateY: 0,
		}
	},
	methods: {
		onTouchStart(event) {
			if (event.touches.length === 2) {
				this.isZooming = true
				this.initialDistance = this.getDistance(event.touches)
				this.startX = event.touches[0].clientX
				this.startY = event.touches[0].clientY
			}
		},
		onTouchMove(event) {
			if (this.isZooming && event.touches.length === 2) {
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
			}
		},
		onTouchEnd(event) {
			if (event.touches.length < 2) {
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
		handleVideoEnd() {
			// Custom logic for when the video ends
			this.$emit('video-ended')
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
