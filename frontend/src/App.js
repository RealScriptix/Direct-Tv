import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorldMap = ({ onRegionSelect, selectedRegion }) => {
  const regions = [
    { id: 'north_america', name: 'North America', x: 150, y: 180, channels: 0 },
    { id: 'europe', name: 'Europe', x: 450, y: 150, channels: 0 },
    { id: 'asia', name: 'Asia', x: 600, y: 200, channels: 0 },
    { id: 'oceania', name: 'Oceania', x: 650, y: 350, channels: 0 },
    { id: 'africa', name: 'Africa', x: 450, y: 280, channels: 0 },
    { id: 'south_america', name: 'South America', x: 250, y: 350, channels: 0 }
  ];

  const [regionData, setRegionData] = useState(regions);

  useEffect(() => {
    const fetchRegionData = async () => {
      try {
        const response = await axios.get(`${API}/regions`);
        const updatedRegions = regions.map(region => {
          const data = response.data.find(r => r.region === region.id);
          return { ...region, channels: data ? data.channel_count : 0 };
        });
        setRegionData(updatedRegions);
      } catch (error) {
        console.error('Error fetching region data:', error);
      }
    };

    fetchRegionData();
  }, []);

  return (
    <div className="relative bg-gradient-to-b from-blue-900 to-blue-600 rounded-xl p-8">
      <div className="absolute inset-0 opacity-20 rounded-xl"
           style={{
             backgroundImage: `url('https://images.unsplash.com/photo-1713098965471-d324f294a71d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG1hcHxlbnwwfHx8Ymx1ZXwxNzUzMTEzMDcxfDA&ixlib=rb-4.1.0&q=85')`,
             backgroundSize: 'cover',
             backgroundPosition: 'center'
           }}>
      </div>
      
      <h2 className="text-3xl font-bold text-white text-center mb-8 relative z-10">
        Global TV Network Coverage
      </h2>
      
      <div className="relative w-full h-96 flex items-center justify-center z-10">
        <svg viewBox="0 0 800 400" className="w-full h-full">
          {regionData.map((region) => (
            <g key={region.id}>
              <circle
                cx={region.x}
                cy={region.y}
                r="25"
                fill={selectedRegion === region.id ? "#FFD700" : "#10B981"}
                stroke={selectedRegion === region.id ? "#FFA500" : "#059669"}
                strokeWidth="3"
                className="cursor-pointer hover:fill-yellow-400 transition-colors duration-200"
                onClick={() => onRegionSelect(region.id)}
              />
              <text
                x={region.x}
                y={region.y + 5}
                textAnchor="middle"
                className="fill-white text-xs font-bold pointer-events-none select-none"
              >
                {region.channels}
              </text>
              <text
                x={region.x}
                y={region.y + 45}
                textAnchor="middle"
                className="fill-white text-sm font-semibold pointer-events-none select-none"
              >
                {region.name}
              </text>
            </g>
          ))}
        </svg>
      </div>
      
      <div className="text-center text-white text-sm mt-4 relative z-10">
        Click on regions to view available channels • Numbers show channel count
      </div>
    </div>
  );
};

const ChannelGrid = ({ channels, liveGuide, onChannelSelect, selectedChannel }) => {
  const formatTime = (dateString) => {
    if (!dateString) return '--:--';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-red-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getProgramTypeColor = (type) => {
    const colors = {
      news: 'bg-red-600',
      sports: 'bg-green-600',
      movie: 'bg-purple-600',
      series: 'bg-blue-600',
      documentary: 'bg-yellow-600',
      entertainment: 'bg-pink-600',
      music: 'bg-indigo-600',
      kids: 'bg-orange-600'
    };
    return colors[type] || 'bg-gray-600';
  };

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full mr-3 animate-pulse"></div>
          Live TV Guide
        </h2>
        <div className="text-green-400 text-sm font-mono">
          {new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: true 
          })}
        </div>
      </div>

      <div className="grid gap-3 max-h-96 overflow-y-auto custom-scrollbar">
        {liveGuide.map((show) => (
          <div
            key={show.channel.id}
            className={`bg-gray-800 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedChannel === show.channel.id 
                ? 'ring-2 ring-blue-500 bg-gray-700' 
                : 'hover:bg-gray-700'
            }`}
            onClick={() => onChannelSelect(show.channel.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <div className="text-xl font-bold text-white">
                    {show.channel.channel_number}
                  </div>
                  <div className="text-xs text-gray-400">CH</div>
                </div>
                
                <div className="flex-1">
                  <div className="text-white font-semibold text-sm">
                    {show.channel.name}
                  </div>
                  <div className="text-gray-400 text-xs">
                    {show.channel.description}
                  </div>
                </div>
              </div>

              <div className="text-right flex-shrink-0">
                {show.current_program ? (
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded text-xs text-white ${getProgramTypeColor(show.current_program.type)}`}>
                        {show.current_program.type.toUpperCase()}
                      </span>
                      <div className="text-green-400 text-xs font-mono">
                        LIVE
                      </div>
                    </div>
                    <div className="text-white text-sm font-medium mt-1">
                      {show.current_program.title}
                    </div>
                    <div className="text-gray-400 text-xs mt-1">
                      {formatTime(show.current_start_time)} - {formatTime(show.current_end_time)}
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="flex-1 bg-gray-600 rounded-full h-1">
                        <div 
                          className={`h-1 rounded-full transition-all duration-300 ${getProgressColor(show.progress_percentage)}`}
                          style={{ width: `${show.progress_percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-400">
                        {show.time_remaining_minutes}m left
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">
                    No current program
                  </div>
                )}
              </div>
            </div>
            
            {show.next_program && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-gray-400 text-xs">Next: </span>
                    <span className="text-white text-sm">{show.next_program.title}</span>
                  </div>
                  <div className="text-gray-400 text-xs">
                    {formatTime(show.next_start_time)}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const ChannelDetails = ({ channel, schedule, onBack }) => {
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric'
    });
  };

  const getProgramTypeColor = (type) => {
    const colors = {
      news: 'bg-red-600',
      sports: 'bg-green-600',
      movie: 'bg-purple-600',
      series: 'bg-blue-600',
      documentary: 'bg-yellow-600',
      entertainment: 'bg-pink-600',
      music: 'bg-indigo-600',
      kids: 'bg-orange-600'
    };
    return colors[type] || 'bg-gray-600';
  };

  const groupScheduleByDate = (schedule) => {
    const groups = {};
    schedule.forEach(item => {
      const date = new Date(item.start_time).toDateString();
      if (!groups[date]) groups[date] = [];
      groups[date].push(item);
    });
    return groups;
  };

  const scheduleGroups = groupScheduleByDate(schedule);

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
          >
            ← Back
          </button>
          <div>
            <h2 className="text-2xl font-bold text-white">
              Channel {channel.channel_number} - {channel.name}
            </h2>
            <p className="text-gray-400">{channel.description}</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm text-gray-400">Region</div>
          <div className="text-white capitalize">{channel.region.replace('_', ' ')}</div>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto custom-scrollbar">
        {Object.entries(scheduleGroups).map(([date, programs]) => (
          <div key={date} className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3 sticky top-0 bg-gray-900 py-2">
              {formatDate(programs[0].start_time)}
            </h3>
            
            <div className="space-y-2">
              {programs.map((item) => (
                <div key={item.id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-sm font-mono text-blue-400">
                          {formatTime(item.start_time)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {item.program.duration_minutes}m
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded text-xs text-white ${getProgramTypeColor(item.program.type)}`}>
                            {item.program.type.toUpperCase()}
                          </span>
                          <h4 className="text-white font-semibold">
                            {item.program.title}
                          </h4>
                        </div>
                        
                        <p className="text-gray-400 text-sm mt-1">
                          {item.program.description}
                        </p>
                        
                        {item.program.genre && (
                          <div className="text-gray-500 text-xs mt-1">
                            Genre: {item.program.genre}
                          </div>
                        )}
                        
                        {item.program.episode_number && (
                          <div className="text-gray-500 text-xs">
                            Season {item.program.season_number}, Episode {item.program.episode_number}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      {item.program.rating && (
                        <div className="bg-gray-700 text-white text-xs px-2 py-1 rounded">
                          {item.program.rating}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [channels, setChannels] = useState([]);
  const [liveGuide, setLiveGuide] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [channelSchedule, setChannelSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('map'); // 'map', 'channels', 'channel-detail'

  // Initialize data on app start
  useEffect(() => {
    const initializeData = async () => {
      try {
        await axios.post(`${API}/init-data`);
        console.log('Sample data initialized');
      } catch (error) {
        console.error('Error initializing data:', error);
      }
    };

    initializeData();
  }, []);

  // Auto-refresh live guide every 30 seconds
  useEffect(() => {
    if (view === 'channels' && selectedRegion) {
      const interval = setInterval(fetchLiveGuide, 30000);
      return () => clearInterval(interval);
    }
  }, [view, selectedRegion]);

  const fetchChannels = async (region) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/channels?region=${region}`);
      setChannels(response.data);
    } catch (error) {
      console.error('Error fetching channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLiveGuide = async () => {
    if (!selectedRegion) return;
    
    try {
      const response = await axios.get(`${API}/live-guide?region=${selectedRegion}`);
      setLiveGuide(response.data);
    } catch (error) {
      console.error('Error fetching live guide:', error);
    }
  };

  const fetchChannelSchedule = async (channelId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/schedule/${channelId}?hours=48`);
      setChannelSchedule(response.data);
    } catch (error) {
      console.error('Error fetching channel schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegionSelect = async (region) => {
    setSelectedRegion(region);
    await fetchChannels(region);
    await fetchLiveGuide();
    setView('channels');
  };

  const handleChannelSelect = async (channelId) => {
    setSelectedChannel(channelId);
    await fetchChannelSchedule(channelId);
    setView('channel-detail');
  };

  const handleBackToChannels = () => {
    setSelectedChannel(null);
    setView('channels');
  };

  const handleBackToMap = () => {
    setSelectedRegion(null);
    setView('map');
  };

  const getSelectedChannelData = () => {
    return channels.find(ch => ch.id === selectedChannel);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-4 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <div className="text-white text-xl font-bold">📺</div>
            </div>
            <h1 className="text-4xl font-bold text-white">
              Global TV Station Network
            </h1>
          </div>
          <p className="text-gray-300 text-lg">
            Live broadcasting worldwide • Real-time programming guide
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-3"></div>
              Loading...
            </div>
          </div>
        )}

        {/* Navigation Breadcrumbs */}
        {view !== 'map' && (
          <div className="mb-6">
            <nav className="flex items-center space-x-2 text-sm">
              <button
                onClick={handleBackToMap}
                className="text-blue-400 hover:text-blue-300 transition-colors duration-200"
              >
                🌍 World Map
              </button>
              {selectedRegion && (
                <>
                  <span className="text-gray-500">→</span>
                  <span className="text-white capitalize">
                    {selectedRegion.replace('_', ' ')}
                  </span>
                </>
              )}
              {selectedChannel && (
                <>
                  <span className="text-gray-500">→</span>
                  <span className="text-white">
                    {getSelectedChannelData()?.name || 'Channel Details'}
                  </span>
                </>
              )}
            </nav>
          </div>
        )}

        {/* Main Content */}
        {view === 'map' && (
          <WorldMap
            onRegionSelect={handleRegionSelect}
            selectedRegion={selectedRegion}
          />
        )}

        {view === 'channels' && (
          <ChannelGrid
            channels={channels}
            liveGuide={liveGuide}
            onChannelSelect={handleChannelSelect}
            selectedChannel={selectedChannel}
          />
        )}

        {view === 'channel-detail' && getSelectedChannelData() && (
          <ChannelDetails
            channel={getSelectedChannelData()}
            schedule={channelSchedule}
            onBack={handleBackToChannels}
          />
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Global TV Network • Broadcasting live 24/7 across all time zones</p>
          <div className="mt-2 flex items-center justify-center space-x-4">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live System Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;