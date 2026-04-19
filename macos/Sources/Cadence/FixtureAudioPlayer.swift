@preconcurrency import AVFoundation
import Foundation

/// Streams a WAV file at real-time pace as PCM16, 16kHz, mono, base64 100ms chunks.
final class FixtureAudioPlayer: AudioSource {
    var onAudioChunk: ((String) -> Void)?

    private let path: String
    private var timer: DispatchSourceTimer?
    private var chunks: [String] = []
    private var cursor = 0

    init(path: String) {
        self.path = path
    }

    func start() throws {
        let url = URL(fileURLWithPath: path)
        let file = try AVAudioFile(forReading: url)

        let targetFormat = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: 16000,
            channels: 1,
            interleaved: true
        )!

        guard let converter = AVAudioConverter(from: file.processingFormat, to: targetFormat) else {
            throw NSError(
                domain: "FixtureAudio", code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Cannot create converter for \(path)"])
        }

        guard let src = AVAudioPCMBuffer(
            pcmFormat: file.processingFormat,
            frameCapacity: AVAudioFrameCount(file.length)
        ) else {
            throw NSError(domain: "FixtureAudio", code: 2,
                userInfo: [NSLocalizedDescriptionKey: "Cannot allocate source buffer"])
        }
        try file.read(into: src)

        let ratio = targetFormat.sampleRate / file.processingFormat.sampleRate
        let outCapacity = AVAudioFrameCount(Double(src.frameLength) * ratio) + 1024
        guard let dst = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: outCapacity) else {
            throw NSError(domain: "FixtureAudio", code: 3,
                userInfo: [NSLocalizedDescriptionKey: "Cannot allocate converted buffer"])
        }

        nonisolated(unsafe) var fed = false
        var convError: NSError?
        converter.convert(to: dst, error: &convError) { _, status in
            if fed { status.pointee = .endOfStream; return nil }
            fed = true
            status.pointee = .haveData
            return src
        }
        if let convError { throw convError }

        guard let int16 = dst.int16ChannelData else {
            throw NSError(domain: "FixtureAudio", code: 4,
                userInfo: [NSLocalizedDescriptionKey: "No channel data after conversion"])
        }

        let totalSamples = Int(dst.frameLength)
        let data = Data(bytes: int16[0], count: totalSamples * 2)
        let chunkBytes = 3200

        chunks.removeAll(keepingCapacity: false)
        var offset = 0
        while offset < data.count {
            let end = min(offset + chunkBytes, data.count)
            chunks.append(data[offset..<end].base64EncodedString())
            offset = end
        }

        cursor = 0
        let queue = DispatchQueue(label: "com.cadence.fixture-audio")
        let t = DispatchSource.makeTimerSource(queue: queue)
        t.schedule(deadline: .now() + .milliseconds(100), repeating: .milliseconds(100))
        t.setEventHandler { [weak self] in
            guard let self else { return }
            if self.cursor >= self.chunks.count {
                self.timer?.cancel()
                self.timer = nil
                return
            }
            self.onAudioChunk?(self.chunks[self.cursor])
            self.cursor += 1
        }
        t.resume()
        self.timer = t
    }

    func stop() {
        timer?.cancel()
        timer = nil
        chunks.removeAll(keepingCapacity: false)
        cursor = 0
    }
}
