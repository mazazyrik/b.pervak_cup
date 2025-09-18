import { useCallback, useEffect, useRef, useState } from 'react'
import { withTimeout, sleep } from '@shared/lib/async'
import { isAndroid, isIOS } from '@shared/lib/platform'
import { drawVideoToCanvas, toBlob } from '@shared/lib/image'
import type { CameraError, CaptureResult } from './types'

type UseCamera = {
  videoRef: React.RefObject<HTMLVideoElement>
  isActive: boolean
  error: CameraError | null
  fallbackEnabled: boolean
  start: (constraints?: MediaStreamConstraints) => Promise<void>
  stop: () => void
  capture: () => Promise<CaptureResult>
}

export function useCamera(): UseCamera {
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [isActive, setIsActive] = useState(false)
  const [error, setError] = useState<CameraError | null>(null)
  const [fallbackEnabled, setFallbackEnabled] = useState(false)

  const stop = useCallback(() => {
    const s = streamRef.current
    if (s) s.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    setIsActive(false)
  }, [])

  const start = useCallback(async (custom?: MediaStreamConstraints) => {
    setError(null)
    setFallbackEnabled(false)
    const constraints: MediaStreamConstraints = custom || {
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    }
    try {
      let s: MediaStream | null = null
      try {
        s = await withTimeout(navigator.mediaDevices.getUserMedia(constraints), 4000)
      } catch {
        s = await withTimeout(
          navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false }),
          4000
        )
      }
      streamRef.current = s
      const v = videoRef.current
      if (!v) throw new Error('no_video')
      v.srcObject = s
      v.muted = true
      v.playsInline = true
      try {
        await v.play()
      } catch {}
      setIsActive(true)
    } catch (e: any) {
      if (e?.name === 'NotAllowedError') setError('not_allowed')
      else if (e?.name === 'NotFoundError') setError('not_found')
      else if (e?.name === 'OverconstrainedError') setError('overconstrained')
      else if (e?.name === 'NotReadableError') setError('not_readable')
      else if (e?.message === 'timeout') setError('timeout')
      else setError('unknown')
      setFallbackEnabled(true)
    }
  }, [])

  const capture = useCallback(async (): Promise<CaptureResult> => {
    const v = videoRef.current
    if (!v) throw new Error('no_video')
    const canvas = document.createElement('canvas')
    await drawVideoToCanvas(v, canvas)
    const blob = await toBlob(canvas, 'image/jpeg', 0.92)
    const url = URL.createObjectURL(blob)
    return { blob, url }
  }, [])

  useEffect(() => {
    const onVis = async () => {
      if (document.hidden) stop()
      else if (streamRef.current) await start().catch(() => {})
    }
    document.addEventListener('visibilitychange', onVis)
    const onOrient = async () => {
      for (let i = 0; i < 3; i++) {
        try {
          stop()
          await sleep(200 * Math.pow(2, i))
          await start()
          break
        } catch {}
      }
    }
    window.addEventListener('orientationchange', onOrient)
    return () => {
      document.removeEventListener('visibilitychange', onVis)
      window.removeEventListener('orientationchange', onOrient)
      stop()
    }
  }, [start, stop])

  useEffect(() => {
    if (isAndroid()) {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) setFallbackEnabled(true)
    }
  }, [])

  return { videoRef, isActive, error, fallbackEnabled, start, stop, capture }
}

