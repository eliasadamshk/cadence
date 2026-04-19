@preconcurrency import AVFoundation
import Foundation

final class AudioCapture: AudioSource {
    private var engine: AVAudioEngine?
    var onAudioChunk: ((String) -> Void)?

    func start() throws {
        guard AVCaptureDevice.default(for: .audio) != nil else {
            throw NSError(
                domain: "AudioCapture", code: 3,
                userInfo: [NSLocalizedDescriptionKey: "No microphone detected — connect a USB mic, headset, or AirPods and try again."])
        }

        let newEngine = AVAudioEngine()
        let input = newEngine.inputNode
        let bus: AVAudioNodeBus = 0
        let nativeFormat = input.inputFormat(forBus: bus)

        guard nativeFormat.channelCount > 0, nativeFormat.sampleRate > 0 else {
            throw NSError(
                domain: "AudioCapture", code: 2,
                userInfo: [NSLocalizedDescriptionKey: "Microphone not available — check System Settings > Privacy > Microphone, and ensure a default input device is set."])
        }

        let targetFormat = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: 16000,
            channels: 1,
            interleaved: true
        )!

        guard let converter = AVAudioConverter(from: nativeFormat, to: targetFormat) else {
            throw NSError(
                domain: "AudioCapture", code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Cannot create audio converter"])
        }

        let frameCapacity: AVAudioFrameCount = 3200

        input.installTap(onBus: bus, bufferSize: 1024, format: nativeFormat) { [weak self] buffer, _ in
            guard let outputBuffer = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: frameCapacity) else { return }

            var error: NSError?
            converter.convert(to: outputBuffer, error: &error) { _, outStatus in
                outStatus.pointee = .haveData
                return buffer
            }

            if error != nil { return }
            guard let int16Data = outputBuffer.int16ChannelData else { return }
            let count = Int(outputBuffer.frameLength)
            guard count > 0 else { return }
            let data = Data(bytes: int16Data[0], count: count * 2)
            let base64 = data.base64EncodedString()
            self?.onAudioChunk?(base64)
        }

        try newEngine.start()
        engine = newEngine
    }

    func stop() {
        guard let engine else { return }
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        self.engine = nil
    }
}
