export type CameraError =
  | 'not_allowed'
  | 'not_found'
  | 'overconstrained'
  | 'not_readable'
  | 'timeout'
  | 'unknown'

export type CaptureResult = {
  blob: Blob
  url: string
}

