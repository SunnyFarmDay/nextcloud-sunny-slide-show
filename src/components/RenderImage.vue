<template>
  <div class="zoom-container" @touchstart="onTouchStart" @touchmove.prevent="onTouchMove" @touchend="onTouchEnd"
    :style="{ transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`, touchAction: 'none' }">
    <img :src="selectedUrl" alt="Selected image" />
  </div>
</template>

<script>
export default {
  props: {
    selectedUrl: {
      type: String,
      required: true,
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
        this.isZooming = true;
        this.initialDistance = this.getDistance(event.touches);
        this.startX = event.touches[0].clientX;
        this.startY = event.touches[0].clientY;
      }
    },
    onTouchMove(event) {
      if (this.isZooming && event.touches.length === 2) {
        const currentDistance = this.getDistance(event.touches);
        const scaleChange = currentDistance / this.initialDistance;
        this.scale = Math.max(1, Math.min(this.scale * scaleChange, 3)); // Limit scale between 1 and 3
        this.initialDistance = currentDistance; // Update initial distance for the next move

        // Calculate translation
        const dx = event.touches[0].clientX - this.startX;
        const dy = event.touches[0].clientY - this.startY;
        this.translateX += dx;
        this.translateY += dy;

        // Update start positions
        this.startX = event.touches[0].clientX;
        this.startY = event.touches[0].clientY;
      }
    },
    onTouchEnd(event) {
      if (event.touches.length < 2) {
        this.isZooming = false;
        // Reset translation when touch ends
        this.translateX = 0;
        this.translateY = 0;
      }
    },
    getDistance(touches) {
      const dx = touches[0].clientX - touches[1].clientX;
      const dy = touches[0].clientY - touches[1].clientY;
      return Math.sqrt(dx * dx + dy * dy);
    },
  },
};
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
  transition: transform 0.1s ease;
  /* Smooth zoom transition */
}

.zoom-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}
</style>