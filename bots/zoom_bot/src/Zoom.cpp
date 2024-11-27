#include "Zoom.h"

// Configure the Zoom SDK with command line arguments
SDKError Zoom::config(int ac, char** av) {
    auto status = m_config.read(ac, av); // Read configuration from command line arguments
    if (status) {
        Log::error("failed to read configuration"); // Log error if configuration fails
        return SDKERR_INTERNAL_ERROR; // Return internal error status
    }

    return SDKERR_SUCCESS; // Return success status
}

// Initialize the Zoom SDK
SDKError Zoom::init() { 
    InitParam initParam; // Structure to hold initialization parameters

    auto host = m_config.zoomHost().c_str(); // Get the Zoom host from configuration

    initParam.strWebDomain = host; // Set web domain for the SDK
    initParam.strSupportUrl = host; // Set support URL for the SDK

    initParam.emLanguageID = LANGUAGE_English; // Set the language for the SDK

    initParam.enableLogByDefault = true; // Enable logging by default
    initParam.enableGenerateDump = true; // Enable generation of dumps for debugging

    auto err = InitSDK(initParam); // Initialize the SDK with parameters
    if (hasError(err)) {
        Log::error("InitSDK failed"); // Log error if initialization fails
        return err; // Return error status
    }
    
    return createServices(); // Create necessary services after initialization
}

// Create services required for the Zoom SDK
SDKError Zoom::createServices() {
    auto err = CreateMeetingService(&m_meetingService); // Create meeting service
    if (hasError(err)) return err; // Return error if service creation fails

    err = CreateSettingService(&m_settingService); // Create settings service
    if (hasError(err)) return err; // Return error if service creation fails

    auto meetingServiceEvent = new MeetingServiceEvent(); // Create a new meeting service event
    meetingServiceEvent->setOnMeetingJoin(onJoin); // Set event callback for meeting join

    err = m_meetingService->SetEvent(meetingServiceEvent); // Set the event for meeting service
    if (hasError(err)) return err; // Return error if setting event fails

    return CreateAuthService(&m_authService); // Create authentication service
}

// Authenticate with the Zoom SDK
SDKError Zoom::auth() {
    SDKError err{SDKERR_UNINITIALIZE}; // Initialize error status

    auto id = m_config.clientId(); // Get client ID from configuration
    auto secret = m_config.clientSecret(); // Get client secret from configuration

    if (id.empty()) {
        Log::error("Client ID cannot be blank"); // Log error if client ID is empty
        return err; // Return uninitialized error
    }

    if (secret.empty()) {
        Log::error("Client Secret cannot be blank"); // Log error if client secret is empty
        return err; // Return uninitialized error
    }

    err = m_authService->SetEvent(new AuthServiceEvent(onAuth)); // Set authentication event
    if (hasError(err)) return err; // Return error if setting event fails

    generateJWT(m_config.clientId(), m_config.clientSecret()); // Generate JWT token

    AuthContext ctx; // Create authentication context
    ctx.jwt_token =  m_jwt.c_str(); // Set JWT token in context

    return m_authService->SDKAuth(ctx); // Perform SDK authentication
}

// Generate a JWT token for authentication
void Zoom::generateJWT(const string& key, const string& secret) {
    m_iat = std::chrono::system_clock::now(); // Set issued at time
    m_exp = m_iat + std::chrono::hours{24}; // Set expiration time (24 hours)

    // Create JWT token with claims
    m_jwt = jwt::create()
            .set_type("JWT")
            .set_issued_at(m_iat)
            .set_expires_at(m_exp)
            .set_payload_claim("appKey", claim(key))
            .set_payload_claim("tokenExp", claim(m_exp))
            .sign(algorithm::hs256{secret}); // Sign the token with secret
}

// Join a Zoom meeting
SDKError Zoom::join() {
    SDKError err{SDKERR_UNINITIALIZE}; // Initialize error status

    auto mid = m_config.meetingId(); // Get meeting ID from configuration
    auto password = m_config.password(); // Get meeting password from configuration
    auto displayName = m_config.displayName(); // Get display name from configuration

    if (mid.empty()) {
        Log::error("Meeting ID cannot be blank"); // Log error if meeting ID is empty
        return err; // Return uninitialized error
    }

    if (password.empty()) {
        Log ::error("Meeting Password cannot be blank"); // Log error if meeting password is empty
        return err; // Return uninitialized error
    }

    if (displayName.empty()) {
        Log::error("Display Name cannot be blank"); // Log error if display name is empty
        return err; // Return uninitialized error
    }

    auto meetingNumber = stoull(mid); // Convert meeting ID to unsigned long long
    auto userName = displayName.c_str(); // Get C-style string for display name
    auto psw = password.c_str(); // Get C-style string for password

    JoinParam joinParam; // Structure to hold join parameters
    joinParam.userType = ZOOM_SDK_NAMESPACE::SDK_UT_WITHOUT_LOGIN; // Set user type for joining

    JoinParam4WithoutLogin& param = joinParam.param.withoutloginuserJoin; // Access parameters for joining without login

    param.meetingNumber = meetingNumber; // Set meeting number
    param.userName = userName; // Set user name
    param.psw = psw; // Set password
    param.vanityID = nullptr; // No vanity ID
    param.customer_key = nullptr; // No customer key
    param.webinarToken = nullptr; // No webinar token
    param.isVideoOff = false; // Video is on
    param.isAudioOff = false; // Audio is on

    if (!m_config.zak().empty()) {
        Log::success("used ZAK token"); // Log success if ZAK token is used
        param.userZAK = m_config.zak().c_str(); // Set ZAK token
    }

    if (!m_config.joinToken().empty()) {
        Log::success("used App Privilege token"); // Log success if App Privilege token is used
        param.app_privilege_token = m_config.joinToken().c_str(); // Set App Privilege token
    }

    if (m_config.useRawAudio()) { // Check if raw audio is enabled
        auto* audioSettings = m_settingService->GetAudioSettings(); // Get audio settings
        if (!audioSettings) return SDKERR_INTERNAL_ERROR; // Return error if audio settings are null

        audioSettings->EnableAutoJoinAudio(true); // Enable auto join audio
    }

    return m_meetingService->Join(joinParam); // Join the meeting with parameters
}

// Start a Zoom meeting
SDKError Zoom::start() {
    SDKError err; // Initialize error status

    StartParam startParam; // Structure to hold start parameters
    startParam.userType = SDK_UT_NORMALUSER; // Set user type for starting

    StartParam4NormalUser  normalUser ; // Structure for normal user start parameters
    normalUser .vanityID = nullptr; // No vanity ID
    normalUser .customer_key = nullptr; // No customer key
    normalUser .isAudioOff = false; // Audio is on
    normalUser .isVideoOff = false; // Video is on

    err = m_meetingService->Start(startParam); // Start the meeting
    hasError(err, "start meeting"); // Check for errors during start

    return err; // Return error status
}

// Leave a Zoom meeting
SDKError Zoom::leave() {
    if (!m_meetingService) 
        return SDKERR_UNINITIALIZE; // Return uninitialized error if meeting service is null

    auto status = m_meetingService->GetMeetingStatus(); // Get current meeting status
    if (status == MEETING_STATUS_IDLE)
        return SDKERR_WRONG_USAGE; // Return wrong usage error if meeting is idle

    return m_meetingService->Leave(LEAVE_MEETING); // Leave the meeting
}

// Clean up resources used by the Zoom SDK
SDKError Zoom::clean() {
    if (m_meetingService)
        DestroyMeetingService(m_meetingService); // Destroy meeting service

    if (m_settingService)
        DestroySettingService(m_settingService); // Destroy settings service

    if (m_authService)
        DestroyAuthService(m_authService); // Destroy authentication service

    if (m_audioHelper)
        m_audioHelper->unSubscribe(); // Unsubscribe audio helper

    if (m_videoHelper)
        m_videoHelper->unSubscribe(); // Unsubscribe video helper

    delete m_renderDelegate; // Delete render delegate
    return CleanUPSDK(); // Clean up SDK resources
}

// Start raw recording of a Zoom meeting
SDKError Zoom::startRawRecording() {
    auto recCtl = m_meetingService->GetMeetingRecordingController(); // Get recording controller

    SDKError err = recCtl->CanStartRawRecording(); // Check if raw recording can start

    if (hasError(err)) {
        Log::info("requesting local recording privilege"); // Log request for local recording privilege
        return recCtl->RequestLocalRecordingPrivilege(); // Request local recording privilege
    }

    err = recCtl->StartRawRecording(); // Start raw recording
    if (hasError(err, "start raw recording")) // Check for errors during raw recording start
        return err; // Return error status

    if (m_config.useRawVideo()) { // Check if raw video is enabled
        if (!m_renderDelegate) {
            m_renderDelegate = new ZoomSDKRendererDelegate(); // Create a new render delegate
            m_videoSource = new ZoomSDKVideoSource(); // Create a new video source
        }

        err = createRenderer(&m_videoHelper, m_renderDelegate); // Create video renderer
        if (hasError(err, "create raw video renderer")) // Check for errors during renderer creation
            return err; // Return error status

        m_renderDelegate->setDir(m_config.videoDir()); // Set directory for video files
        m_renderDelegate->setFilename(m_config.videoFile()); // Set filename for video files
        
        auto participantCtl = m_meetingService->GetMeetingParticipantsController(); // Get participants controller
        auto uid = participantCtl->GetParticipantsList()->GetItem(0); // Get the first participant's UID

        m_videoHelper->setRawDataResolution(ZoomSDKResolution_720P); // Set video resolution
        err = m_videoHelper->subscribe(uid, RAW_DATA_TYPE_VIDEO); // Subscribe to raw video data
        if (hasError(err, "subscribe to raw video")) // Check for errors during subscription
            return err; // Return error status
    }

    if (m_config.useRawAudio()) { // Check if raw audio is enabled
        m_audioHelper = GetAudioRawdataHelper(); // Get audio raw data helper
        if (!m_audioHelper)
            return SDKERR_UNINITIALIZE; // Return uninitialized error if audio helper is null

        if (!m_audioSource) {
            auto mixedAudio = !m_config.separateParticipantAudio(); // Determine if audio should be mixed
            auto transcribe = m_config.transcribe(); // Get transcription setting

            m_audioSource = new ZoomSDKAudioRawDataDelegate(mixedAudio, transcribe); // Create audio raw data delegate
            m_audioSource->setDir(m_config.audioDir()); // Set directory for audio files
            m_audioSource->setFilename(m_config.audioFile()); // Set filename for audio files
        }

        err = m_audioHelper->subscribe(m_audioSource); // Subscribe to raw audio data
        if (hasError(err, "subscribe to raw audio")) // Check for errors during subscription
            return err; // Return error status
    }

    return SDKERR_SUCCESS; // Return success status
}

// Stop raw recording of a Zoom meeting
SDKError Zoom::stopRawRecording() {
    auto recCtrl = m_meetingService->GetMeetingRecordingController(); // Get recording controller
    auto err = recCtrl->StopRawRecording(); // Stop raw recording
    hasError(err, "stop raw recording"); // Check for errors during stop

    return err; // Return error status
}

// Check if the meeting has started
bool Zoom::isMeetingStart() {
    return m_config.isMeetingStart(); // Return meeting start status
}

// Check for errors and log messages accordingly
bool Zoom::hasError(const SDKError e, const string& action) {
    auto isError = e != SDKERR_SUCCESS; // Determine if there is an error

    if(!action.empty()) {
        if (isError) {
            stringstream ss;
            ss << "failed to " << action << " with status " << e; // Log error message
            Log::error(ss.str()); // Log error
        } else {
            Log::success(action); // Log success message
        }
    }
    return isError; // Return error status
}