#include "Config.h"

// Constructor for the Config class
Config::Config() :
        m_app(m_name, "zoomsdk"), // Initialize the application with name and description
        m_rawRecordAudioCmd(m_app.add_subcommand("RawAudio", "Enable Audio Raw Recording")), // Subcommand for raw audio recording
        m_rawRecordVideoCmd(m_app.add_subcommand("RawVideo", "Enable Video Raw Recording")) // Subcommand for raw video recording
{
    // Set the configuration file for the application
    m_app.set_config("--config", "config.toml");

    // Add options for meeting parameters
    m_app.add_option("-m, --meeting-id", m_meetingId, "Meeting ID of the meeting"); // Meeting ID
    m_app.add_option("-p, --password", m_password, "Password of the meeting"); // Meeting password
    m_app.add_option("-n, --display-name", m_displayName, "Display Name for the meeting")->capture_default_str(); // Display name with default capture

    // Add options for Zoom API tokens and URLs
    m_app.add_option("-z,--zak", m_zak, "ZAK Token to join the meeting"); // ZAK Token
    m_app.add_option("--host", m_zoomHost, "Host Domain for the Zoom Meeting")->capture_default_str(); // Zoom host domain
    m_app.add_option("-u, --join-url", m_joinUrl, "Join or Start a Meeting URL"); // Join URL for the meeting
    m_app.add_option("-t, --join-token", m_joinToken, "Join the meeting with App Privilege using a token"); // Join token for app privilege

    // Add options for client credentials
    m_app.add_option("--client-id", m_clientId, "Zoom Meeting Client ID")->required(); // Client ID (required)
    m_app.add_option("--client-secret", m_clientSecret, "Zoom Meeting Client Secret")->required(); // Client Secret (required)

    // Add flag to indicate if the meeting should be started
    m_app.add_flag("-s, --start", m_isMeetingStart, "Start a Zoom Meeting");

    // Add options for raw audio recording parameters
    m_rawRecordAudioCmd->add_option("-f, --file", m_audioFile, "Output PCM audio file")->required(); // Output audio file (required)
    m_rawRecordAudioCmd->add_option("-d, --dir", m_audioDir, "Audio Output Directory"); // Output directory for audio
    m_rawRecordAudioCmd->add_option("--sock-file", m_sockFile, "Unix Socket File name"); // Output audio file (required)
    m_rawRecordAudioCmd->add_option("--sock-dir", m_sockDir, "Unix Socket Directory"); // Output directory for audio
    m_rawRecordAudioCmd->add_flag("-s, --separate-participants", m_separateParticipantAudio, "Output to separate PCM files for each participant"); // Flag to separate audio files
    m_rawRecordAudioCmd->add_flag("-t, --transcribe", m_transcribe, "Transcribe audio to text"); // Flag to enable transcription

    // Add options for raw video recording parameters
    m_rawRecordVideoCmd->add_option("-f, --file", m_videoFile, "Output YUV video file")->required(); // Output video file (required)
    m_rawRecordVideoCmd->add_option("-d, --dir", m_videoDir, "Video Output Directory"); // Output directory for video
}

// Method to read command line arguments and configure the application
int Config::read(int ac, char **av) {
    try {
        m_app.parse(ac, av); // Parse the command line arguments
    } catch(const CLI::CallForHelp &e) {
        exit(m_app.exit(e)); // Exit if help is requested
    } catch (const CLI::ParseError& err) {
        return m_app.exit(err); // Return error if parsing fails
    } 

    // If a join URL is provided, parse it
    if (!m_joinUrl.empty())
        parseUrl(m_joinUrl);

    return 0; // Return success
}

// Method to parse the join URL and extract meeting information
bool Config::parseUrl(const string& join_url) {
    auto url = ada::parse<ada::url>(join_url); // Parse the URL

    // Check if URL parsing was successful
    if (!url) {
        cerr << "unable to parse join URL" << endl; // Log error if parsing fails
        return false; // Return failure
    }

    string token, lastRoute; // Initialize token and last route variables
    istringstream ss(static_cast<string>(url->get_pathname())); // Stream for pathname

    // Extract tokens from the pathname
    while (getline(ss, token, '/')) {
        if(token.empty()) continue; // Skip empty tokens

        m_isMeetingStart = token == "s"; // Set meeting start flag

        // If the last route was "j" or "s", set the meeting ID
        if (lastRoute == "j" || lastRoute == "s") {
            m_meetingId = token; // Assign the token as the meeting ID
            break; // Exit the loop after finding the meeting ID
        }

        lastRoute = token; // Update the last route
    }

    // Check if the meeting ID was found
    if (m_meetingId.empty()) return false; // Return failure if no meeting ID

    ada::url_search_params search(url->get_search()); // Parse the search parameters from the URL
    if (!search.has("pwd")) 
        return false; // Return failure if password is not present

    m_password = move(*search.get(string_view("pwd"))); // Move the password into the member variable

    return true; // Return success
}

// Getter for the client ID
const string& Config::clientId() const {
    return m_clientId; // Return the client ID
}

// Getter for the client secret
const string& Config::clientSecret() const {
    return m_clientSecret; // Return the client secret
}

// Getter for the ZAK token
const string &Config::zak() const {
    return m_zak; // Return the ZAK token
}

// Check if raw recording is enabled (audio or video)
bool Config::useRawRecording() const {
    return useRawAudio() || useRawVideo(); // Return true if either audio or video raw recording is enabled
}

// Check if raw audio recording is enabled
bool Config::useRawAudio() const {
    return !m_audioFile.empty() || m_separateParticipantAudio || m_transcribe; // Return true if audio file is set or other audio options are enabled
}

// Check if raw video recording is enabled
bool Config::useRawVideo() const {
    return !m_videoFile.empty(); // Return true if video file is set
}

// Check if transcription is enabled
bool Config::transcribe() const {
    return m_transcribe; // Return the transcription flag
}

// Getter for the audio output directory
const string& Config::audioDir() const {
    return m_audioDir; // Return the audio output directory
}

// Getter for the audio output file
const string& Config::audioFile() const {
    return m_audioFile; // Return the audio output file
}

// Getter for the socket output directory
const string& Config::socketDir() const {
    return m_sockDir; // Return the audio output directory
}

// Getter for the socket output file
const string& Config::socketFile() const {
    return m_sockFile; // Return the audio output file
}

// Getter for the video output directory
const string& Config::videoDir() const {
    return m_videoDir; // Return the video output directory
}

// Getter for the video output file
const string& Config::videoFile() const {
    return m_videoFile; // Return the video output file
}

// Check if separate audio files for participants are enabled
bool Config::separateParticipantAudio() const {
    return m_separateParticipantAudio; // Return the flag for separate participant audio
}

// Check if the meeting is set to start
bool Config::isMeetingStart() const {
    return m_isMeetingStart; // Return the meeting start flag
}

// Getter for the join token
const string& Config::joinToken() const {
    return m_joinToken; // Return the join token
}

// Getter for the meeting ID
const string& Config::meetingId() const {
    return m_meetingId; // Return the meeting ID
}

// Getter for the meeting password
const string& Config::password() const {
    return m_password; // Return the meeting password
}

// Getter for the display name
const string& Config::displayName() const {
    return m_displayName; // Return the display name
}

// Getter for the Zoom host domain
const string& Config::zoomHost() const {
    return m_zoomHost; // Return the Zoom host domain
}