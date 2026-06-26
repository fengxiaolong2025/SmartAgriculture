import { onUnmounted } from 'vue'

export function usePolling(fn, interval = 3000) {
  let timer = null

  const start = () => {
    fn()
    timer = setInterval(fn, interval)
  }

  const stop = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onUnmounted(stop)

  return { start, stop }
}
