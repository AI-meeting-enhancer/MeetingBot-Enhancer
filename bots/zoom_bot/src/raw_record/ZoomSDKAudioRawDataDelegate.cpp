#include "ZoomSDKAudioRawDataDelegate.h"
#include <vector>


ZoomSDKAudioRawDataDelegate::ZoomSDKAudioRawDataDelegate(bool useMixedAudio = true, bool transcribe = false) : m_useMixedAudio(useMixedAudio), m_transcribe(transcribe){
    server.start();
}

void ZoomSDKAudioRawDataDelegate::onMixedAudioRawDataReceived(AudioRawData *data) {
    if (!m_useMixedAudio) return;

    // write to socket
    if (m_transcribe) {
        server.writeBuf(data->GetBuffer(), data->GetBufferLen());
    }

    // or write to file
    if (m_dir.empty())
        return Log::error("Output Directory cannot be blank");


    if (m_filename.empty())
        m_filename = "test.pcm";


    stringstream path;
    path << m_dir << "/" << m_filename;
    
    // uncomment the below to enable recording to file
    // writeToFile(path.str(), data);
}

void ZoomSDKAudioRawDataDelegate::setUser_DisplayName(uint32_t node_id, const std::string& displayName) {
    m_userDisplayNames[node_id] = displayName;
}

void ZoomSDKAudioRawDataDelegate::onOneWayAudioRawDataReceived(AudioRawData* data, uint32_t node_id) {
    Log::info(m_useMixedAudio+"d");
    if (m_useMixedAudio) return;

    // Prepare the socket message
    const unsigned char* buffer = reinterpret_cast<const unsigned char*>(data->GetBuffer());
    int bufferLen = data->GetBufferLen();

    // Get the display name for the current user
    std::string displayName = m_userDisplayNames[node_id];

    // Create a message to send: node_id (1 byte) + display name length (1 byte) + display name + audio data
    std::vector<unsigned char> message;
    message.push_back(static_cast<unsigned char>(node_id)); // Node ID
    message.push_back(static_cast<unsigned char>(displayName.length())); // Length of display name
    message.insert(message.end(), displayName.begin(), displayName.end()); // Display name
    message.insert(message.end(), buffer, buffer + bufferLen); // Audio data

    // Send the audio data to the socket
    int ret = server.writeBuf(message.data(), message.size());
    if (ret < 0) {
        Log::error("Failed to send audio data to socket for node " + std::to_string(node_id));
    }
}
void ZoomSDKAudioRawDataDelegate::onShareAudioRawDataReceived(AudioRawData* data) {
    stringstream ss;
    ss << "Shared Audio Raw data: " << data->GetBufferLen() / 10 << "k at " << data->GetSampleRate() << "Hz";
    Log::info(ss.str());
}


void ZoomSDKAudioRawDataDelegate::writeToFile(const string &path, AudioRawData *data)
{
    static std::ofstream file;
	file.open(path, std::ios::out | std::ios::binary | std::ios::app);
    
	if (!file.is_open())
        return Log::error("failed to open audio file path: " + path);
	
    file.write(data->GetBuffer(), data->GetBufferLen());

    file.close();
	file.flush();

    stringstream ss;
    ss << "Writing " << data->GetBufferLen() << "b to " << path << " at " << data->GetSampleRate() << "Hz";

    // Log::info(ss.str());
}

void ZoomSDKAudioRawDataDelegate::setDir(const string &dir)
{
    m_dir = dir;
}

void ZoomSDKAudioRawDataDelegate::setFilename(const string &filename)
{
    m_filename = filename;
}
