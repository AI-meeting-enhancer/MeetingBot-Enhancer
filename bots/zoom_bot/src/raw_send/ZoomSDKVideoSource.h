
#ifndef ZOOM_SDK_VIDEO_SOURCE_H
#define ZOOM_SDK_VIDEO_SOURCE_H

#include "rawdata/rawdata_video_source_helper_interface.h"
#include "../util/Log.h"

using namespace ZOOMSDK;
using namespace std;

struct Frame {
    char* data;
    unsigned int width;
    unsigned int height;
    unsigned int len;
};

class ZoomSDKVideoSource : public IZoomSDKVideoSource    {
    void onInitialize(IZoomSDKVideoSender* sender, IList<VideoSourceCapability >* support_cap_list, VideoSourceCapability& suggest_cap) override;
    void onPropertyChange(IList<VideoSourceCapability >* support_cap_list, VideoSourceCapability suggest_cap) override;
    void onStartSend() override;
    void onStopSend() override;
    void onUninitialized() override;

    IZoomSDKVideoSender* m_videoSender;
    unsigned int m_height;
    unsigned int m_width;
    bool m_isReady;

public:
    ZoomSDKVideoSource();

    IZoomSDKVideoSender* getSender() const;

    bool isReady();
    void setWidth(const unsigned int& width);
    void setHeight(const unsigned int& height);
};


#endif //ZOOM_SDK_VIDEO_SOURCE_H
