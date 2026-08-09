import { useRef, useState } from 'react'
import { FiUploadCloud, FiFile } from 'react-icons/fi'

const MAX_SIZE_MB = 5

const ResumeUploadZone = ({ onFileSelected, isUploading, uploadProgress, hasExistingResume }) => {
  const inputRef = useRef(null)
  const [isDragActive, setIsDragActive] = useState(false)
  const [validationError, setValidationError] = useState('')

  const validateAndSelect = (file) => {
    if (!file) return
    setValidationError('')

    if (file.type !== 'application/pdf') {
      setValidationError('Only PDF files are supported.')
      return
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setValidationError(`File exceeds the ${MAX_SIZE_MB}MB size limit.`)
      return
    }
    onFileSelected(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragActive(false)
    const file = event.dataTransfer.files?.[0]
    validateAndSelect(file)
  }

  const handleInputChange = (event) => {
    const file = event.target.files?.[0]
    validateAndSelect(file)
    event.target.value = ''
  }

  return (
    <div>
      <div
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragActive(true)
        }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed px-6 py-14 text-center transition-colors ${
          isDragActive ? 'border-accent bg-accent/5' : 'border-slate-800 bg-slate-950/40'
        }`}
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <FiUploadCloud size={26} />
        </span>

        {isUploading ? (
          <div className="w-full max-w-xs">
            <p className="mb-2 text-sm text-slate-300">Analyzing your resume...</p>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-accent transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <>
            <div>
              <p className="text-sm font-medium text-slate-200">Drag and drop your resume here</p>
              <p className="mt-1 text-xs text-slate-500">PDF only, up to {MAX_SIZE_MB}MB</p>
            </div>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="flex items-center gap-2 rounded-2xl bg-accent px-5 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90"
            >
              <FiFile size={15} />
              {hasExistingResume ? 'Replace Resume' : 'Choose File'}
            </button>
          </>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          onChange={handleInputChange}
          className="hidden"
        />
      </div>

      {validationError && <p className="mt-2 text-xs text-red-400">{validationError}</p>}
    </div>
  )
}

export default ResumeUploadZone