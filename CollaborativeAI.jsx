import React, { useState, useEffect, useCallback } from 'react';

const CollaborativeAI = () => {
  const [projectIdea, setProjectIdea] = useState('');
  const [activeAgents, setActiveAgents] = useState(new Set());
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [outputStream, setOutputStream] = useState([
    { message: '🧠 Collaborative AI System initialized', type: 'system', timestamp: new Date() },
    { message: '📡 All agents connected and ready', type: 'success', timestamp: new Date() }
  ]);

  const agents = [
    { id: 'background', name: 'Background Agent', description: 'Literature review and problem framing', color: '#10b981' },
    { id: 'technical', name: 'Technical Agent', description: 'System architecture and innovation design', color: '#f59e0b' },
    { id: 'market', name: 'Market Agent', description: 'Market research and application analysis', color: '#ef4444' },
    { id: 'budget', name: 'Budget Agent', description: 'Resource estimation and funding breakdown', color: '#8b5cf6' },
    { id: 'planner', name: 'Planner Agent', description: 'Work plan, milestones, and timeline', color: '#06b6d4' },
    { id: 'impact', name: 'Impact Agent', description: 'Academic, industrial, and social impact', color: '#f97316' },
    { id: 'pi', name: 'PI Agent', description: 'Principal Investigator - Final integration', color: '#0ea5e9' }
  ];

  const addToStream = useCallback((message, type = 'info') => {
    setOutputStream(prev => [...prev.slice(-19), {
      message,
      type,
      timestamp: new Date()
    }]);
  }, []);

  const selectAgent = (agentId) => {
    setActiveAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
    addToStream(`Selected ${agentId} agent`, 'info');
  };

  const generateReport = async () => {
    if (isGenerating || !projectIdea.trim()) {
      if (!projectIdea.trim()) {
        addToStream('Error: Please enter a project idea', 'error');
      }
      return;
    }

    setIsGenerating(true);
    addToStream('🚀 Starting collaborative report generation...', 'system');

    // Simulate agent collaboration sequence
    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];
      setCurrentAgent(agent.id);
      
      addToStream(`🔄 ${agent.name} processing...`, 'processing');
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 2000));
      
      addToStream(`✅ ${agent.name} completed analysis`, 'success');
      
      if (i < agents.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 800));
      }
    }

    setCurrentAgent(null);
    addToStream('✅ Collaborative report generation complete!', 'success');
    setIsGenerating(false);
  };

  const getTypeColor = (type) => {
    const colors = {
      system: '#0ea5e9',
      processing: '#f59e0b',
      success: '#10b981',
      error: '#ef4444',
      info: '#64748b'
    };
    return colors[type] || colors.info;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-200">
      <div className="grid grid-cols-12 h-screen">
        {/* Agent Network Panel */}
        <div className="col-span-3 bg-slate-800/60 backdrop-blur-sm border-r border-slate-600 p-5 overflow-y-auto">
          <div className="text-center mb-8">
            <h1 className="text-lg font-black text-sky-400 font-mono tracking-wider animate-pulse">
              🧠 COLLABORATIVE AI
            </h1>
          </div>

          <div className="space-y-3">
            {agents.map(agent => (
              <div
                key={agent.id}
                onClick={() => selectAgent(agent.id)}
                className={`
                  relative p-4 rounded-xl cursor-pointer transition-all duration-300 border
                  ${activeAgents.has(agent.id) 
                    ? 'border-sky-400 bg-sky-400/10 shadow-lg shadow-sky-400/20' 
                    : 'border-slate-600 bg-slate-900/60 hover:border-slate-500'
                  }
                  ${currentAgent === agent.id ? 'animate-pulse' : ''}
                `}
                style={{
                  boxShadow: activeAgents.has(agent.id) 
                    ? `0 0 20px ${agent.color}30` 
                    : 'none'
                }}
              >
                {currentAgent === agent.id && (
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>
                )}
                
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm" style={{ color: agent.color }}>
                    {agent.name}
                  </span>
                  <div 
                    className={`w-2 h-2 rounded-full ${currentAgent === agent.id ? 'animate-spin' : 'animate-pulse'}`}
                    style={{ backgroundColor: agent.color }}
                  ></div>
                </div>
                
                <p className="text-xs text-slate-400 leading-relaxed">
                  {agent.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Main Workspace */}
        <div className="col-span-6 p-5 overflow-y-auto bg-slate-900/30">
          {/* Command Center */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-6 mb-6 border border-slate-600">
            <textarea
              value={projectIdea}
              onChange={(e) => setProjectIdea(e.target.value)}
              placeholder="Enter your R&D project idea...&#10;&#10;Example: 'AI-enabled Modular Robot Adaptor for Industry 4.0 Applications'"
              className="w-full bg-slate-900/80 border-2 border-slate-600 rounded-xl p-4 text-cyan-300 font-mono text-sm resize-none min-h-24 focus:outline-none focus:border-sky-400 focus:shadow-lg focus:shadow-sky-400/20 transition-all"
            />
            
            <button
              onClick={generateReport}
              disabled={isGenerating}
              className="mt-4 px-8 py-4 bg-gradient-to-r from-sky-500 to-cyan-500 rounded-xl text-white font-semibold text-lg hover:from-sky-400 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-lg hover:shadow-sky-400/30 hover:-translate-y-1 active:translate-y-0"
            >
              🚀 Generate Collaborative Report
            </button>
          </div>

          {/* Collaboration Timeline */}
          <div className="bg-slate-800/40 rounded-xl p-5 mb-6">
            <h3 className="text-lg font-semibold text-sky-400 mb-4 flex items-center">
              🔄 Collaboration Timeline
            </h3>
            
            <div className="space-y-3">
              {agents.map((agent, index) => (
                <div
                  key={agent.id}
                  className={`flex items-center p-3 border-l-2 pl-4 ml-2 relative transition-all duration-300 ${
                    currentAgent === agent.id || activeAgents.has(agent.id)
                      ? 'border-l-sky-400'
                      : 'border-l-slate-600'
                  }`}
                >
                  <div
                    className={`absolute -left-1.5 w-3 h-3 rounded-full transition-all duration-300 ${
                      currentAgent === agent.id || activeAgents.has(agent.id)
                        ? 'shadow-lg'
                        : ''
                    }`}
                    style={{
                      backgroundColor: currentAgent === agent.id || activeAgents.has(agent.id) 
                        ? agent.color 
                        : '#64748b',
                      boxShadow: currentAgent === agent.id || activeAgents.has(agent.id)
                        ? `0 0 10px ${agent.color}`
                        : 'none'
                    }}
                  ></div>
                  
                  <span className="text-sm text-slate-300">
                    {agent.description}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Output Stream */}
          <div className="bg-slate-900/60 rounded-xl p-5 font-mono text-sm max-h-80 overflow-y-auto">
            {outputStream.map((entry, index) => (
              <div
                key={index}
                className="mb-1 leading-relaxed"
                style={{ color: getTypeColor(entry.type) }}
              >
                [{entry.timestamp.toLocaleTimeString()}] {entry.message}
              </div>
            ))}
          </div>
        </div>

        {/* Report Viewer */}
        <div className="col-span-3 bg-slate-800/60 backdrop-blur-sm border-l border-slate-600 p-5 overflow-y-auto">
          <h3 className="text-lg font-semibold text-sky-400 mb-5 text-center">
            📄 Report Viewer
          </h3>
          
          <div className="bg-slate-900/80 border border-slate-600 rounded-xl h-96 mb-5 flex items-center justify-center text-slate-500">
            <div className="text-center">
              <div className="text-4xl mb-2">📄</div>
              <div>Document preview will appear here</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {['📄 Export DOCX', '📋 Copy Link', '📊 Analytics', '🔄 Regenerate'].map((label, index) => (
              <button
                key={index}
                className="px-3 py-2 bg-purple-500/20 border border-purple-500 rounded-lg text-purple-400 text-xs hover:bg-purple-500/30 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-200"
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
};

export default CollaborativeAI;