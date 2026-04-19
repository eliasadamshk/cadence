import Foundation

protocol AudioSource: AnyObject {
    var onAudioChunk: ((String) -> Void)? { get set }
    func start() throws
    func stop()
}
