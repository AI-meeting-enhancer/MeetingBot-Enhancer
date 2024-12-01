#include "ZoomSDKAudioRawDataDelegate.h"
#include "zoom_sdk_def.h" // or the correct header file that defines AudioType
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, int> userList; //[{no:0,name:"Bob",node_id:23452}, {no:1, name:"John",node_id:32421}]

ZoomSDKAudioRawDataDelegate::ZoomSDKAudioRawDataDelegate(bool useMixedAudio = true, bool transcribe = false) : m_useMixedAudio(useMixedAudio), m_transcribe(transcribe)
{
    server.start();
}

void ZoomSDKAudioRawDataDelegate::onMixedAudioRawDataReceived(AudioRawData *data)
{
    if (!m_useMixedAudio)
        return;

    // write to socket
    if (m_transcribe)
    {
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

void ZoomSDKAudioRawDataDelegate::onOneWayAudioRawDataReceived(AudioRawData *data, uint32_t node_id)
{
    if (m_useMixedAudio)
        return;

    if (data == nullptr)
    {
        Log::error("Received null AudioRawData");
        return;
    }

    int bufferLen = data->GetBufferLen();
    if (bufferLen <= 0)
    {
        Log::error("Received audio data with invalid length");
        return;
    }

    // Check if the current speaker is a new member
    auto it = userList.find(std::to_string(node_id));
    int index = 0;

    if (it == userList.end()) // if current speaker is new member
    {
        index = userList.size();                   // Use the current size as the index
        userList[std::to_string(node_id)] = index; // Store the new user with their index
        Log::info(std::to_string(index));
    }
    else
    {
        index = it->second; // Retrieve the existing index
        Log::info(std::to_string(index));
    }

    // Create a buffer to hold the index and audio data
    std::vector<char> buffer(sizeof(int) + bufferLen);
    // Convert index to little-endian byte order
    uint32_t index_le = htole32(index); // Use htole32 for little-endian conversion
    memcpy(buffer.data(), &index_le, sizeof(uint32_t));
    memcpy(buffer.data() + sizeof(int), data->GetBuffer(), bufferLen); // Copy the audio data into the buffer

    // Write to socket
    if (m_transcribe)
    {
        server.writeBuf(buffer.data(), buffer.size()); // Send the combined index and audio data
    }
}

void ZoomSDKAudioRawDataDelegate::onShareAudioRawDataReceived(AudioRawData *data)
{
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
