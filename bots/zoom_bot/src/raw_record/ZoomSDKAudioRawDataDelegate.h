
#ifndef ZOOM_SDK_AUDIO_RAW_DATA_DELEGATE_H
#define ZOOM_SDK_AUDIO_RAW_DATA_DELEGATE_H

#include <iostream>
#include <fstream>
#include <unordered_map>
#include <sstream>

#include "zoom_sdk_raw_data_def.h"
#include "rawdata/rawdata_audio_helper_interface.h"

#include "../util/Log.h"
#include "../util/SocketServer.h"

using namespace std;
using namespace ZOOMSDK;

class ZoomSDKAudioRawDataDelegate : public IZoomSDKAudioRawDataDelegate {
    std::unordered_map<uint32_t, std::string> m_userDisplayNames; // Map to store display names

    SocketServer server;

    string m_dir = "out";
    string m_filename = "test.pcm";
    bool m_useMixedAudio;
    bool m_transcribe;

    void writeToFile(const string& path, AudioRawData* data);
public:

    // Add a method to set the display name for a user
    void setUser DisplayName(uint32_t node_id, const std::string& displayName);

    ZoomSDKAudioRawDataDelegate(bool useMixedAudio, bool transcribe);
    void setDir(const string& dir);
    void setFilename(const string& filename);

    void onMixedAudioRawDataReceived(AudioRawData* data) override;
    void onOneWayAudioRawDataReceived(AudioRawData* data, uint32_t node_id) override;
    void onShareAudioRawDataReceived(AudioRawData* data) override;

    void onOneWayInterpreterAudioRawDataReceived(AudioRawData* data_, const zchar_t* pLanguageName) override {};
};



#endif //ZOOM_SDK_AUDIO_RAW_DATA_DELEGATE_H
