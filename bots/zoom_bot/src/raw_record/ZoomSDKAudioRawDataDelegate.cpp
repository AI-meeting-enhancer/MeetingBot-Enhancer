#include "ZoomSDKAudioRawDataDelegate.h"
#include "zoom_sdk_def.h" // or the correct header file that defines AudioType
#include <unordered_map>
#include <vector>
#include "../Zoom.h"

std::unordered_map<std::string, int> userList; //{ node_id:index, 23423432:1, 623143223:2 }

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


    // Retrieve display name using node_id
    std::string displayName = Zoom::getInstance().getParticipantsCtl()->GetUserByUserID(node_id)->GetUserName();

    // Check if display name contains "Bot"
    // if (displayName.find("Bot") != std::string::npos)
    // {
    //     Log::info("Skipping audio stream for Bot: " + displayName);
    //     return; // Do not send audio data via socket
    // }

    // Check if the current speaker is a new member
    auto it = userList.find(std::to_string(node_id));
    int index = 0;

    if (it == userList.end()) // if current speaker is new member
    {
        index = userList.size();                   // Use the current size as the index
        userList[std::to_string(node_id)] = index; // Store the new user with their index
    }
    else
    {
        index = it->second; // Retrieve the existing index
    }


    // Define fixed size for user identification part
    const size_t fixedUserIdSize = sizeof(int) + 50; // 50 bytes for the display name
    std::vector<char> buffer(fixedUserIdSize + bufferLen);

    // Convert index to little-endian byte order
    uint32_t index_le = htole32(index); // Use htole32 for little-endian conversion
    memcpy(buffer.data(), &index_le, sizeof(uint32_t));

    // Copy display name to the buffer
    strncpy(buffer.data() + sizeof(uint32_t), displayName.c_str(), 50); // Ensure it fits within 50 bytes
    // Fill the remaining bytes with null characters if the display name is shorter than 50 bytes
    memset(buffer.data() + sizeof(uint32_t) + displayName.length(), 0, 50 - displayName.length());

    // Copy the audio data into the buffer
    memcpy(buffer.data() + fixedUserIdSize, data->GetBuffer(), bufferLen); // Copy the audio data

    // Write to socket
    if (m_transcribe)
    {
        server.writeBuf(buffer.data(), buffer.size()); // Send the combined index, display name, and audio data
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

}

void ZoomSDKAudioRawDataDelegate::setDir(const string &dir)
{
    m_dir = dir;
}

void ZoomSDKAudioRawDataDelegate::setFilename(const string &filename)
{
    m_filename = filename;
}
